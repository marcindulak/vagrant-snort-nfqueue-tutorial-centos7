# https://github.com/lest/prometheus-rpm
sudo su - -c "curl -s https://packagecloud.io/install/repositories/prometheus-rpm/release/script.rpm.sh | sed 's/yum install -y/yum install -d0 -e0 -y/' | bash"
sudo su - -c "yum -d 1 -e 0 -y install prometheus"
# configure prometheus to scrape node_exporter
sudo su - -c """sed -i '/The job name is added as a label/a\ \n  # Metrics from nodes using \"node_exporter\".\n  - job_name: \"node_exporter\"\n    metrics_path: \"/metrics\"\n    file_sd_configs:\n     \
 - files:\n        - /etc/prometheus/node_exporter.json\n' /etc/prometheus/prometheus.yml"""
sudo su - -c "systemctl enable prometheus"
sudo su - -c "systemctl start prometheus"
