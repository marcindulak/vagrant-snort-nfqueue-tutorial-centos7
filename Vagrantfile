# -*- mode: ruby -*-
# vi: set ft=ruby :

NETWORK = ENV.fetch('NETWORK', '192.168.17.')

hosts = {
  'attacker0' => {'hostname' => 'attacker0', 'ip' => NETWORK + '10', 'mac' => '080027001710'},
  'monitor0' => {'hostname' => 'monitor0', 'ip' => NETWORK + '20', 'mac' => '080027001720',
                 'prometheus_port' => {'guest' => 9090, 'host' => 9090}},
  'snort0' => {'hostname' => 'snort0', 'ip' => NETWORK + '30', 'mac' => '080027001730'},
}

Vagrant.configure(2) do |config|
  hosts.keys.sort.each do |host|
      config.vm.define hosts[host]['hostname'] do |machine|
        #machine.vm.box = 'centos/7'
        machine.vm.box = 'bento/centos-7.3'
        machine.vm.box_url = machine.vm.box
        #machine.vm.synced_folder '.', '/vagrant', disabled: true
        machine.vm.network 'private_network', ip: hosts[host]['ip'], mac: hosts[host]['mac']
        #if host.start_with?("monitor")
        #  machine.vm.network 'forwarded_port', guest: hosts[host]['prometheus_port']['guest'], host: hosts[host]['prometheus_port']['host']
        #end
        machine.vm.provider 'virtualbox' do |v|
          if host.start_with?("attacker")
            v.memory = 2048  # memory needed for tcpreplay caching
          else
            v.memory = 512
          end
          if host.start_with?("snort")
            v.cpus = 4  # cores used by snort's multithreading
          else
            v.cpus = 1
          end
          # disable VBox time synchronization and use ntp
          v.customize ['setextradata', :id, 'VBoxInternal/Devices/VMMDev/0/Config/GetHostTimeDisabled', 1]
        end
      end
  end
  # disable IPv6 on Linux
  $linux_disable_ipv6 = <<SCRIPT
sysctl -w net.ipv6.conf.default.disable_ipv6=1
sysctl -w net.ipv6.conf.all.disable_ipv6=1
sysctl -w net.ipv6.conf.lo.disable_ipv6=1
SCRIPT
  # setenforce 0
  $setenforce_0 = <<SCRIPT
if test `getenforce` = 'Enforcing'; then setenforce 0; fi
#sed -Ei 's/^SELINUX=.*/SELINUX=Permissive/' /etc/selinux/config
SCRIPT
  # stop firewalld
  $systemctl_stop_firewalld = <<SCRIPT
systemctl stop firewalld.service
SCRIPT
  # common settings on all machines
  $etc_hosts = <<SCRIPT
echo "$*" >> /etc/hosts
SCRIPT
  $epel7 = <<SCRIPT
yum -d 1 -e 0 -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
SCRIPT
  $snort_el = <<SCRIPT
cat <<'END' > /etc/yum.repos.d/copr-marcindulak-snort.repo
[copr-marcindulak-snort]
name=copr-marcindulak-snort
baseurl=https://copr-be.cloud.fedoraproject.org/results/marcindulak/snort/epel-$releasever-$basearch
enabled=1
gpgcheck=1
gpgkey=https://copr-be.cloud.fedoraproject.org/results/marcindulak/snort/pubkey.gpg
END
SCRIPT
  # https://github.com/lest/prometheus-rpm
  $prometheus_el = <<SCRIPT
curl -s https://packagecloud.io/install/repositories/prometheus-rpm/release/script.rpm.sh | sed 's/yum install -y/yum install -d0 -e0 -y/' | bash
SCRIPT
  hosts.keys.sort.each do |host|
    config.vm.define hosts[host]['hostname'] do |machine|
      machine.vm.provision :shell, :inline => 'hostname ' + hosts[host]['hostname'], run: 'always'
      machine.vm.provision :shell, :inline => 'echo ' + hosts[host]['hostname'] + ' > /etc/hostname'
      hosts.keys.sort.each do |k|
        machine.vm.provision 'shell' do |s|
          s.inline = $etc_hosts
          s.args   = [hosts[k]['ip'], hosts[k]['hostname']]
        end
      end
      machine.vm.provision :shell, :inline => $setenforce_0, run: 'always'
      machine.vm.provision :shell, :inline => $epel7
      if host.start_with?("snort")
        machine.vm.provision :shell, :inline => $snort_el
      end
      if host.start_with?("monitor") or host.start_with?("snort")
        machine.vm.provision :shell, :inline => $prometheus_el
      end
      machine.vm.provision :shell, :inline => $linux_disable_ipv6, run: 'always'
      # install and enable ntp
      machine.vm.provision :shell, :inline => 'yum -d 1 -e 0 -y install ntp'
      machine.vm.provision :shell, :inline => 'systemctl enable ntpd'
      machine.vm.provision :shell, :inline => 'systemctl start ntpd'
    end
  end
end
