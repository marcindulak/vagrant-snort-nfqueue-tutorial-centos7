# Description

An example of `snort++` (https://www.snort.org/snort3) network Intrusion Detection and Prevention System (ID/IPS) deployed on an endpoint Apache host.

In this setup the nfqueue (https://home.regit.org/netfilter-en/using-nfqueue-and-libnetfilter_queue/) iptables target is used to enable the intrusion prevention capability of snort, and the prometheus (https://prometheus.io/) time-series database is used for monitoring of snort alerts.

The setup combines Vagrant (https://www.vagrantup.com) with Jupyter (http://jupyter.org/) in order to
achieve a "reproducible", executable documentation in the spirit of https://en.wikipedia.org/wiki/Literate_programming

Please go to [vagrant-snort-nfqueue-tutorial-centos7.ipynb](ipynb/vagrant-snort-nfqueue-tutorial-centos7.ipynb)


# Dependencies

None


# License

BSD 2-clause


# Todo
