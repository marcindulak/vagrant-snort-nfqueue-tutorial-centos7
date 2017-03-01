import dateutil.parser
import json
import os
from pwd import getpwnam
import shutil
import tempfile
import time

from idstools import maps
from idstools.scripts.u2json import load_from_snort_conf
from idstools.scripts.u2json import Formatter
from idstools import unified2

import argparse
import warnings

warnings.filterwarnings("ignore")

def create_parser():
    parser = argparse.ArgumentParser(
        description='Write Snort alerts in Prometheus Textfile Collector format',
    )

    parser.add_argument("--directory", default='/var/log/snort',
                        help="Spool directory with unified2 logs: default /var/log/snort")
    parser.add_argument("--prefix", default='unified2.log',
                        help="Name (prefix) of the unified2 log file: default unified2.log")
    parser.add_argument("--output", default='/var/lib/prometheus/snort.prom', required=False, help="Full path to output file")
    parser.add_argument("--node_exporter_username", default='prometheus', required=False, help="node_exporter user name")
    parser.add_argument("--node_exporter_groupname", default='prometheus', required=False, help="node_exporter group name")
    parser.add_argument("--timestamp", default=False, action='store_true', help="Include timestamp in prometheus metrics")
    parser.add_argument("--threshold_seconds", default=20,
                        required=False, type=int, help="Spool to the output file every threshold_seconds, 20 by default")

    return parser

parser = create_parser()
args = parser.parse_args()

assert os.path.exists(args.directory), args.directory + ': no such file or directory'
assert os.path.exists(os.path.dirname(args.output)), os.path.dirname(args.output) + ': no such file or directory'

msgmap = maps.SignatureMap()
classmap = maps.ClassificationMap()
formatter = Formatter(msgmap=msgmap, classmap=classmap)

reader = unified2.SpoolRecordReader(directory=args.directory, prefix=args.prefix, follow=True, init_filename=None, init_offset=None)

labels = ['generator-id', 'signature-id', 'blocked', 'source-ip', 'dport-icode']

alert_count = {}
text_collector = {}
last_time = time.time()
for record in reader:
    formatted = dict(formatter.format(record))
    if not 'event' in formatted:
        continue
    event = formatted['event']
    #[('event', {'impact': 0, 'protocol': 6, 'classification': 'Misc Attack', 'dport-icode': 443, 'signature-revision': 8, 'classification-id': 30, 'signature-id': 10997, 'sensor-id': 0, 'impact-flag': 0, 'sport-itype': 60748, 'priority': 2, 'event-second': 1481294223, 'generator-id': 1, 'destination-ip': '10.255.2.160', 'event-id': 6, 'vlan-id': None, 'mpls-label': None, 'msg': 'SERVER-WEBAPP SSLv2 OpenSSl KEY_ARG buffer overflow attempt', 'source-ip': '10.255.2.200', 'event-microsecond': 885673, 'blocked': 0})]
    alert_id = 'snort' + ''.join(['_' + str(event[label]) for label in labels])
    alert_count[alert_id] = alert_count.get(alert_id, 0) + 1
    timestamp = int(float(event['event-second']) * 1000 + float(event['event-microsecond']) / 1000)
    entry = 'snort_alert_count{' + ','.join([key.replace('-', '_') + '=' '"' + str(value) + '"' for key, value in list((key, event[key]) for key in labels)]) + '} '
    if args.timestamp:
        text_collector.update({entry: str(alert_count[alert_id]) + ' ' + str(timestamp)})
    else:
        text_collector.update({entry: str(alert_count[alert_id])})
    if time.time() - last_time > int(args.threshold_seconds):
        with tempfile.NamedTemporaryFile(delete=True) as temp:
            temp.write('# HELP snort_alert_count Snort alert count.\n')
            temp.write('# TYPE snort_alert_count counter\n')
            for key in sorted(text_collector.keys()):
                temp.write(key + ' ' + text_collector[key] + '\n')
            temp.flush()
            shutil.copy2(temp.name, args.output)
            os.chown(args.output, getpwnam(args.node_exporter_username).pw_uid, getpwnam(args.node_exporter_groupname).pw_gid)
        last_time = time.time()
