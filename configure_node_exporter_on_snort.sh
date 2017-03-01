# https://github.com/lest/prometheus-rpm
sudo su - -c "curl -s https://packagecloud.io/install/repositories/prometheus-rpm/release/script.rpm.sh | sed 's/yum install -y/yum install -d0 -e0 -y/' | bash"
sudo su - -c "yum -d 1 -e 0 -y install node_exporter"
# configure node_exporter
sudo su - -c "echo NODE_EXPORTER_OPTS='-collector.textfile.directory=/var/lib/prometheus' >> /etc/default/node_exporter"
sudo su - -c "systemctl enable node_exporter"
sudo su - -c "systemctl start node_exporter"
