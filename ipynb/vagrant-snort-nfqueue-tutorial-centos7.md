
# Description

An example of `snort++` (https://www.snort.org/snort3) network Intrusion Detection and Prevention System (ID/IPS) deployed on an endpoint Apache host.

`snort` belongs to the class of rule-based network IDS/IPS systems. The `snort` rules work similarly to virus signatures:
like a virus scanner, `snort` can only detect a network traffic for which a rule is written in advance.

The instance of running `snort` software is called a sensor.
In order for `snort` to serve as an IPS the traffic must pass through the sensor.
`snort` then applies rules in order to block and/or log selected traffic.

`snort` IPS has been initially designed for sensor placing on a separate Linux machine, through which the traffic will pass
over a network bridge [https://openmaniak.com/inline_bridge.php](https://openmaniak.com/inline_bridge.php).

In order to place the sensor on an end-point host (the destination of the traffic,
or e.g. a load balancer) the recommended method is to send all traffic to be monitored
to `nfqueue` on this host and let `snort` apply rule based decisions to the packets present in `nfqueue`
[https://sourceforge.net/p/snort/mailman/message/35461638/](https://sourceforge.net/p/snort/mailman/message/35461638/)

In this setup the `nfqueue` (https://home.regit.org/netfilter-en/using-nfqueue-and-libnetfilter_queue/) `iptables` target is used to enable
the intrusion prevention capability of `snort`, and the `prometheus` (https://prometheus.io/) time-series database is used for monitoring of `snort` alerts.

`snort++` (or `snort3`), planned at least since 2005 (Snort Coockbook, p. 179) supports "multiple packet processing threads"
and several other parts of the code base have been rewritten compared to `snort2`. This setup uses `snort++`, though it is still *alpha*. After following the steps during this setup it is rather easy to switch to the more reliable `snort2`.

# Configuration overview

The private 192.168.17.0/24 network is associated with the Vagrant eth1 interfaces.
eth0 is used by Vagrant.  Vagrant reserves eth0 and this cannot be currently changed
(see https://github.com/mitchellh/vagrant/issues/2093).


                                                    -----------------
                                                    | monitor0      |
                                                    |               |
                                                    | prometheus    |
                                                    -----------------
                                                     |     |
                                                 eth1| eth0|
                                        192.168.17.20|     |
                 -----------------------------------------------------------------
                 |                                  Vagrant HOST                 |
                 -----------------------------------------------------------------
                  |     |                                         |     |         
              eth1| eth0|                                     eth1| eth0|         
     192.168.17.30|     |                            192.168.17.10|     |         
                 -----------------                               -----------------
                 | snort0        |                               | attacker0     |
                 |               |                               |               |
                 | snort         |                               -----------------
                 | node_exporter |
                 | apache        |
                 -----------------

Note that the target Apache host and the attacker machines reside on the same private network, while on the internet all addresses would be public.
This is in order to simplify routing, and it does no affect the `snort` configuration, i.e. a host configured like **snort0** would perform it's job if put on the internet.

`snort++` offers a multithreading mode. Note however that `snort`'s multithreading does not mean that a single `snort`
instance will internally load balance the traffic and process in multiple threads http://seclists.org/snort/2015/q2/90,
but instead multithreading means running multiple `snort` processes attached to different network interfaces, like one would do with `snort2` (is this statement correct?).
Obviously such multithreading configuration is not applicable to this setup.

# Sample Usage

Install VirtualBox https://www.virtualbox.org/ and Vagrant https://www.vagrantup.com/downloads.html

## Retrive the repository under the `jupyter` current working directory


```python
%%bash
pwd
```

    /scratch/ubuntu/jupyter



```python
%%bash
git clone https://github.com/marcindulak/vagrant-snort-nfqueue-tutorial-centos7
```

    Cloning into 'vagrant-snort-nfqueue-tutorial-centos7'...


## Copy the `snort` setup files into the `jupyter` working directory


```python
%%bash
cp -rvf vagrant-snort-nfqueue-tutorial-centos7/* .
```

    'vagrant-snort-nfqueue-tutorial-centos7/configure_node_exporter_on_snort.sh' -> './configure_node_exporter_on_snort.sh'
    'vagrant-snort-nfqueue-tutorial-centos7/configure_prometheus_on_monitor.sh' -> './configure_prometheus_on_monitor.sh'
    'vagrant-snort-nfqueue-tutorial-centos7/copr-marcindulak-snort.repo' -> './copr-marcindulak-snort.repo'
    'vagrant-snort-nfqueue-tutorial-centos7/ipynb/vagrant-snort-nfqueue-tutorial-centos7.ipynb' -> './ipynb/vagrant-snort-nfqueue-tutorial-centos7.ipynb'
    'vagrant-snort-nfqueue-tutorial-centos7/LICENSE' -> './LICENSE'
    'vagrant-snort-nfqueue-tutorial-centos7/node_exporter.json' -> './node_exporter.json'
    'vagrant-snort-nfqueue-tutorial-centos7/pytbull_config.cfg' -> './pytbull_config.cfg'
    'vagrant-snort-nfqueue-tutorial-centos7/README.md' -> './README.md'
    'vagrant-snort-nfqueue-tutorial-centos7/snort-alert-count.py' -> './snort-alert-count.py'
    'vagrant-snort-nfqueue-tutorial-centos7/snort-alert-count.service' -> './snort-alert-count.service'
    'vagrant-snort-nfqueue-tutorial-centos7/snort-test-alert.service' -> './snort-test-alert.service'
    'vagrant-snort-nfqueue-tutorial-centos7/Vagrantfile' -> './Vagrantfile'


## Bring up the VMs

 Note that the output appears only when the shell exits, be patient. It should take about 5-20 minutes on a modern hardware.


```python
%%bash
vagrant up
```

    Bringing machine 'attacker0' up with 'virtualbox' provider...
    Bringing machine 'monitor0' up with 'virtualbox' provider...
    Bringing machine 'snort0' up with 'virtualbox' provider...
    ==> attacker0: Importing base box 'bento/centos-7.3'...
    [K==> attacker0: Matching MAC address for NAT networking...
    ==> attacker0: Checking if box 'bento/centos-7.3' is up to date...
    ==> attacker0: Setting the name of the VM: jupyter_attacker0_1488730840517_36544
    ==> attacker0: Clearing any previously set network interfaces...
    ==> attacker0: Preparing network interfaces based on configuration...
        attacker0: Adapter 1: nat
        attacker0: Adapter 2: hostonly
    ==> attacker0: Forwarding ports...
        attacker0: 22 (guest) => 2222 (host) (adapter 1)
    ==> attacker0: Running 'pre-boot' VM customizations...
    ==> attacker0: Booting VM...
    ==> attacker0: Waiting for machine to boot. This may take a few minutes...
        attacker0: SSH address: 127.0.0.1:2222
        attacker0: SSH username: vagrant
        attacker0: SSH auth method: private key
        attacker0: Warning: Remote connection disconnect. Retrying...
        attacker0: Warning: Remote connection disconnect. Retrying...
        attacker0: Warning: Remote connection disconnect. Retrying...
        attacker0: 
        attacker0: Vagrant insecure key detected. Vagrant will automatically replace
        attacker0: this with a newly generated keypair for better security.
        attacker0: 
        attacker0: Inserting generated public key within guest...
        attacker0: Removing insecure key from the guest if it's present...
        attacker0: Key inserted! Disconnecting and reconnecting using new SSH key...
    ==> attacker0: Machine booted and ready!
    ==> attacker0: Checking for guest additions in VM...
    ==> attacker0: Configuring and enabling network interfaces...
    ==> attacker0: Automatic installation for Landrush IP not enabled
    ==> attacker0: Mounting shared folders...
        attacker0: /vagrant => /scratch/ubuntu/jupyter
    ==> attacker0: Running provisioner: shell...
        attacker0: Running: inline script
    ==> attacker0: Running provisioner: shell...
        attacker0: Running: inline script
    ==> attacker0: Running provisioner: shell...
        attacker0: Running: inline script
    ==> attacker0: Running provisioner: shell...
        attacker0: Running: inline script
    ==> attacker0: Running provisioner: shell...
        attacker0: Running: inline script
    ==> attacker0: Running provisioner: shell...
        attacker0: Running: inline script
    ==> attacker0: Running provisioner: shell...
        attacker0: Running: inline script
    ==> attacker0: 
    ==> attacker0: ================================================================================
    ==> attacker0:  Package            Arch         Version   Repository                      Size
    ==> attacker0: ================================================================================
    ==> attacker0: Installing:
    ==> attacker0:  epel-release       noarch       7-9       /epel-release-7-9.noarch        24 k
    ==> attacker0: 
    ==> attacker0: Transaction Summary
    ==> attacker0: ================================================================================
    ==> attacker0: Install  1 Package
    ==> attacker0: 
    ==> attacker0: Total size: 24 k
    ==> attacker0: Installed size: 24 k
    ==> attacker0: 
    ==> attacker0: Installed:
    ==> attacker0:   epel-release.noarch 0:7-9                                                     
    ==> attacker0: Running provisioner: shell...
        attacker0: Running: inline script
    ==> attacker0: net.ipv6.conf.default.disable_ipv6 = 1
    ==> attacker0: net.ipv6.conf.all.disable_ipv6 = 1
    ==> attacker0: net.ipv6.conf.lo.disable_ipv6 = 1
    ==> attacker0: Running provisioner: shell...
        attacker0: Running: inline script
    ==> attacker0: 
    ==> attacker0: ================================================================================
    ==> attacker0:  Package             Arch       Version                       Repository   Size
    ==> attacker0: ================================================================================
    ==> attacker0: Installing:
    ==> attacker0:  ntp                 x86_64     4.2.6p5-25.el7.centos.1       updates     547 k
    ==> attacker0: Installing for dependencies:
    ==> attacker0:  autogen-libopts     x86_64     5.18-5.el7                    base         66 k
    ==> attacker0:  ntpdate             x86_64     4.2.6p5-25.el7.centos.1       updates      85 k
    ==> attacker0: 
    ==> attacker0: Transaction Summary
    ==> attacker0: ================================================================================
    ==> attacker0: Install  1 Package (+2 Dependent packages)
    ==> attacker0: 
    ==> attacker0: Total download size: 699 k
    ==> attacker0: Installed size: 1.6 M
    ==> attacker0: Public key for autogen-libopts-5.18-5.el7.x86_64.rpm is not installed
    ==> attacker0: warning: /var/cache/yum/x86_64/7/base/packages/autogen-libopts-5.18-5.el7.x86_64.rpm: Header V3 RSA/SHA256 Signature, key ID f4a80eb5: NOKEY
    ==> attacker0: Public key for ntpdate-4.2.6p5-25.el7.centos.1.x86_64.rpm is not installed
    ==> attacker0: Importing GPG key 0xF4A80EB5:
    ==> attacker0:  Userid     : "CentOS-7 Key (CentOS 7 Official Signing Key) <security@centos.org>"
    ==> attacker0:  Fingerprint: 6341 ab27 53d7 8a78 a7c2 7bb1 24c6 a8a7 f4a8 0eb5
    ==> attacker0:  Package    : centos-release-7-3.1611.el7.centos.x86_64 (@anaconda)
    ==> attacker0:  From       : /etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7
    ==> attacker0: 
    ==> attacker0: Installed:
    ==> attacker0:   ntp.x86_64 0:4.2.6p5-25.el7.centos.1                                          
    ==> attacker0: 
    ==> attacker0: Dependency Installed:
    ==> attacker0:   autogen-libopts.x86_64 0:5.18-5.el7  ntpdate.x86_64 0:4.2.6p5-25.el7.centos.1 
    ==> attacker0: Running provisioner: shell...
        attacker0: Running: inline script
    ==> attacker0: Created symlink from /etc/systemd/system/multi-user.target.wants/ntpd.service to /usr/lib/systemd/system/ntpd.service.
    ==> attacker0: Running provisioner: shell...
        attacker0: Running: inline script
    ==> monitor0: Importing base box 'bento/centos-7.3'...
    [K==> monitor0: Matching MAC address for NAT networking...
    ==> monitor0: Checking if box 'bento/centos-7.3' is up to date...
    ==> monitor0: Setting the name of the VM: jupyter_monitor0_1488730918093_50224
    ==> monitor0: Fixed port collision for 22 => 2222. Now on port 2200.
    ==> monitor0: Clearing any previously set network interfaces...
    ==> monitor0: Preparing network interfaces based on configuration...
        monitor0: Adapter 1: nat
        monitor0: Adapter 2: hostonly
    ==> monitor0: Forwarding ports...
        monitor0: 22 (guest) => 2200 (host) (adapter 1)
    ==> monitor0: Running 'pre-boot' VM customizations...
    ==> monitor0: Booting VM...
    ==> monitor0: Waiting for machine to boot. This may take a few minutes...
        monitor0: SSH address: 127.0.0.1:2200
        monitor0: SSH username: vagrant
        monitor0: SSH auth method: private key
        monitor0: Warning: Remote connection disconnect. Retrying...
        monitor0: Warning: Remote connection disconnect. Retrying...
        monitor0: Warning: Remote connection disconnect. Retrying...
        monitor0: 
        monitor0: Vagrant insecure key detected. Vagrant will automatically replace
        monitor0: this with a newly generated keypair for better security.
        monitor0: 
        monitor0: Inserting generated public key within guest...
        monitor0: Removing insecure key from the guest if it's present...
        monitor0: Key inserted! Disconnecting and reconnecting using new SSH key...
    ==> monitor0: Machine booted and ready!
    ==> monitor0: Checking for guest additions in VM...
    ==> monitor0: Configuring and enabling network interfaces...
    ==> monitor0: Automatic installation for Landrush IP not enabled
    ==> monitor0: Mounting shared folders...
        monitor0: /vagrant => /scratch/ubuntu/jupyter
    ==> monitor0: Running provisioner: shell...
        monitor0: Running: inline script
    ==> monitor0: Running provisioner: shell...
        monitor0: Running: inline script
    ==> monitor0: Running provisioner: shell...
        monitor0: Running: inline script
    ==> monitor0: Running provisioner: shell...
        monitor0: Running: inline script
    ==> monitor0: Running provisioner: shell...
        monitor0: Running: inline script
    ==> monitor0: Running provisioner: shell...
        monitor0: Running: inline script
    ==> monitor0: Running provisioner: shell...
        monitor0: Running: inline script
    ==> monitor0: 
    ==> monitor0: ================================================================================
    ==> monitor0:  Package            Arch         Version   Repository                      Size
    ==> monitor0: ================================================================================
    ==> monitor0: Installing:
    ==> monitor0:  epel-release       noarch       7-9       /epel-release-7-9.noarch        24 k
    ==> monitor0: 
    ==> monitor0: Transaction Summary
    ==> monitor0: ================================================================================
    ==> monitor0: Install  1 Package
    ==> monitor0: 
    ==> monitor0: Total size: 24 k
    ==> monitor0: Installed size: 24 k
    ==> monitor0: 
    ==> monitor0: Installed:
    ==> monitor0:   epel-release.noarch 0:7-9                                                     
    ==> monitor0: Running provisioner: shell...
        monitor0: Running: inline script
    ==> monitor0: Detected operating system as centos/7.
    ==> monitor0: Checking for curl...
    ==> monitor0: Detected curl...
    ==> monitor0: Downloading repository file: https://packagecloud.io/install/repositories/prometheus-rpm/release/config_file.repo?os=centos&dist=7&source=script
    ==> monitor0: done.
    ==> monitor0: Installing pygpgme to verify GPG signatures...
    ==> monitor0: Importing GPG key 0x7457CCD1:
    ==> monitor0:  Userid     : "https://packagecloud.io/prometheus-rpm/centos (https://packagecloud.io/docs#gpg_signing) <support@packagecloud.io>"
    ==> monitor0:  Fingerprint: d7df c575 af4b 92c6 e62a d3c5 f721 6757 7457 ccd1
    ==> monitor0:  From       : https://packagecloud.io/prometheus-rpm/release/gpgkey
    ==> monitor0: Package pygpgme-0.3-9.el7.x86_64 already installed and latest version
    ==> monitor0: Installing yum-utils...
    ==> monitor0: Public key for libxml2-python-2.9.1-6.el7_2.3.x86_64.rpm is not installed
    ==> monitor0: warning: /var/cache/yum/x86_64/7/base/packages/libxml2-python-2.9.1-6.el7_2.3.x86_64.rpm: Header V3 RSA/SHA256 Signature, key ID f4a80eb5: NOKEY
    ==> monitor0: Importing GPG key 0xF4A80EB5:
    ==> monitor0:  Userid     : "CentOS-7 Key (CentOS 7 Official Signing Key) <security@centos.org>"
    ==> monitor0:  Fingerprint: 6341 ab27 53d7 8a78 a7c2 7bb1 24c6 a8a7 f4a8 0eb5
    ==> monitor0:  Package    : centos-release-7-3.1611.el7.centos.x86_64 (@anaconda)
    ==> monitor0:  From       : /etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7
    ==> monitor0: Generating yum cache for prometheus-rpm_release...
    ==> monitor0: Importing GPG key 0x7457CCD1:
    ==> monitor0:  Userid     : "https://packagecloud.io/prometheus-rpm/centos (https://packagecloud.io/docs#gpg_signing) <support@packagecloud.io>"
    ==> monitor0:  Fingerprint: d7df c575 af4b 92c6 e62a d3c5 f721 6757 7457 ccd1
    ==> monitor0:  From       : https://packagecloud.io/prometheus-rpm/release/gpgkey
    ==> monitor0: 
    ==> monitor0: The repository is setup! You can now install packages.
    ==> monitor0: Running provisioner: shell...
        monitor0: Running: inline script
    ==> monitor0: net.ipv6.conf.default.disable_ipv6 = 1
    ==> monitor0: net.ipv6.conf.all.disable_ipv6 = 1
    ==> monitor0: net.ipv6.conf.lo.disable_ipv6 = 1
    ==> monitor0: Running provisioner: shell...
        monitor0: Running: inline script
    ==> monitor0: 
    ==> monitor0: ================================================================================
    ==> monitor0:  Package             Arch       Version                       Repository   Size
    ==> monitor0: ================================================================================
    ==> monitor0: Installing:
    ==> monitor0:  ntp                 x86_64     4.2.6p5-25.el7.centos.1       updates     547 k
    ==> monitor0: Installing for dependencies:
    ==> monitor0:  autogen-libopts     x86_64     5.18-5.el7                    base         66 k
    ==> monitor0:  ntpdate             x86_64     4.2.6p5-25.el7.centos.1       updates      85 k
    ==> monitor0: 
    ==> monitor0: Transaction Summary
    ==> monitor0: ================================================================================
    ==> monitor0: Install  1 Package (+2 Dependent packages)
    ==> monitor0: 
    ==> monitor0: Total download size: 699 k
    ==> monitor0: Installed size: 1.6 M
    ==> monitor0: 
    ==> monitor0: Installed:
    ==> monitor0:   ntp.x86_64 0:4.2.6p5-25.el7.centos.1                                          
    ==> monitor0: 
    ==> monitor0: Dependency Installed:
    ==> monitor0:   autogen-libopts.x86_64 0:5.18-5.el7  ntpdate.x86_64 0:4.2.6p5-25.el7.centos.1 
    ==> monitor0: Running provisioner: shell...
        monitor0: Running: inline script
    ==> monitor0: Created symlink from /etc/systemd/system/multi-user.target.wants/ntpd.service to /usr/lib/systemd/system/ntpd.service.
    ==> monitor0: Running provisioner: shell...
        monitor0: Running: inline script
    ==> snort0: Importing base box 'bento/centos-7.3'...
    [K==> snort0: Matching MAC address for NAT networking...
    ==> snort0: Checking if box 'bento/centos-7.3' is up to date...
    ==> snort0: Setting the name of the VM: jupyter_snort0_1488731018034_93022
    ==> snort0: Fixed port collision for 22 => 2222. Now on port 2201.
    ==> snort0: Clearing any previously set network interfaces...
    ==> snort0: Preparing network interfaces based on configuration...
        snort0: Adapter 1: nat
        snort0: Adapter 2: hostonly
    ==> snort0: Forwarding ports...
        snort0: 22 (guest) => 2201 (host) (adapter 1)
    ==> snort0: Running 'pre-boot' VM customizations...
    ==> snort0: Booting VM...
    ==> snort0: Waiting for machine to boot. This may take a few minutes...
        snort0: SSH address: 127.0.0.1:2201
        snort0: SSH username: vagrant
        snort0: SSH auth method: private key
        snort0: Warning: Remote connection disconnect. Retrying...
        snort0: Warning: Remote connection disconnect. Retrying...
        snort0: Warning: Remote connection disconnect. Retrying...
        snort0: 
        snort0: Vagrant insecure key detected. Vagrant will automatically replace
        snort0: this with a newly generated keypair for better security.
        snort0: 
        snort0: Inserting generated public key within guest...
        snort0: Removing insecure key from the guest if it's present...
        snort0: Key inserted! Disconnecting and reconnecting using new SSH key...
    ==> snort0: Machine booted and ready!
    ==> snort0: Checking for guest additions in VM...
    ==> snort0: Configuring and enabling network interfaces...
    ==> snort0: Automatic installation for Landrush IP not enabled
    ==> snort0: Mounting shared folders...
        snort0: /vagrant => /scratch/ubuntu/jupyter
    ==> snort0: Running provisioner: shell...
        snort0: Running: inline script
    ==> snort0: Running provisioner: shell...
        snort0: Running: inline script
    ==> snort0: Running provisioner: shell...
        snort0: Running: inline script
    ==> snort0: Running provisioner: shell...
        snort0: Running: inline script
    ==> snort0: Running provisioner: shell...
        snort0: Running: inline script
    ==> snort0: Running provisioner: shell...
        snort0: Running: inline script
    ==> snort0: Running provisioner: shell...
        snort0: Running: inline script
    ==> snort0: 
    ==> snort0: ================================================================================
    ==> snort0:  Package            Arch         Version   Repository                      Size
    ==> snort0: ================================================================================
    ==> snort0: Installing:
    ==> snort0:  epel-release       noarch       7-9       /epel-release-7-9.noarch        24 k
    ==> snort0: 
    ==> snort0: Transaction Summary
    ==> snort0: ================================================================================
    ==> snort0: Install  1 Package
    ==> snort0: 
    ==> snort0: Total size: 24 k
    ==> snort0: Installed size: 24 k
    ==> snort0: 
    ==> snort0: Installed:
    ==> snort0:   epel-release.noarch 0:7-9                                                     
    ==> snort0: Running provisioner: shell...
        snort0: Running: inline script
    ==> snort0: Running provisioner: shell...
        snort0: Running: inline script
    ==> snort0: Detected operating system as centos/7.
    ==> snort0: Checking for curl...
    ==> snort0: Detected curl...
    ==> snort0: Downloading repository file: https://packagecloud.io/install/repositories/prometheus-rpm/release/config_file.repo?os=centos&dist=7&source=script
    ==> snort0: done.
    ==> snort0: Installing pygpgme to verify GPG signatures...
    ==> snort0: Importing GPG key 0x7457CCD1:
    ==> snort0:  Userid     : "https://packagecloud.io/prometheus-rpm/centos (https://packagecloud.io/docs#gpg_signing) <support@packagecloud.io>"
    ==> snort0:  Fingerprint: d7df c575 af4b 92c6 e62a d3c5 f721 6757 7457 ccd1
    ==> snort0:  From       : https://packagecloud.io/prometheus-rpm/release/gpgkey
    ==> snort0: Package pygpgme-0.3-9.el7.x86_64 already installed and latest version
    ==> snort0: Installing yum-utils...
    ==> snort0: warning: /var/cache/yum/x86_64/7/base/packages/yum-utils-1.1.31-40.el7.noarch.rpm: Header V3 RSA/SHA256 Signature, key ID f4a80eb5: NOKEY
    ==> snort0: Public key for yum-utils-1.1.31-40.el7.noarch.rpm is not installed
    ==> snort0: Importing GPG key 0xF4A80EB5:
    ==> snort0:  Userid     : "CentOS-7 Key (CentOS 7 Official Signing Key) <security@centos.org>"
    ==> snort0:  Fingerprint: 6341 ab27 53d7 8a78 a7c2 7bb1 24c6 a8a7 f4a8 0eb5
    ==> snort0:  Package    : centos-release-7-3.1611.el7.centos.x86_64 (@anaconda)
    ==> snort0:  From       : /etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7
    ==> snort0: Generating yum cache for prometheus-rpm_release...
    ==> snort0: Importing GPG key 0x7457CCD1:
    ==> snort0:  Userid     : "https://packagecloud.io/prometheus-rpm/centos (https://packagecloud.io/docs#gpg_signing) <support@packagecloud.io>"
    ==> snort0:  Fingerprint: d7df c575 af4b 92c6 e62a d3c5 f721 6757 7457 ccd1
    ==> snort0:  From       : https://packagecloud.io/prometheus-rpm/release/gpgkey
    ==> snort0: 
    ==> snort0: The repository is setup! You can now install packages.
    ==> snort0: Running provisioner: shell...
        snort0: Running: inline script
    ==> snort0: net.ipv6.conf.default.disable_ipv6 = 1
    ==> snort0: net.ipv6.conf.all.disable_ipv6 = 1
    ==> snort0: net.ipv6.conf.lo.disable_ipv6 = 1
    ==> snort0: Running provisioner: shell...
        snort0: Running: inline script
    ==> snort0: 
    ==> snort0: ================================================================================
    ==> snort0:  Package             Arch       Version                       Repository   Size
    ==> snort0: ================================================================================
    ==> snort0: Installing:
    ==> snort0:  ntp                 x86_64     4.2.6p5-25.el7.centos.1       updates     547 k
    ==> snort0: Installing for dependencies:
    ==> snort0:  autogen-libopts     x86_64     5.18-5.el7                    base         66 k
    ==> snort0:  ntpdate             x86_64     4.2.6p5-25.el7.centos.1       updates      85 k
    ==> snort0: 
    ==> snort0: Transaction Summary
    ==> snort0: ================================================================================
    ==> snort0: Install  1 Package (+2 Dependent packages)
    ==> snort0: Total download size: 699 k
    ==> snort0: Installed size: 1.6 M
    ==> snort0: 
    ==> snort0: Installed:
    ==> snort0:   ntp.x86_64 0:4.2.6p5-25.el7.centos.1                                          
    ==> snort0: 
    ==> snort0: Dependency Installed:
    ==> snort0:   autogen-libopts.x86_64 0:5.18-5.el7  ntpdate.x86_64 0:4.2.6p5-25.el7.centos.1 
    ==> snort0: Running provisioner: shell...
        snort0: Running: inline script
    ==> snort0: Created symlink from /etc/systemd/system/multi-user.target.wants/ntpd.service to /usr/lib/systemd/system/ntpd.service.
    ==> snort0: Running provisioner: shell...
        snort0: Running: inline script


While waiting look at https://github.com/marcindulak/vagrant-snort-tutorial-centos7/blob/master/Vagrantfile. Notice that only a base system installation is performed on the VMs. The actual configuration of the machines is performed below.

## Configure `prometheus` on **monitor0**


```python
%%bash
vagrant ssh monitor0 -c "sudo su - -c 'sh /vagrant/configure_prometheus_on_monitor.sh'"
```

    Detected operating system as centos/7.
    Checking for curl...
    Detected curl...
    Downloading repository file: https://packagecloud.io/install/repositories/prometheus-rpm/release/config_file.repo?os=centos&dist=7&source=script
    done.
    Installing pygpgme to verify GPG signatures...
    Package pygpgme-0.3-9.el7.x86_64 already installed and latest version
    Installing yum-utils...
    Package yum-utils-1.1.31-40.el7.noarch already installed and latest version
    Generating yum cache for prometheus-rpm_release...
    
    The repository is setup! You can now install packages.
    
    ================================================================================
     Package       Arch      Version                Repository                 Size
    ================================================================================
    Installing:
     prometheus    x86_64    1.5.2-1.el7.centos     prometheus-rpm_release    9.6 M
    
    Transaction Summary
    ================================================================================
    Install  1 Package
    
    Total download size: 9.6 M
    Installed size: 48 M
    
    Installed:
      prometheus.x86_64 0:1.5.2-1.el7.centos                                        
    


    Created symlink from /etc/systemd/system/multi-user.target.wants/prometheus.service to /usr/lib/systemd/system/prometheus.service.



```python
%%bash
vagrant ssh monitor0 -c "sudo su - -c 'install -m 644 /vagrant/node_exporter.json /etc/prometheus'"
```

This configures the `prometheus` server on **monitor0**.

The `prometheus` server periodically pulls the metrics exposed by the nodes defined in `/etc/prometheus/node_exporter.json`.
Node exporter (https://github.com/prometheus/node_exporter) allows one to expose an arbitrary metric from a machine running the `node_exporter` service, using the functionality of Textfile Collector.

## Configure `snort` on **snort0**


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'install -m 644 /vagrant/copr-marcindulak-snort.repo /etc/yum.repos.d'"
```


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'yum -y -d 1 -e 0 install snort snort-extra'"
```

    
    ================================================================================
     Package          Arch   Version                   Repository              Size
    ================================================================================
    Installing:
     snort            x86_64 3.0.0-0.227.a4.el7.centos copr-marcindulak-snort 1.8 M
     snort-extra      x86_64 1.0.0-0.227.a4.el7.centos copr-marcindulak-snort 134 k
    Installing for dependencies:
     daq              x86_64 2.2.1-1.el7.centos        copr-marcindulak-snort  86 k
     daq-modules      x86_64 2.2.1-1.el7.centos        copr-marcindulak-snort  37 k
     hwloc-libs       x86_64 1.11.2-1.el7              base                   1.5 M
     libdnet          x86_64 1.12-13.1.el7             base                    31 k
     libnetfilter_queue
                      x86_64 1.0.2-2.el7               epel                    23 k
     libtool-ltdl     x86_64 2.4.2-21.el7_2            base                    49 k
     luajit           x86_64 2.0.4-3.el7               epel                   343 k
    
    Transaction Summary
    ================================================================================
    Install  2 Packages (+7 Dependent packages)
    
    Total download size: 3.9 M
    Installed size: 11 M
    Public key for libnetfilter_queue-1.0.2-2.el7.x86_64.rpm is not installed
    Public key for daq-modules-2.2.1-1.el7.centos.x86_64.rpm is not installed
    
    Installed:
      snort.x86_64 0:3.0.0-0.227.a4.el7.centos                                      
      snort-extra.x86_64 0:1.0.0-0.227.a4.el7.centos                                
    
    Dependency Installed:
      daq.x86_64 0:2.2.1-1.el7.centos                                               
      daq-modules.x86_64 0:2.2.1-1.el7.centos                                       
      hwloc-libs.x86_64 0:1.11.2-1.el7                                              
      libdnet.x86_64 0:1.12-13.1.el7                                                
      libnetfilter_queue.x86_64 0:1.0.2-2.el7                                       
      libtool-ltdl.x86_64 0:2.4.2-21.el7_2                                          
      luajit.x86_64 0:2.0.4-3.el7                                                   
    


    warning: /var/cache/yum/x86_64/7/epel/packages/libnetfilter_queue-1.0.2-2.el7.x86_64.rpm: Header V3 RSA/SHA256 Signature, key ID 352c64e5: NOKEY
    warning: /var/cache/yum/x86_64/7/copr-marcindulak-snort/packages/daq-modules-2.2.1-1.el7.centos.x86_64.rpm: Header V3 RSA/SHA1 Signature, key ID 37627d2f: NOKEY
    Importing GPG key 0x37627D2F:
     Userid     : "marcindulak_snort (None) <marcindulak#snort@copr.fedorahosted.org>"
     Fingerprint: 987e e485 5793 87ee 3581 3bfb a919 6b3b 3762 7d2f
     From       : https://copr-be.cloud.fedoraproject.org/results/marcindulak/snort/pubkey.gpg
    Importing GPG key 0x352C64E5:
     Userid     : "Fedora EPEL (7) <epel@fedoraproject.org>"
     Fingerprint: 91e9 7d7c 4a5e 96f1 7f3e 888f 6a2f aea2 352c 64e5
     Package    : epel-release-7-9.noarch (installed)
     From       : /etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-7



```python
%%bash
! vagrant ssh snort0 -c "sudo su - -c 'systemctl is-active snort@enp0s8'"
```

    unknown


The exclamation mark above is used in order to assert that the command return with non-zero exit status.
We want a non-zero status because `snort` service should not be active yet. Note that `jupyter` cell does not "care" about the exit status, but if you run the command in the terminal or as part of as shell script the exit status does matter. 

## Disable affixing of unified2.log

The instance of `snort` is configured to log alerts and payloads which triggered the alerts in the `unified2` format (https://www.snort.org/faq/readme-unified2).

At every `snort` restart or when the maximum size of the log file is exceeded `snort` will create a `/var/log/snort/unified2.log.`date +%s` file, i.e. `/var/log/snort/unified2.log.` followed by the number of seconds elapsed since 1970-01-01 00:00:00 UTC (https://en.wikipedia.org/wiki/Unix_time).

This is inconvenient for the purpose of demonstrations and therefore adjust the `snort` configuration to always write to `/var/log/snort/unified2.log


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c \"echo unified2 = { limit = 128, units = \'M\', nostamp = true, mpls_event_types = true, vlan_event_types = true } >> /etc/snort/snort.lua\""""
```

## Workaround for http://seclists.org/snort/2017/q1/581


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c \"sed -i 's|/usr/lib64/snort_extra|/usr/lib64/snort_extra/codecs|' /usr/lib/systemd/system/snort@.service\""
```


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'systemctl daemon-reload'"
```

## Start snort


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'systemctl start snort@enp0s8'"
```


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'systemctl is-active snort@enp0s8'"
```

    active


"active" means `snort` is running now.

An important comment needs to be made about the `iptables` configuration:


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'iptables-save'"
```

    # Generated by iptables-save v1.4.21 on Sun Mar  5 16:26:00 2017
    *filter
    :INPUT ACCEPT [50:7194]
    :FORWARD ACCEPT [0:0]
    :OUTPUT ACCEPT [36:6074]
    -A INPUT -i enp0s8 -j NFQUEUE --queue-num 0 --queue-bypass
    -A OUTPUT -o enp0s8 -j NFQUEUE --queue-num 0 --queue-bypass
    COMMIT
    # Completed on Sun Mar  5 16:26:00 2017


which is performed by the `snort` service


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'systemctl status snort@enp0s8'"
```

    ● snort@enp0s8.service - Snort on 'enp0s8'
       Loaded: loaded (/usr/lib/systemd/system/snort@.service; disabled; vendor preset: disabled)
       Active: active (running) since Sun 2017-03-05 16:25:55 UTC; 7s ago
      Process: 5096 ExecStartPre=/bin/sh -c /usr/sbin/iptables -t filter -C OUTPUT -o %I -j NFQUEUE --queue-num 0 --queue-bypass || /usr/sbin/iptables -t filter -I OUTPUT -o %I -j NFQUEUE --queue-num 0 --queue-bypass (code=exited, status=0/SUCCESS)
      Process: 5086 ExecStartPre=/bin/sh -c /usr/sbin/iptables -t filter -C INPUT -i %I -j NFQUEUE --queue-num 0 --queue-bypass || /usr/sbin/iptables -t filter -I INPUT -i %I -j NFQUEUE --queue-num 0 --queue-bypass (code=exited, status=0/SUCCESS)
     Main PID: 5101 (snort)
       CGroup: /system.slice/system-snort.slice/snort@enp0s8.service
               └─5101 /usr/sbin/snort -d -Q --daq-dir /usr/lib64/daq --daq nfq -l /var/log/snort -c /etc/snort/snort.lua -A unified2 -v --plugin-path /usr/lib64/snort_extra/codecs
    
    Mar 05 16:25:55 snort0 snort[5101]: Non-Encoded MIME attachment Extraction Depth: 1460
    Mar 05 16:25:55 snort0 snort[5101]: SSH config:
    Mar 05 16:25:55 snort0 snort[5101]: Max Encrypted Packets: 25
    Mar 05 16:25:55 snort0 snort[5101]: Max Server Version String Length: 80
    Mar 05 16:25:55 snort0 snort[5101]: MaxClientBytes: 19600
    Mar 05 16:25:55 snort0 snort[5101]: Portscan Detection Config:
    Mar 05 16:25:55 snort0 snort[5101]: Detect Protocols:  TCP UDP ICMP IP
    Mar 05 16:25:55 snort0 snort[5101]: Detect Scan Type:  portscan portsweep decoy_portscan distributed_portscan
    Mar 05 16:25:55 snort0 snort[5101]: Sensitivity Level: Medium
    Mar 05 16:25:55 snort0 snort[5101]: Memcap (in bytes): 1048576


In this setup all the traffic reaching `snort0` is passed to `nfqueue` for `snort` inspection. It should be **stressed** that the traffic after being processed by the `nfqueue` target does to return back to `netfilter` - `iptables` won't process any further rules https://sourceforge.net/p/snort/mailman/message/29066595/.
On a production system one would first filter the traffic using `iptables` rules and pass the remaining, "good" traffic to `nfqueue` for further `snort` inspection. This would however limit `snort`'s ability to detect events which involve multiple ports, like portscans.

## Configure `node_exporter` for **snort0**


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'sh /vagrant/configure_node_exporter_on_snort.sh'"
```

    Detected operating system as centos/7.
    Checking for curl...
    Detected curl...
    Downloading repository file: https://packagecloud.io/install/repositories/prometheus-rpm/release/config_file.repo?os=centos&dist=7&source=script
    done.
    Installing pygpgme to verify GPG signatures...
    Package pygpgme-0.3-9.el7.x86_64 already installed and latest version
    Installing yum-utils...
    Package yum-utils-1.1.31-40.el7.noarch already installed and latest version
    Generating yum cache for prometheus-rpm_release...
    
    The repository is setup! You can now install packages.
    
    ================================================================================
     Package         Arch     Version                Repository                Size
    ================================================================================
    Installing:
     node_exporter   x86_64   0.13.0-1.el7.centos    prometheus-rpm_release   2.3 M
    
    Transaction Summary
    ================================================================================
    Install  1 Package
    
    Total download size: 2.3 M
    Installed size: 7.9 M
    
    Installed:
      node_exporter.x86_64 0:0.13.0-1.el7.centos                                    
    


    Created symlink from /etc/systemd/system/multi-user.target.wants/node_exporter.service to /usr/lib/systemd/system/node_exporter.service.



```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'systemctl daemon-reload'"
```


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'yum -d 1 -e 0 -y install python*-idstools python-dateutil'"
```

    
    ================================================================================
     Package                  Arch          Version               Repository   Size
    ================================================================================
    Installing:
     python-dateutil          noarch        1.5-7.el7             base         85 k
     python2-idstools         noarch        0.5.4-1.el7           epel         76 k
     python34-idstools        noarch        0.5.4-1.el7           epel         78 k
    Installing for dependencies:
     python34                 x86_64        3.4.5-3.el7           epel         50 k
     python34-libs            x86_64        3.4.5-3.el7           epel        6.7 M
    
    Transaction Summary
    ================================================================================
    Install  3 Packages (+2 Dependent packages)
    
    Total download size: 7.0 M
    Installed size: 28 M
    
    Installed:
      python-dateutil.noarch 0:1.5-7.el7      python2-idstools.noarch 0:0.5.4-1.el7 
      python34-idstools.noarch 0:0.5.4-1.el7 
    
    Dependency Installed:
      python34.x86_64 0:3.4.5-3.el7        python34-libs.x86_64 0:3.4.5-3.el7       
    



```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'install -m 755 /vagrant/snort-alert-count.py /usr/local/bin'"
```


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'install -m 644 /vagrant/snort-alert-count.service /usr/lib/systemd/system'"
```


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'systemctl daemon-reload'"
```


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'systemctl enable snort-alert-count'"
```

    Created symlink from /etc/systemd/system/multi-user.target.wants/snort-alert-count.service to /usr/lib/systemd/system/snort-alert-count.service.



```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'systemctl start snort-alert-count'"
```


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'systemctl is-active snort-alert-count'"
```

    active


In the context of `snort` this means: the `snort-alert-count.py` script continuously reads the `snort` alerts unified2 file generated by `snort` on **snort0** and writes the Textfile Collector file on **snort0** under `/var/lib/prometheus`.
The `node_exporter` service on **snort0** reads this file and exposes the metrics to the `prometheus` server.
  
Anyone willing to correct `snort-alert-count.py` so it writes the Textfile Collector file at regular time intervals, **independently** whether new alerts are arriving? Contributions are welcome.

# Snort usage

## Drop ICMP traffic

The classic example presented in most `snort` tutorials when explaining `snort` rules is to alert on `ping`. Our `snort` instance runs in IPS mode so we will be able to block 'pings'.

Here is a great introduction to `snort` rules "DevNet 1126 Detection Strategies with Snort" https://www.youtube.com/watch?v=-aeZ6OD8BPg

### Verify that `ping` works between `monitor0` and `snort0`


```python
%%bash
vagrant ssh monitor0 -c "sudo su - -c 'ping -c 1 -W 1 -I enp0s8 snort0'"
```

    PING snort0 (192.168.17.30) from 192.168.17.20 enp0s8: 56(84) bytes of data.
    64 bytes from snort0 (192.168.17.30): icmp_seq=1 ttl=64 time=16.2 ms
    
    --- snort0 ping statistics ---
    1 packets transmitted, 1 received, 0% packet loss, time 0ms
    rtt min/avg/max/mdev = 16.218/16.218/16.218/0.000 ms


### Copy the default `sample.rules` distributed by `snort` and enable them in `/etc/snort/snort_defaults.lua`


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'cp -p /etc/snort/sample.rules /etc/snort/rules/snort.rules'"
```


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c \"echo RULE_PATH = conf_dir .. \'/rules\' >> /etc/snort/snort_defaults.lua\""  # http://seclists.org/snort/2017/q1/524
```


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c \"echo ips = { include = RULE_PATH .. \'/snort.rules\' } >> /etc/snort/snort_defaults.lua\""
```

### Enable dropping of incoming ICMP traffic on `snort0` by appending the appropriate rule to `/etc/snort/rules/sample.rules`


```python
%%bash
echo 'drop icmp any any -> 192.168.17.30 any (msg:"icmp any any -> 192.168.17.30 any"; sid:3000001; rev:001;)' > 3000001.rules
```


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'cat /vagrant/3000001.rules >> /etc/snort/rules/snort.rules'"
```

The `3000001` is the first, free for a custom use, Signature ID after the ET rules (https://rules.emergingthreats.net/)

### Make `snort` to re-read the rules without restarting


```python
%%bash
vagrant ssh snort0 -c 'sudo su - -c "kill -hup $(pidof snort)"'
```


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'systemctl is-active snort@enp0s8'"
```

    active


### Verify that the ICMP traffic is now blocked by `snort0`


```python
%%bash
! vagrant ssh monitor0 -c "sudo su - -c 'ping -c 1 -W 1 -I enp0s8 snort0'"
```

    PING snort0 (192.168.17.30) from 192.168.17.20 enp0s8: 56(84) bytes of data.
    
    --- snort0 ping statistics ---
    1 packets transmitted, 0 received, 100% packet loss, time 0ms
    


If at this point the packet is **not** being dropped you may have another `snort0` or `monitor0` instance active somewhere from another `vagrant up`, or some other issue.

### Enable dropping of outgoing ICMP traffic on `snort0`


```python
%%bash
echo 'drop icmp 192.168.17.30 any -> any any (msg:"icmp 192.168.17.30 any -> any any"; sid:3000002; rev:001;)' > 3000002.rules
```


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'cat /vagrant/3000002.rules >> /etc/snort/rules/snort.rules'"
```


```python
%%bash
vagrant ssh snort0 -c 'sudo su - -c "kill -hup $(pidof snort)"'
```


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'ping -c 1 -W 1 -I enp0s8 monitor0'"
```

    PING monitor0 (192.168.17.20) from 192.168.17.30 enp0s8: 56(84) bytes of data.
    
    --- monitor0 ping statistics ---
    1 packets transmitted, 0 received, 100% packet loss, time 0ms
    


Note that the IDS functionality with `nfqueue` requires `snort` to run as `root`. In order to run `snort` in IDS mode change the user from `root` to `snort` and
remove the `-Q` option from `/usr/lib/systemd/system/snort@.service`.

## Display the alerts

Until now we should have two alerts showing the dropped incoming and outgoing ICMP packets. The details of the alert and the payload can be displayed using `u2spewfoo`


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'u2spewfoo /var/log/snort/unified2.log'"
```

    
    (Event)
    	sensor id: 0	event id: 1	event second: 1488731227	event microsecond: 371831
    	sig id: 3000001	gen id: 1	revision: 1	 classification: 0
    	priority: 0	ip source: 192.168.17.20	ip destination: 192.168.17.30
    	src port: 0	dest port: 0	ip_proto: 1	impact_flag: 0	blocked: 0
    	mpls label: 0	vland id: 0	policy id: 0
    
    Packet
    	sensor id: 0	event id: 1	event second: 1488731227
    	packet second: 1488731227	packet microsecond: 371831
    	linktype: 228	packet_length: 84
    [    0] 45 00 00 54 B9 54 40 00 40 01 DD D1 C0 A8 11 14  E..T.T@.@.......
    [   16] C0 A8 11 1E 08 00 62 B5 13 4E 00 01 5B 3C BC 58  ......b..N..[<.X
    [   32] 00 00 00 00 A6 93 05 00 00 00 00 00 10 11 12 13  ................
    [   48] 14 15 16 17 18 19 1A 1B 1C 1D 1E 1F 20 21 22 23  ............ !"#
    [   64] 24 25 26 27 28 29 2A 2B 2C 2D 2E 2F 30 31 32 33  $%&'()*+,-./0123
    [   80] 34 35 36 37                                      4567
    
    (Event)
    	sensor id: 0	event id: 2	event second: 1488731235	event microsecond: 779042
    	sig id: 3000002	gen id: 1	revision: 1	 classification: 0
    	priority: 0	ip source: 192.168.17.30	ip destination: 192.168.17.20
    	src port: 0	dest port: 0	ip_proto: 1	impact_flag: 0	blocked: 0
    	mpls label: 0	vland id: 0	policy id: 0
    
    Packet
    	sensor id: 0	event id: 2	event second: 1488731235
    	packet second: 1488731235	packet microsecond: 779042
    	linktype: 228	packet_length: 84
    [    0] 45 00 00 54 56 A4 40 00 40 01 40 82 C0 A8 11 1E  E..TV.@.@.@.....
    [   16] C0 A8 11 14 08 00 4C 2A 17 8A 00 01 63 3C BC 58  ......L*....c<.X
    [   32] 00 00 00 00 AA E2 0B 00 00 00 00 00 10 11 12 13  ................
    [   48] 14 15 16 17 18 19 1A 1B 1C 1D 1E 1F 20 21 22 23  ............ !"#
    [   64] 24 25 26 27 28 29 2A 2B 2C 2D 2E 2F 30 31 32 33  $%&'()*+,-./0123
    [   80] 34 35 36 37                                      4567


An alternative method of listing the contents of the `unified2` log is performed using https://github.com/jasonish/py-idstools,
which converts `unified2` to `json` or `eve` (https://redmine.openinfosecfoundation.org/projects/suricata/wiki/_Logstash_Kibana_and_Suricata_JSON_output).


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'idstools-u2json /var/log/snort/unified2.log'"
```

    {"event": {"dport-icode": 0, "event-id": 1, "priority": 0, "impact": 0, "destination-ip": "192.168.17.30", "signature-revision": 1, "mpls-label": 0, "impact-flag": 0, "sensor-id": 0, "sport-itype": 0, "source-ip": "192.168.17.20", "protocol": 1, "classification-id": 0, "event-second": 1488731227, "generator-id": 1, "event-microsecond": 371831, "pad2": 0, "vlan-id": 0, "signature-id": 3000001, "blocked": 0}}
    {"packet": {"sensor-id": 0, "event-second": 1488731227, "length": 84, "data": "b'RQAAVLlUQABAAd3RwKgRFMCoER4IAGK1E04AAVs8vFgAAAAAppMFAAAAAAAQERITFBUWFxgZGhscHR4fICEiIyQlJicoKSorLC0uLzAxMjM0NTY3'", "packet-second": 1488731227, "event-id": 1, "linktype": 228, "packet-microsecond": 371831}}
    {"event": {"dport-icode": 0, "event-id": 2, "priority": 0, "impact": 0, "destination-ip": "192.168.17.20", "signature-revision": 1, "mpls-label": 0, "impact-flag": 0, "sensor-id": 0, "sport-itype": 0, "source-ip": "192.168.17.30", "protocol": 1, "classification-id": 0, "event-second": 1488731235, "generator-id": 1, "event-microsecond": 779042, "pad2": 0, "vlan-id": 0, "signature-id": 3000002, "blocked": 0}}
    {"packet": {"sensor-id": 0, "event-second": 1488731235, "length": 84, "data": "b'RQAAVFakQABAAUCCwKgRHsCoERQIAEwqF4oAAWM8vFgAAAAAquILAAAAAAAQERITFBUWFxgZGhscHR4fICEiIyQlJicoKSorLC0uLzAxMjM0NTY3'", "packet-second": 1488731235, "event-id": 2, "linktype": 228, "packet-microsecond": 779042}}


    WARNING: No alert message map entries loaded.
    WARNING: No classifications loaded.


Note that despite the fact that the packet has been dropped `unified2` does not provide this information as can be seen from the `u2spewfoo` output. As a consequence `idstools-u2json` assumes the packet has not been dropped. It seems worth inquiring the `snort-users` mailing list https://lists.sourceforge.net/lists/listinfo/snort-users whether the `unified2` missing *blocked* information is a bug, ar maybe a missing feature.

There is also tool `u2boat` for converting `unified2` into `pcap`, but does not seem to work as expected http://seclists.org/snort/2017/q1/11


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'u2boat /var/log/snort/unified2.log /tmp/u2boat.pcap'"
```

    Defaulting to pcap output.



```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'yum -d 1 -e 0 -y install tcpdump'"
```

    
    ================================================================================
     Package          Arch            Version                   Repository     Size
    ================================================================================
    Installing:
     tcpdump          x86_64          14:4.5.1-3.el7            base          387 k
    
    Transaction Summary
    ================================================================================
    Install  1 Package
    
    Total download size: 387 k
    Installed size: 931 k
    
    Installed:
      tcpdump.x86_64 14:4.5.1-3.el7                                                 
    



```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'tcpdump -XX -r /tmp/u2boat.pcap'" | grep 'ethertype Unknown'
```

    16:27:07.371831 40:00:40:01:dd:d1 (oui Unknown) > 45:00:00:54:b9:54 (oui Unknown), ethertype Unknown (0xc0a8), length 84: 
    16:27:15.779042 40:00:40:01:40:82 (oui Unknown) > 45:00:00:54:56:a4 (oui Unknown), ethertype Unknown (0xc0a8), length 84: 


    reading from file /tmp/u2boat.pcap, link-type EN10MB (Ethernet)


See "Introduction to Packet Analysis" https://www.youtube.com/watch?v=visrNiKIP3E&index=17 for a refresher about network protocols and
tools like `tcpdump` or `wireshark`.

The `eve` format is used when pushing `snort` logs into ELK (https://www.elastic.co/products), or for converting `unified2` into `pcap`


```python
%%bash
vagrant ssh snort0 -c 'sudo su - -c "python2 $(which idstools-u2eve) /var/log/snort/unified2.log > /tmp/u2eve.log"'
```

    WARNING: No alert message map entries loaded.
    WARNING: No classifications loaded.



```python
%%bash
vagrant ssh snort0 -c "sudo su - -c \"sed -i 's/-0600/+0000/' /usr/lib/python2.7/site-packages/idstools/scripts/eve2pcap.py\""  # https://github.com/jasonish/py-idstools/issues/37
```


```python
%%bash
vagrant ssh snort0 -c 'sudo su - -c "python2 $(which idstools-eve2pcap) /tmp/u2eve.log --dlt RAW -o /tmp/u2eve2pcap.pcap"'
```


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'tcpdump -XX -r /tmp/u2eve2pcap.pcap'" | grep 'ICMP'
```

    16:27:07.371831 IP monitor0 > snort0: ICMP echo request, id 4942, seq 1, length 64
    16:27:15.779042 IP snort0 > monitor0: ICMP echo request, id 6026, seq 1, length 64


    reading from file /tmp/u2eve2pcap.pcap, link-type RAW (Raw IP)


## Periodic test alert

A periodic test alert can be setup (http://ossectools.blogspot.dk/2011/04/network-intrusion-detection-systems.html) the purpose of which
will be to probe whether `snort` or another resource on `snort0` is able to keep up with the traffic. If the rate of the test alert
falls below a threshold we will know that some alerts were missed by `snort`. An HTTP request on port 80 will be used as a test alert.

### In order for the rule to triggered a web server must be listening on port 80 on `snort0`


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'yum -d 1 -e 0 -y install httpd'"
```

    
    ================================================================================
     Package            Arch          Version                     Repository   Size
    ================================================================================
    Installing:
     httpd              x86_64        2.4.6-45.el7.centos         base        2.7 M
    Installing for dependencies:
     apr                x86_64        1.4.8-3.el7                 base        103 k
     apr-util           x86_64        1.5.2-6.el7                 base         92 k
     httpd-tools        x86_64        2.4.6-45.el7.centos         base         84 k
     mailcap            noarch        2.1.41-2.el7                base         31 k
    
    Transaction Summary
    ================================================================================
    Install  1 Package (+4 Dependent packages)
    
    Total download size: 3.0 M
    Installed size: 10 M
    
    Installed:
      httpd.x86_64 0:2.4.6-45.el7.centos                                            
    
    Dependency Installed:
      apr.x86_64 0:1.4.8-3.el7                     apr-util.x86_64 0:1.5.2-6.el7    
      httpd-tools.x86_64 0:2.4.6-45.el7.centos     mailcap.noarch 0:2.1.41-2.el7    
    



```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'systemctl enable httpd'"
```

    Created symlink from /etc/systemd/system/multi-user.target.wants/httpd.service to /usr/lib/systemd/system/httpd.service.


### The rule must be added to detect the test alert

The proper rule would like alert tcp 192.168.17.20 any -> any 80 (msg:"snort-test-alert"; flow:to_server,established; http_uri; content:"/snort-test-alert"; metadata:service http; classtype:not-suspicious; sid:3000003; rev:001;) but due to http://seclists.org/snort/2017/q1/635 it is modified


```python
%%bash
echo 'alert tcp 192.168.17.20 any -> any 80 (msg:"snort-test-alert"; content:"/snort-test-alert"; classtype:not-suspicious; sid:3000003; rev:001;)' > 3000003.rules
```


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'cat /vagrant/3000003.rules >> /etc/snort/rules/snort.rules'"
```


```python
%%bash
vagrant ssh snort0 -c 'sudo su - -c "kill -hup $(pidof snort)"'
```

The HTTP request is sent using `curl -s -m 1 http://snort0/snort-test-alert` from `monitor0`, let's save it's `pcap` on `snort0`. The `pcap` will be later used to
test how much traffic `snort0` can handle by replaying the traffic with `tcpreplay`

In order to capture the HTTP traffic Apache must be listening


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'systemctl start httpd'"
```


```python
%%bash
vagrant ssh monitor0 -c "sudo su - -c 'yum -d 1 -e 0 -y install at'"
```

    
    ================================================================================
     Package       Arch              Version                  Repository       Size
    ================================================================================
    Installing:
     at            x86_64            3.1.13-22.el7            base             51 k
    
    Transaction Summary
    ================================================================================
    Install  1 Package
    
    Total download size: 51 k
    Installed size: 95 k
    
    Installed:
      at.x86_64 0:3.1.13-22.el7                                                     
    



```python
%%bash
vagrant ssh monitor0 -c "sudo su - -c 'systemctl start atd'"
```


```python
%%bash
vagrant ssh monitor0 -c "echo 'curl -s -m 1 http://snort0/snort-test-alert' | at now + 1 minute"
```

    job 1 at Sun Mar  5 16:30:00 2017



```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'timeout 70 tcpdump -i enp0s8 port 80 -w /vagrant/snort-test-alert.pcap'"
```

    tcpdump: listening on enp0s8, link-type EN10MB (Ethernet), capture size 65535 bytes
    10 packets captured
    10 packets received by filter
    0 packets dropped by kernel


We expect 10 packets to be captured. Verify that the test alert has been detected by `snort`


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'idstools-u2json /var/log/snort/unified2.log'" | grep '"signature-id": 3000003'
```

    {"event": {"priority": 3, "blocked": 0, "event-second": 1488731401, "generator-id": 1, "sensor-id": 0, "protocol": 6, "event-id": 3, "signature-id": 3000003, "signature-revision": 1, "dport-icode": 80, "destination-ip": "192.168.17.30", "impact": 0, "impact-flag": 0, "source-ip": "192.168.17.20", "classification-id": 1, "vlan-id": 0, "event-microsecond": 76418, "sport-itype": 44018, "mpls-label": 0, "pad2": 0}}


    WARNING: No alert message map entries loaded.
    WARNING: No classifications loaded.


Let's stop Apache for the purpose of the demonstrations in the next section


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'systemctl stop httpd'"
```

and restart `snort` to clear the `unified2` log.


```python
%%bash
vagrant ssh snort0 -c 'sudo su - -c "systemctl restart snort@enp0s8"'
```

### After having verified the test alert is being detected by `snort` enable the `snort-test-alert` service


```python
%%bash
vagrant ssh monitor0 -c "sudo su - -c 'install -m 644 /vagrant/snort-test-alert.service /usr/lib/systemd/system'"
```


```python
%%bash
vagrant ssh monitor0 -c "sudo su - -c 'systemctl daemon-reload'"
```


```python
%%bash
vagrant ssh monitor0 -c "sudo su - -c 'systemctl enable snort-test-alert'"
```

    Created symlink from /etc/systemd/system/multi-user.target.wants/snort-test-alert.service to /usr/lib/systemd/system/snort-test-alert.service.



```python
%%bash
vagrant ssh monitor0 -c "sudo su - -c 'systemctl start snort-test-alert'"
```


```python
%%bash
vagrant ssh monitor0 -c "sudo su - -c 'systemctl is-active snort-test-alert'"
```

    active


The test alert should keep appearing in the `tcpdump` output on `snort0`


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'timeout 10 tcpdump -i enp0s8 port 80'" | grep snort0.http
```

    16:35:42.861239 IP monitor0.44122 > snort0.http: Flags [S], seq 2779488221, win 29200, options [mss 1460,sackOK,TS val 515613 ecr 0,nop,wscale 6], length 0
    16:35:42.861687 IP snort0.http > monitor0.44122: Flags [R.], seq 0, ack 2779488222, win 0, length 0


    tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
    listening on enp0s8, link-type EN10MB (Ethernet), capture size 65535 bytes
    2 packets captured
    2 packets received by filter
    0 packets dropped by kernel


but it is not yet detectable by `snort` (because `httpd` is not running, only `tcp` traffic is exchanged)


```python
%%bash
! vagrant ssh snort0 -c "sudo su - -c 'idstools-u2json /var/log/snort/unified2.log'" | grep '"signature-id": 3000003'
```

    WARNING: No alert message map entries loaded.
    WARNING: No classifications loaded.


### After Apache is started the test alerts will be detected by `snort`


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'systemctl start httpd&& sleep 10'"
```


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'u2spewfoo /var/log/snort/unified2.log'"
```

    
    (Event)
    	sensor id: 0	event id: 1	event second: 1488731752	event microsecond: 872101
    	sig id: 3000003	gen id: 1	revision: 1	 classification: 1
    	priority: 3	ip source: 192.168.17.20	ip destination: 192.168.17.30
    	src port: 44128	dest port: 80	ip_proto: 6	impact_flag: 0	blocked: 0
    	mpls label: 0	vland id: 0	policy id: 0
    
    Packet
    	sensor id: 0	event id: 1	event second: 1488731752
    	packet second: 1488731752	packet microsecond: 872101
    	linktype: 228	packet_length: 138
    [    0] 45 00 00 8A E9 7D 40 00 40 06 AD 6D C0 A8 11 14  E....}@.@..m....
    [   16] C0 A8 11 1E AC 60 00 50 4D 02 EC 4D F0 37 04 8B  .....`.PM..M.7..
    [   32] 80 18 01 C9 19 A6 00 00 01 01 08 0A 00 08 05 39  ...............9
    [   48] 00 06 7D C7 47 45 54 20 2F 73 6E 6F 72 74 2D 74  ..}.GET /snort-t
    [   64] 65 73 74 2D 61 6C 65 72 74 20 48 54 54 50 2F 31  est-alert HTTP/1
    [   80] 2E 31 0D 0A 55 73 65 72 2D 41 67 65 6E 74 3A 20  .1..User-Agent: 
    [   96] 63 75 72 6C 2F 37 2E 32 39 2E 30 0D 0A 48 6F 73  curl/7.29.0..Hos
    [  112] 74 3A 20 73 6E 6F 72 74 30 0D 0A 41 63 63 65 70  t: snort0..Accep
    [  128] 74 3A 20 2A 2F 2A 0D 0A 0D 0A                    t: */*....
    
    (Event)
    	sensor id: 0	event id: 2	event second: 1488731762	event microsecond: 882214
    	sig id: 3000003	gen id: 1	revision: 1	 classification: 1
    	priority: 3	ip source: 192.168.17.20	ip destination: 192.168.17.30
    	src port: 44130	dest port: 80	ip_proto: 6	impact_flag: 0	blocked: 0
    	mpls label: 0	vland id: 0	policy id: 0
    
    Packet
    	sensor id: 0	event id: 2	event second: 1488731762
    	packet second: 1488731762	packet microsecond: 882214
    	linktype: 228	packet_length: 138
    [    0] 45 00 00 8A 89 79 40 00 40 06 0D 72 C0 A8 11 14  E....y@.@..r....
    [   16] C0 A8 11 1E AC 62 00 50 80 C6 A5 26 30 E0 44 58  .....b.P...&0.DX
    [   32] 80 18 01 C9 5E 5C 00 00 01 01 08 0A 00 08 2C 53  ....^\........,S
    [   48] 00 06 A4 E2 47 45 54 20 2F 73 6E 6F 72 74 2D 74  ....GET /snort-t
    [   64] 65 73 74 2D 61 6C 65 72 74 20 48 54 54 50 2F 31  est-alert HTTP/1
    [   80] 2E 31 0D 0A 55 73 65 72 2D 41 67 65 6E 74 3A 20  .1..User-Agent: 
    [   96] 63 75 72 6C 2F 37 2E 32 39 2E 30 0D 0A 48 6F 73  curl/7.29.0..Hos
    [  112] 74 3A 20 73 6E 6F 72 74 30 0D 0A 41 63 63 65 70  t: snort0..Accep
    [  128] 74 3A 20 2A 2F 2A 0D 0A 0D 0A                    t: */*....



```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'idstools-u2json /var/log/snort/unified2.log'" | grep '"signature-id": 3000003'
```

    {"event": {"sport-itype": 44128, "pad2": 0, "protocol": 6, "event-microsecond": 872101, "signature-id": 3000003, "impact-flag": 0, "signature-revision": 1, "generator-id": 1, "priority": 3, "mpls-label": 0, "dport-icode": 80, "blocked": 0, "impact": 0, "source-ip": "192.168.17.20", "sensor-id": 0, "destination-ip": "192.168.17.30", "classification-id": 1, "vlan-id": 0, "event-id": 1, "event-second": 1488731752}}
    {"event": {"sport-itype": 44130, "pad2": 0, "protocol": 6, "event-microsecond": 882214, "signature-id": 3000003, "impact-flag": 0, "signature-revision": 1, "generator-id": 1, "priority": 3, "mpls-label": 0, "dport-icode": 80, "blocked": 0, "impact": 0, "source-ip": "192.168.17.20", "sensor-id": 0, "destination-ip": "192.168.17.30", "classification-id": 1, "vlan-id": 0, "event-id": 2, "event-second": 1488731762}}


    WARNING: No alert message map entries loaded.
    WARNING: No classifications loaded.


## Snort alerts in Prometheus

Prometheus is not best suited for storing and analyzing `snort` alerts but the simplicity of `prometheus` configuration fits well into this tutorial.
For an introduction to `prometheus` see "An introduction to monitoring and alerting with time-series at scale, with Prometheus" https://www.youtube.com/watch?v=gNmWzkGViAY

The `snort-alert-count.py` script on `snort0` continuously reads the output produced by `idstools-u2json /var/log/snort/unified2.log` and
periodically writes the `snort` alerts counter into the `/var/lib/prometheus/snort.prom`.


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'grep snort_alert_count /var/lib/prometheus/snort.prom'"
```

    # HELP snort_alert_count Snort alert count.
    # TYPE snort_alert_count counter
    snort_alert_count{generator_id="1",signature_id="3000003",blocked="0",source_ip="192.168.17.20",dport_icode="80"}  1


After several minutes `snort` alerts will start appearing in `prometheus`


```python
%%bash
sleep 300
```


```python
%%bash
vagrant ssh monitor0 -c "curl -sgG --data-urlencode query='rate(snort_alert_count[5m]) * 60' localhost:9090/api/v1/query"
```

    {"status":"success","data":{"resultType":"vector","result":[{"metric":{"blocked":"0","dport_icode":"80","generator_id":"1","instance":"snort0:9100","job":"node","signature_id":"3000003","source_ip":"192.168.17.20"},"value":[1488732072.408,"5.894736842105263"]}]}}

The `prometheus` query 'rate(snort_alert_count[5m]) * 60' returns the average rate of increase of `snort` alerts (per alert) per minute, during the last 5 minutes
(https://prometheus.io/docs/querying/functions/#rate()). The `snort-test-alert` on `monitor0` performs `curl` against `snort0` every 10 seconds
so such defined rate of the test alert should be equal to 6 per minute.

Prometheus has it's own alerting system, but one can simply query the HTTP API of `prometheus` and include such checks into traditional
monitoring systems like `nagios`


```python
%%bash
vagrant ssh monitor0 -c "sudo su - -c 'yum -d 1 -e 0 -y install git jq'"
```

    
    ================================================================================
     Package                Arch         Version                   Repository  Size
    ================================================================================
    Installing:
     git                    x86_64       1.8.3.1-6.el7_2.1         base       4.4 M
     jq                     x86_64       1.5-1.el7                 epel       153 k
    Installing for dependencies:
     libgnome-keyring       x86_64       3.8.0-3.el7               base       109 k
     oniguruma              x86_64       5.9.5-3.el7               epel       129 k
     perl-Error             noarch       1:0.17020-2.el7           base        32 k
     perl-Git               noarch       1.8.3.1-6.el7_2.1         base        53 k
     perl-TermReadKey       x86_64       2.30-20.el7               base        31 k
     rsync                  x86_64       3.0.9-17.el7              base       360 k
    
    Transaction Summary
    ================================================================================
    Install  2 Packages (+6 Dependent packages)
    
    Total download size: 5.2 M
    Installed size: 24 M
    Public key for jq-1.5-1.el7.x86_64.rpm is not installed
    
    Installed:
      git.x86_64 0:1.8.3.1-6.el7_2.1              jq.x86_64 0:1.5-1.el7             
    
    Dependency Installed:
      libgnome-keyring.x86_64 0:3.8.0-3.el7   oniguruma.x86_64 0:5.9.5-3.el7       
      perl-Error.noarch 1:0.17020-2.el7       perl-Git.noarch 0:1.8.3.1-6.el7_2.1  
      perl-TermReadKey.x86_64 0:2.30-20.el7   rsync.x86_64 0:3.0.9-17.el7          
    


    warning: /var/cache/yum/x86_64/7/epel/packages/jq-1.5-1.el7.x86_64.rpm: Header V3 RSA/SHA256 Signature, key ID 352c64e5: NOKEY
    Importing GPG key 0x352C64E5:
     Userid     : "Fedora EPEL (7) <epel@fedoraproject.org>"
     Fingerprint: 91e9 7d7c 4a5e 96f1 7f3e 888f 6a2f aea2 352c 64e5
     Package    : epel-release-7-9.noarch (installed)
     From       : /etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-7



```python
%%bash
vagrant ssh monitor0 -c "git clone https://github.com/prometheus/nagios_plugins"
```

    Cloning into 'nagios_plugins'...



```python
%%bash
vagrant ssh monitor0 -c "bash ./nagios_plugins/check_prometheus_metric.sh -H localhost:9090 -q \"rate(snort_alert_count{signature_id='3000003'}[5m]) * 60\" -w 5 -c 4 -n snort-test-alert -m lt -t vector -i"
```

    OK - snort-test-alert is 6: { blocked: 0, dport_icode: 80, generator_id: 1, instance: snort0:9100, job: node, signature_id: 3000003, source_ip: 192.168.17.20 }


This query will return the "WARNING" when the rate of the test alert drops below 5 and "CRITICAL" when it drops below 4.

Over the years several domain-specific languages (DSL) have been proposed for making the alerts produced by IDS/IPS systems more manageable.
One can use `prometheus` as a poor man's replacement of such a system. For example, it is interesting to know whether there are any
persistent attackers on the network, who access the system over an extended period of time using various or the same types of attacks.

The query below will identify the source IP numbers which triggered an alert during the last 5 minutes, and were also triggering some alerts
(not necessarily the same) during the preceding hour:

((sum without (signature-id,generator-id,dport-icode)(rate(snort_alert_count{alert_id!="1:3000003"}[5m]))) > 0 and (sum without (signature-id,generator-id,dport-icode)(rate(snort_alert_count{alert_id!="1:3000003"}[1h] offset 5m))) > 0) * 60

Another query will provide a complementary information about the types of alerts, which tiggered during the last 5 minutes, and were
also triggered during the preceding hour, independently of the source IP number:

((sum without (source-ip,dport-icode)(rate(snort_alert_count{alert_id!="1:3000003"}[5m]))) > 0 and (sum without (source-ip,dport-icode)(rate(snort_alert_count{alert_id!="1:3000003"}[1h] offset 5m))) > 0) * 60

See "PromCon 2016: Alerting in the Prometheus Universe - Fabian Reinartz" https://www.youtube.com/watch?v=yrK6z3fpu1E for more details about alerting in `prometheus`.

## Manage rules with Pulledpork

Pulledpork [https://github.com/shirkdog/pulledpork](https://github.com/shirkdog/pulledpork) writes the selected rules into `/etc/snort/rules/snort.rules`.

Unfortunately certain rules options have been modified/removed from `snort++` (see https://github.com/snortadmin/snort3/blob/master/doc/differences.txt),
which means that most `snort2` rules are unusable. Just skip this section. The instructions in this section should work with `snort2` however.

`snortrules-snapshot-*.tar.gz` are available for free after registration at https://www.snort.org/downloads, and are divided into `categories`.
On the oter hand the `community-rules.tar.gz` available without registration are not divided into `categories`, but still use `categories` labels in the `msg` field.

Pulledpork works in a slightly complicated way when `categories` are involved (I hope I got it right, if not corrections are welcome).
The behavior is dependent on the setting of the `order` variable in `/etc/pulledpork/pulledpork.conf`, and for `order=disable,enable,drop`:

- all rules that are uncommented in the files distributed within a rules tarball are written into `/etc/snort/rules/snort.rules`

- a category listed in `/etc/pulledpork/enablesid.conf` will enable all rules from the category (also the commented)

- a category listed in `/etc/pulledpork/disablesid.conf` will disable all rules from the category (also the commented)

- a category listed in `/etc/pulledpork/dropsid.conf` will convert uncommented rules from the category to drop, and also the commented rules if the category is in `/etc/pulledpork/enablesid.conf`

- `/etc/pulledpork/modifysid.conf` can be used to modify the rules, like replacing ports or other sequences of characters in the rule

The list of categories and how to create the list manually is here
[https://github.com/shirkdog/pulledpork/blob/master/doc/README.CATEGORIES](https://github.com/shirkdog/pulledpork/blob/master/doc/README.CATEGORIES)

Let's use `community-rules.tar.gz` using `pulledpork`, enabling few categories, disabled (commented) by default


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'yum -d 1 -e 0 -y install pulledpork'"
```

    
    ================================================================================
     Package                     Arch       Version                  Repository
                                                                               Size
    ================================================================================
    Installing:
     pulledpork                  noarch     0.7.2-2.el7              epel      44 k
    Installing for dependencies:
     perl-Archive-Tar            noarch     1.92-2.el7               base      73 k
     perl-Business-ISBN          noarch     2.06-2.el7               base      25 k
     perl-Business-ISBN-Data     noarch     20120719.001-2.el7       base      24 k
     perl-Compress-Raw-Bzip2     x86_64     2.061-3.el7              base      32 k
     perl-Compress-Raw-Zlib      x86_64     1:2.061-4.el7            base      57 k
     perl-Crypt-SSLeay           x86_64     0.64-5.el7               base      58 k
     perl-Data-Dumper            x86_64     2.145-3.el7              base      47 k
     perl-Digest                 noarch     1.17-245.el7             base      23 k
     perl-Digest-MD5             x86_64     2.52-3.el7               base      30 k
     perl-Encode-Locale          noarch     1.03-5.el7               base      16 k
     perl-File-Listing           noarch     6.04-7.el7               base      13 k
     perl-HTML-Parser            x86_64     3.71-4.el7               base     115 k
     perl-HTML-Tagset            noarch     3.20-15.el7              base      18 k
     perl-HTTP-Cookies           noarch     6.01-5.el7               base      26 k
     perl-HTTP-Daemon            noarch     6.01-5.el7               base      20 k
     perl-HTTP-Date              noarch     6.02-8.el7               base      14 k
     perl-HTTP-Message           noarch     6.06-6.el7               base      82 k
     perl-HTTP-Negotiate         noarch     6.01-5.el7               base      17 k
     perl-IO-Compress            noarch     2.061-2.el7              base     260 k
     perl-IO-HTML                noarch     1.00-2.el7               base      23 k
     perl-IO-Socket-IP           noarch     0.21-4.el7               base      35 k
     perl-IO-Socket-SSL          noarch     1.94-5.el7               base     114 k
     perl-IO-Zlib                noarch     1:1.10-291.el7           base      51 k
     perl-LWP-MediaTypes         noarch     6.02-2.el7               base      24 k
     perl-LWP-Protocol-https     noarch     6.04-4.el7               base      11 k
     perl-Mozilla-CA             noarch     20130114-5.el7           base      11 k
     perl-Net-HTTP               noarch     6.06-2.el7               base      29 k
     perl-Net-LibIDN             x86_64     0.12-15.el7              base      28 k
     perl-Net-SSLeay             x86_64     1.55-4.el7               base     285 k
     perl-Package-Constants      noarch     1:0.02-291.el7           base      45 k
     perl-Sys-Syslog             x86_64     0.33-3.el7               base      42 k
     perl-TimeDate               noarch     1:2.30-2.el7             base      52 k
     perl-URI                    noarch     1.60-9.el7               base     106 k
     perl-WWW-RobotRules         noarch     6.02-5.el7               base      18 k
     perl-libwww-perl            noarch     6.05-2.el7               base     205 k
    
    Transaction Summary
    ================================================================================
    Install  1 Package (+35 Dependent packages)
    
    Total download size: 2.0 M
    Installed size: 4.7 M
    
    Installed:
      pulledpork.noarch 0:0.7.2-2.el7                                               
    
    Dependency Installed:
      perl-Archive-Tar.noarch 0:1.92-2.el7                                          
      perl-Business-ISBN.noarch 0:2.06-2.el7                                        
      perl-Business-ISBN-Data.noarch 0:20120719.001-2.el7                           
      perl-Compress-Raw-Bzip2.x86_64 0:2.061-3.el7                                  
      perl-Compress-Raw-Zlib.x86_64 1:2.061-4.el7                                   
      perl-Crypt-SSLeay.x86_64 0:0.64-5.el7                                         
      perl-Data-Dumper.x86_64 0:2.145-3.el7                                         
      perl-Digest.noarch 0:1.17-245.el7                                             
      perl-Digest-MD5.x86_64 0:2.52-3.el7                                           
      perl-Encode-Locale.noarch 0:1.03-5.el7                                        
      perl-File-Listing.noarch 0:6.04-7.el7                                         
      perl-HTML-Parser.x86_64 0:3.71-4.el7                                          
      perl-HTML-Tagset.noarch 0:3.20-15.el7                                         
      perl-HTTP-Cookies.noarch 0:6.01-5.el7                                         
      perl-HTTP-Daemon.noarch 0:6.01-5.el7                                          
      perl-HTTP-Date.noarch 0:6.02-8.el7                                            
      perl-HTTP-Message.noarch 0:6.06-6.el7                                         
      perl-HTTP-Negotiate.noarch 0:6.01-5.el7                                       
      perl-IO-Compress.noarch 0:2.061-2.el7                                         
      perl-IO-HTML.noarch 0:1.00-2.el7                                              
      perl-IO-Socket-IP.noarch 0:0.21-4.el7                                         
      perl-IO-Socket-SSL.noarch 0:1.94-5.el7                                        
      perl-IO-Zlib.noarch 1:1.10-291.el7                                            
      perl-LWP-MediaTypes.noarch 0:6.02-2.el7                                       
      perl-LWP-Protocol-https.noarch 0:6.04-4.el7                                   
      perl-Mozilla-CA.noarch 0:20130114-5.el7                                       
      perl-Net-HTTP.noarch 0:6.06-2.el7                                             
      perl-Net-LibIDN.x86_64 0:0.12-15.el7                                          
      perl-Net-SSLeay.x86_64 0:1.55-4.el7                                           
      perl-Package-Constants.noarch 1:0.02-291.el7                                  
      perl-Sys-Syslog.x86_64 0:0.33-3.el7                                           
      perl-TimeDate.noarch 1:2.30-2.el7                                             
      perl-URI.noarch 0:1.60-9.el7                                                  
      perl-WWW-RobotRules.noarch 0:6.02-5.el7                                       
      perl-libwww-perl.noarch 0:6.05-2.el7                                          
    



```python
%%bash
vagrant ssh snort0 -c "sudo su - -c \"sed -i '/IPBLACKLIST/d' /etc/pulledpork/pulledpork.conf\""  # we don't use IP blacklisting feature
```


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'echo pcre:INDICATOR-SCAN >> /etc/pulledpork/enablesid.conf'"
```


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'echo pcre:SERVER-APACHE >> /etc/pulledpork/enablesid.conf'"
```


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'echo pcre:SERVER-WEBAPP >> /etc/pulledpork/enablesid.conf'"
```

Fetch and install the selected rules, under `/tmp/snort.rules` - on our setup we don't want to overwrite `/etc/snort/rules/snort.rules`!


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'pulledpork -PE -c /etc/pulledpork/pulledpork.conf -o /tmp/snort.rules'"
```

     
        https://github.com/shirkdog/pulledpork
          _____ ____
         `----,\    )
          `--==\\  /    PulledPork v0.7.2 - E.Coli in your water bottle!
           `--==\\/
         .-~~~~-.Y|\\_  Copyright (C) 2009-2016 JJ Cummings
      @_/        /  66\_  cummingsj@gmail.com
        |    \   \   _(")
         \   /-| ||'--'  Rules give me wings!
          \_\  \_\\
     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Checking latest MD5 for community-rules.tar.gz....
    Rules tarball download of community-rules.tar.gz....
    	They Match
    	Done!
    Checking latest MD5 for opensource.tar.gz....
    Rules tarball download of opensource.tar.gz....
    	They Match
    	Done!
    Prepping rules from community-rules.tar.gz for work....
    	Done!
    Prepping rules from opensource.tar.gz for work....
    	Done!
    Reading rules...
    Modifying Sids....
    	Done!
    Processing /etc/pulledpork/enablesid.conf....
    	Modified 831 rules
    	Skipped 831 rules (already disabled)
    	Done
    Processing /etc/pulledpork/dropsid.conf....
    	Modified 0 rules
    	Skipped 0 rules (already disabled)
    	Done
    Processing /etc/pulledpork/disablesid.conf....
    	Modified 0 rules
    	Skipped 0 rules (already disabled)
    	Done
    Setting Flowbit State....
    	Done
    Writing /tmp/snort.rules....
    	Done
    Generating sid-msg.map....
    	Done
    Writing v1 /etc/snort/sid-msg.map....
    	Done
    Writing /var/log/sid_changes.log....
    	Done
    Rule Stats...
    	New:-------1693
    	Deleted:---0
    	Enabled Rules:----1693
    	Dropped Rules:----0
    	Disabled Rules:---0
    	Total Rules:------1693
    No IP Blacklist Changes
    
    Done
    Please review /var/log/sid_changes.log for additional details
    Fly Piggy Fly!


## Examples of actions from the attacker machine

This subject is virtually unlimited, but a representative set of actions detectable by `snort` is available at https://www.aldeid.com/wiki/Suricata-vs-snort

### Portscans

The "SYN" scan consists of finding out whether a TCP port is open by sending "SYN".
The port is considered open when "SYN-ACK" or "SYN" is received https://nmap.org/book/man-port-scanning-techniques.html
The rule detecting "SYN" (PSNG_TCP_PORTSCAN) belongs to the portscan preprocessor and is included in `snortrules-snapshot-*.tar.gz`, available for free after registration. However, at https://www.snort.org/faq/readme-sfportscan we find that the "TCP Portscan" corresponds to gid 122, sid 1, so we write our own version of this rule


```python
%%bash
echo 'alert ( msg: "PSNG_TCP_PORTSCAN"; sid: 1; gid: 122; rev: 1; )' > 122:1.rules
```


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'cat /vagrant/122:1.rules >> /etc/snort/rules/snort.rules'"
```

In order to detect this type of portscan performed by a single host the `sense_level` needs to be set to `high`


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c \"sed -i '/port_scan/d' /etc/snort/snort.lua\""
```


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c \"echo port_scan = { sense_level = \'high\' } >> /etc/snort/snort.lua\""
```


```python
%%bash
vagrant ssh snort0 -c 'sudo su - -c "kill -hup $(pidof snort)"'
```

Perform the scan from `attacker0`, saving the `pcap` file


```python
%%bash
vagrant ssh attacker0 -c 'sudo su - -c "yum -d 1 -e 0 -y install nmap"'
```

    
    ================================================================================
     Package            Arch            Version                 Repository     Size
    ================================================================================
    Installing:
     nmap               x86_64          2:6.40-7.el7            base          4.0 M
    Installing for dependencies:
     nmap-ncat          x86_64          2:6.40-7.el7            base          201 k
    
    Transaction Summary
    ================================================================================
    Install  1 Package (+1 Dependent package)
    
    Total download size: 4.2 M
    Installed size: 17 M
    
    Installed:
      nmap.x86_64 2:6.40-7.el7                                                      
    
    Dependency Installed:
      nmap-ncat.x86_64 2:6.40-7.el7                                                 
    



```python
%%bash
vagrant ssh attacker0 -c "sudo su - -c 'yum -d 1 -e 0 -y install at'"
```

    
    ================================================================================
     Package       Arch              Version                  Repository       Size
    ================================================================================
    Installing:
     at            x86_64            3.1.13-22.el7            base             51 k
    
    Transaction Summary
    ================================================================================
    Install  1 Package
    
    Total download size: 51 k
    Installed size: 95 k
    
    Installed:
      at.x86_64 0:3.1.13-22.el7                                                     
    



```python
%%bash
vagrant ssh attacker0 -c "sudo su - -c 'systemctl start atd'"
```


```python
%%bash
vagrant ssh attacker0 -c "sudo su -c \"echo 'nmap -sS snort0' | at now + 1 minute\""
```

    job 1 at Sun Mar  5 16:43:00 2017



```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'timeout 70 tcpdump -i enp0s8 tcp and host attacker0 -w /vagrant/portscan.pcap'"
```

    tcpdump: listening on enp0s8, link-type EN10MB (Ethernet), capture size 65535 bytes
    1886 packets captured
    2004 packets received by filter
    118 packets dropped by kernel


`snort` is able to detect the "SYN" scan in the captured `pcap` file


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'SNORT_LUA_PATH=/etc/snort LUA_PATH=/usr/include/snort/lua/?.lua snort --daq-dir /usr/lib64/daq -c /etc/snort/snort.lua --plugin-path /usr/lib64/snort_extra -R /etc/snort/rules/snort.rules -r /vagrant/portscan.pcap -A alert_fast -q'"
```

    03/05-16:43:00.630631 [**] [122:1:1] "PSNG_TCP_PORTSCAN" [**] [Priority: 0] {IP} 192.168.17.10 -> 192.168.17.30



```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'idstools-u2json /var/log/snort/unified2.log'" | grep -v packet | grep '"signature-id": 1' | grep '"generator-id": 122' 
```

    {"event": {"sport-itype": 0, "sensor-id": 0, "vlan-id": 0, "event-id": 44, "classification-id": 0, "generator-id": 122, "signature-id": 1, "blocked": 0, "pad2": 0, "signature-revision": 1, "source-ip": "192.168.17.10", "event-second": 1488732180, "dport-icode": 0, "impact-flag": 0, "protocol": 6, "event-microsecond": 630592, "destination-ip": "192.168.17.30", "mpls-label": 0, "priority": 0, "impact": 0}}


    WARNING: No alert message map entries loaded.
    WARNING: No classifications loaded.


### Tcpreplay

Here `tcpreplay` is used from the `attacker0` machine, this is actually not an attack.
The reason for using `attacker0` is the amount of RAM needed for caching of packets in `tcpeplay`, but also to demonstrate the purpose of `tcprewrite`.

We will be pretending to be `monitor0` from `attacker0`. In order to demonstrate this let's disable the `snort-test-alert` on `monitor0`


```python
%%bash
vagrant ssh monitor0 -c "sudo su - -c 'systemctl stop snort-test-alert'"
```

and get the total number of tiggered test alerts until now. All of them were triggered by the traffic from `monitor0` to `snort0`


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'idstools-u2json /var/log/snort/unified2.log'" | grep -v packet | grep '"signature-id": 3000003' | grep '192.168.17.30' | wc -l
```

    48


    WARNING: No alert message map entries loaded.
    WARNING: No classifications loaded.


Let's replay the test alert 100000 times aiming at 200 Mbps (which may or may not be reached, depending on the speed of you RAM) from the original `pcap`


```python
%%bash
vagrant ssh attacker0 -c 'sudo su - -c "yum -d 1 -e 0 -y install tcpreplay"'
```

    
    ================================================================================
     Package            Arch            Version                 Repository     Size
    ================================================================================
    Installing:
     tcpreplay          x86_64          4.1.2-1.el7             epel          299 k
    Installing for dependencies:
     tcpdump            x86_64          14:4.5.1-3.el7          base          387 k
    
    Transaction Summary
    ================================================================================
    Install  1 Package (+1 Dependent package)
    
    Total download size: 687 k
    Installed size: 2.2 M
    Public key for tcpreplay-4.1.2-1.el7.x86_64.rpm is not installed
    
    Installed:
      tcpreplay.x86_64 0:4.1.2-1.el7                                                
    
    Dependency Installed:
      tcpdump.x86_64 14:4.5.1-3.el7                                                 
    


    warning: /var/cache/yum/x86_64/7/epel/packages/tcpreplay-4.1.2-1.el7.x86_64.rpm: Header V3 RSA/SHA256 Signature, key ID 352c64e5: NOKEY
    Importing GPG key 0x352C64E5:
     Userid     : "Fedora EPEL (7) <epel@fedoraproject.org>"
     Fingerprint: 91e9 7d7c 4a5e 96f1 7f3e 888f 6a2f aea2 352c 64e5
     Package    : epel-release-7-9.noarch (installed)
     From       : /etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-7



```python
%%bash
vagrant ssh attacker0 -c 'sudo su - -c "tcpreplay -K -l 100000 -M 200 --intf1 enp0s8 /vagrant/snort-test-alert.pcap"'
```

    Actual: 1000000 packets (113600000 bytes) sent in 6.04 seconds.
    Rated: 17731700.0 Bps, 141.85 Mbps, 156089.32 pps
    Flows: 2 flows, 0.31 fps, 1000000 flow packets, 0 non-flow
    Statistics for network device: enp0s8
    	Successful packets:        1000000
    	Failed packets:            0
    	Truncated packets:         0
    	Retried packets (ENOBUFS): 0
    	Retried packets (EAGAIN):  0


    File Cache is enabled


Note that the `attacker0` IP is not detected by `snort0`, but instead the count for alerts from `monitor0` increases significantly


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'idstools-u2json /var/log/snort/unified2.log'" | grep -v packet | grep '"signature-id": 3000003' | grep '192.168.17.10' | wc -l
```

    0


    WARNING: No alert message map entries loaded.
    WARNING: No classifications loaded.



```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'idstools-u2json /var/log/snort/unified2.log'" | grep -v packet | grep '"signature-id": 3000003' | grep '192.168.17.20' | wc -l
```

    4594


    WARNING: No alert message map entries loaded.
    WARNING: No classifications loaded.


After this test make sure the `prometheus` level of the test snort alert is restored


```python
%%bash
vagrant ssh monitor0 -c "sudo su - -c 'systemctl start snort-test-alert'"
```


```python
%%bash
vagrant ssh monitor0 -c "sudo su - -c 'systemctl is-active snort-test-alert'"
```

    active



```python
%%bash
sleep 300
```


```python
%%bash
vagrant ssh monitor0 -c "bash ./nagios_plugins/check_prometheus_metric.sh -H localhost:9090 -q \"rate(snort_alert_count{source_ip='192.168.17.20',signature_id='3000003'}[5m]) * 60\" -w 5 -c 4 -n snort-test-alert -m lt -t vector -i"
```

    OK - snort-test-alert is 963: { blocked: 0, dport_icode: 80, generator_id: 1, instance: snort0:9100, job: node, signature_id: 3000003, source_ip: 192.168.17.20 }


Let's now `tcprewrite` the source in the `snort-test-alert.pcap` to honestly report that we are an `attacker0`. `tcprewrite` of the destination would be necessary if `pcap` has been captured on a different machine than `snort0`


```python
%%bash
vagrant ssh attacker0 -c 'tcprewrite --infile=/vagrant/snort-test-alert.pcap --outfile=/tmp/1.pcap --dstipmap=0.0.0.0/0:192.168.17.30 --enet-dmac=08:00:27:00:17:30 --portmap=80:80'
```


```python
%%bash
vagrant ssh attacker0 -c 'tcprewrite --infile=/tmp/1.pcap --outfile=/tmp/2.pcap --srcipmap=0.0.0.0/0:192.168.17.10 --enet-smac=08:00:27:00:17:10'
```

Replay it, this time with 20 times more packets, this will take about 5 minutes


```python
%%bash
vagrant ssh attacker0 -c 'sudo su - -c "tcpreplay -K -l 2000000 -M 200 --intf1 enp0s8 /tmp/2.pcap"'
```

    Actual: 20000000 packets (2272000000 bytes) sent in 147.00 seconds.
    Rated: 15447500.0 Bps, 123.58 Mbps, 135981.74 pps
    Flows: 2 flows, 0.01 fps, 20000000 flow packets, 0 non-flow
    Statistics for network device: enp0s8
    	Successful packets:        20000000
    	Failed packets:            0
    	Truncated packets:         0
    	Retried packets (ENOBUFS): 0
    	Retried packets (EAGAIN):  0


    File Cache is enabled


The CPU/Memory usage by `snort` on `snort0` increases significantly (100% CPU) during the replay at a modest 200 Mbps. You can always login to any of the machines, e.g. **vagrant ssh snort0**. To gain root use **sudo su -**

There are no alerts detected on the traffic replayed by `attacker0` (because we have not define a rule for such traffic)


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'idstools-u2json /var/log/snort/unified2.log'" | grep -v packet | grep '"signature-id": 3000003' | grep '192.168.17.10' | wc -l
```

    0


    WARNING: No alert message map entries loaded.
    WARNING: No classifications loaded.


but the load on `snort0` caused by `attacker0` was sufficient for our snort test alerts from `monitor0` to be missed by `snort0`. Let's quickly check the count of the test alerts, the rate should be "WARNING" or "CRITICAL"


```python
%%bash
! vagrant ssh monitor0 -c "bash ./nagios_plugins/check_prometheus_metric.sh -H localhost:9090 -q \"rate(snort_alert_count{source_ip='192.168.17.20',signature_id='3000003'}[5m]) * 60\" -w 5 -c 4 -n snort-test-alert -m lt -t vector -i"
```

    CRITICAL - snort-test-alert is 3: { blocked: 0, dport_icode: 80, generator_id: 1, instance: snort0:9100, job: node, signature_id: 3000003, source_ip: 192.168.17.20 }


Sometimes people blame `nfqueue` for dropping packets. The sixth column of `/proc/net/netfilter/nfnetlink_queue` reports the number of packets dropped by `nfqueue` - it is zero


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'cat /proc/net/netfilter/nfnetlink_queue'"
```

        0   6961     0 2 65531     0 18229869 24722689  1


It is an interesting subject for a discussion at `snort-users` what are the factors limiting the performance of this setup.

### Pytbull

http://pytbull.sourceforge.net/ is a `python` module which automates scans against `snort`/`suricata` IDS/IPS.


```python
%%bash
vagrant ssh attacker0 -c 'sudo su - -c "yum -d 1 -e 0 -y install mercurial"'
```

    
    ================================================================================
     Package            Arch            Version                 Repository     Size
    ================================================================================
    Installing:
     mercurial          x86_64          2.6.2-6.el7_2           base          2.6 M
    
    Transaction Summary
    ================================================================================
    Install  1 Package
    
    Total download size: 2.6 M
    Installed size: 12 M
    
    Installed:
      mercurial.x86_64 0:2.6.2-6.el7_2                                              
    



```python
%%bash
vagrant ssh attacker0 -c 'sudo su - -c "yum -d 1 -e 0 -y install python-feedparser python-cherrypy nikto hping3 tcpreplay httpd-tools python-paramiko ncrack scapy"'
```

    Package tcpreplay-4.1.2-1.el7.x86_64 already installed and latest version
    Package python-paramiko is obsoleted by python2-paramiko, trying to install python2-paramiko-1.16.1-2.el7.noarch instead
    
    ================================================================================
     Package                Arch        Version                     Repository
                                                                               Size
    ================================================================================
    Installing:
     hping3                 x86_64      0.0.20051105-24.el7         epel       96 k
     httpd-tools            x86_64      2.4.6-45.el7.centos         base       84 k
     ncrack                 x86_64      0.4-0.11.ALPHA.el7          epel      554 k
     nikto                  noarch      1:2.1.5-10.el7              epel      263 k
     python-cherrypy        noarch      3.2.2-4.el7                 base      422 k
     python-feedparser      noarch      5.1.3-3.el7                 epel      107 k
     python2-paramiko       noarch      1.16.1-2.el7                epel      258 k
     scapy                  noarch      2.2.0-2.el7                 epel      489 k
    Installing for dependencies:
     apr                    x86_64      1.4.8-3.el7                 base      103 k
     apr-util               x86_64      1.5.2-6.el7                 base       92 k
     libtomcrypt            x86_64      1.17-23.el7                 epel      224 k
     libtommath             x86_64      0.42.0-4.el7                epel       35 k
     perl-libwhisker2       noarch      2.5-14.el7                  epel       89 k
     python-chardet         noarch      2.2.1-1.el7_1               base      227 k
     python-six             noarch      1.9.0-2.el7                 base       29 k
     python2-crypto         x86_64      2.6.1-13.el7                epel      476 k
     python2-ecdsa          noarch      0.13-4.el7                  epel       83 k
     tcl                    x86_64      1:8.5.13-8.el7              base      1.9 M
    
    Transaction Summary
    ================================================================================
    Install  8 Packages (+10 Dependent packages)
    
    Total download size: 5.4 M
    Installed size: 18 M
    
    Installed:
      hping3.x86_64 0:0.0.20051105-24.el7                                           
      httpd-tools.x86_64 0:2.4.6-45.el7.centos                                      
      ncrack.x86_64 0:0.4-0.11.ALPHA.el7                                            
      nikto.noarch 1:2.1.5-10.el7                                                   
      python-cherrypy.noarch 0:3.2.2-4.el7                                          
      python-feedparser.noarch 0:5.1.3-3.el7                                        
      python2-paramiko.noarch 0:1.16.1-2.el7                                        
      scapy.noarch 0:2.2.0-2.el7                                                    
    
    Dependency Installed:
      apr.x86_64 0:1.4.8-3.el7               apr-util.x86_64 0:1.5.2-6.el7          
      libtomcrypt.x86_64 0:1.17-23.el7       libtommath.x86_64 0:0.42.0-4.el7       
      perl-libwhisker2.noarch 0:2.5-14.el7   python-chardet.noarch 0:2.2.1-1.el7_1  
      python-six.noarch 0:1.9.0-2.el7        python2-crypto.x86_64 0:2.6.1-13.el7   
      python2-ecdsa.noarch 0:0.13-4.el7      tcl.x86_64 1:8.5.13-8.el7              
    



```python
%%bash
vagrant ssh attacker0 -c 'sudo su - -c "hg clone http://pytbull.hg.sourceforge.net:8000/hgroot/pytbull/pytbull"'
```

    destination directory: pytbull
    requesting all changes
    adding changesets
    adding manifests
    adding file changes
    added 17 changesets with 199 changes to 148 files
    updating to branch default
    139 files updated, 0 files merged, 0 files removed, 0 files unresolved



```python
%%bash
vagrant ssh attacker0 -c 'sudo su - -c "cp -f /vagrant/pytbull_config.cfg ~/pytbull/conf/config.cfg"'
```

Let's stop the test alert not to confuse `pytbull`


```python
%%bash
vagrant ssh monitor0 -c "sudo su - -c 'systemctl stop snort-test-alert'"
```

`pytbull` is expecting to have access to `snort0:/var/log/snort/alert_fast.txt` in the `-A fast` format


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'systemctl stop snort@enp0s8'"
```


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c \"sed -i 's/-A unified2/-A fast/' /usr/lib/systemd/system/snort@.service\""
```


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'systemctl daemon-reload'"
```


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c \"sed -i 's/^unified2 =/--unified2 =/' /etc/snort/snort.lua\""
```


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c \"echo alert_fast = { file = true, limit = 128, units = \'M\' } >> /etc/snort/snort.lua\""""
```


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'rm -f /var/log/snort/alert_fast.txt'"
```

Remove our ping drops, as they will fire on some `pytbull` tests


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c \"sed -i '/drop icmp/d' /etc/snort/rules/snort.rules\""
```


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'systemctl start snort@enp0s8'"
```


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'systemctl is-active snort@enp0s8'"
```

    active


Moreover `pytbull` wants an `ftp` server on the `snort0` sensor to access `/var/log/snort/alert_fast.txt`. This is not something one wants on a production sensor


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'yum -d 1 -e 0 -y install vsftpd&& systemctl start vsftpd'"
```

    
    ================================================================================
     Package          Arch             Version                 Repository      Size
    ================================================================================
    Installing:
     vsftpd           x86_64           3.0.2-21.el7            base           169 k
    
    Transaction Summary
    ================================================================================
    Install  1 Package
    
    Total download size: 169 k
    Installed size: 348 k
    
    Installed:
      vsftpd.x86_64 0:3.0.2-21.el7                                                  
    



```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'getent passwd pilou > /dev/null || useradd pilou'"
```


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'echo oopsoops | passwd --stdin pilou'"
```

    Changing password for user pilou.
    passwd: all authentication tokens updated successfully.



```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'chmod go+rx /var/log/snort'"
```


```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'chmod go+r /var/log/snort/alert_fast.txt'"
```

Test whether `snort` is still able to detect the test alert


```python
%%bash
vagrant ssh monitor0 -c "curl -s -m 1 http://snort0/snort-test-alert"
```

    <!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
    <html><head>
    <title>404 Not Found</title>
    </head><body>
    <h1>Not Found</h1>
    <p>The requested URL /snort-test-alert was not found on this server.</p>
    </body></html>



```python
%%bash
vagrant ssh snort0 -c "sudo su - -c 'grep 3000003 /var/log/snort/alert_fast.txt'"
```

    03/05-16:53:10.021496 [**] [1:3000003:1] "snort-test-alert" [**] [Classification: Not Suspicious Traffic] [Priority: 3] {TCP} 192.168.17.20:44622 -> 192.168.17.30:80


Run `pytbull`, it should takes less than 5 minutes


```python
%%bash
vagrant ssh attacker0 -c "sudo su - -c \"cd /root/pytbull; echo -e '1\ny\n' | timeout 720 ./pytbull --debug --offline --mode=gateway -t snort0\""
```

    
    Starting Nmap 6.40 ( http://nmap.org ) at 2017-03-05 16:53 UTC
    Nmap scan report for snort0 (192.168.17.30)
    Host is up (0.00084s latency).
    Not shown: 65530 closed ports
    PORT     STATE SERVICE
    21/tcp   open  ftp
    22/tcp   open  ssh
    80/tcp   open  http
    111/tcp  open  rpcbind
    9100/tcp open  jetdirect
    MAC Address: 08:00:27:00:17:30 (Cadmus Computer Systems)
    
    Nmap done: 1 IP address (1 host up) scanned in 3.36 seconds
    
    Starting Nmap 6.40 ( http://nmap.org ) at 2017-03-05 16:53 UTC
    Nmap scan report for snort0 (192.168.17.30)
    Host is up (0.0089s latency).
    Not shown: 65530 closed ports
    PORT     STATE SERVICE
    21/tcp   open  ftp
    22/tcp   open  ssh
    80/tcp   open  http
    111/tcp  open  rpcbind
    9100/tcp open  jetdirect
    MAC Address: 08:00:27:00:17:30 (Cadmus Computer Systems)
    
    Nmap done: 1 IP address (1 host up) scanned in 5.45 seconds
    - ***** RFIURL is not defined in nikto.conf--no RFI tests will run *****
    - ***** SSL support not available (see docs for SSL install) *****
    - Nikto v2.1.5
    ---------------------------------------------------------------------------
    + Target IP:          192.168.17.30
    + Target Hostname:    snort0
    + Target Port:        80
    + Start Time:         2017-03-05 16:53:48 (GMT0)
    ---------------------------------------------------------------------------
    + Server: Apache/2.4.6 (CentOS)
    + 4197 items checked: 0 error(s) and 0 item(s) reported on remote host
    + End Time:           2017-03-05 16:53:48 (GMT0) (0 seconds)
    ---------------------------------------------------------------------------
    + 1 host(s) tested
    
    Starting Nmap 6.40 ( http://nmap.org ) at 2017-03-05 16:53 UTC
    Nmap scan report for snort0 (192.168.17.30)
    Host is up (0.00035s latency).
    PORT   STATE         SERVICE
    80/tcp open|filtered http
    MAC Address: 08:00:27:00:17:30 (Cadmus Computer Systems)
    
    Nmap done: 1 IP address (1 host up) scanned in 0.23 seconds
    
                                     _   _           _ _
                         _ __  _   _| |_| |__  _   _| | |
                        | '_ \| | | | __| '_ \| | | | | |
                        | |_) | |_| | |_| |_) | |_| | | |
                        | .__/ \__, |\__|_.__/ \__,_|_|_|
                        |_|    |___/
                           Sebastien Damaye, aldeid.com
    
    What would you like to do?
    1. Run a new campaign (will erase previous results)
    2. View results from previous campaign
    3. Exit
    Choose an option: 
    (gateway mode)
    (debug mode)
    (offline)
    
    +------------------------------------------------------------------------+
    | pytbull will set off IDS/IPS alarms and/or other security devices      |
    | and security monitoring software. The user is aware that malicious     |
    | content will be downloaded and that the user should have been          |
    | authorized before running the tool.                                    |
    +------------------------------------------------------------------------+
    Do you accept (y/n)? 
    BASIC CHECKS
    ------------
    Checking root privileges......................................... [   OK   ]
    Checking remote port 21/tcp (FTP)................................ [   OK   ]
    Checking remote port 22/tcp (SSH)................................ [   OK   ]
    Checking remote port 80/tcp (HTTP)............................... [   OK   ]
    Checking path for sudo........................................... [   OK   ]
    Checking path for nmap........................................... [   OK   ]
    Checking path for nikto.......................................... [   OK   ]
    Checking path for niktoconf...................................... [   OK   ]
    Checking path for hping3......................................... [   OK   ]
    Checking path for tcpreplay...................................... [   OK   ]
    Checking path for ab............................................. [   OK   ]
    Checking path for ping........................................... [   OK   ]
    Checking path for ncrack......................................... [   OK   ]
    Removing temporary file.......................................... [   OK   ]
    Cleaning database................................................ [   OK   ]
    
    TESTS
    ------------
    Client Side Attacks.............................................. [   no   ]
    Test Rules....................................................... [   yes  ]
    Bad Traffic...................................................... [   yes  ]
    Fragmented Packets............................................... [   yes  ]
    Brute Force...................................................... [   yes  ]
    Evasion Techniques............................................... [   yes  ]
    ShellCodes....................................................... [   no   ]
    Denial of Service................................................ [   yes  ]
    Pcap Replay...................................................... [   no   ]
    Normal Usage..................................................... [   yes  ]
    IP Reputation.................................................... [   no   ]
    
    
    TEST RULES
    ------------
    TEST #1 - Simple LFI............................................. [  done  ]
    TEST #2 - LFI using NULL byte.................................... [  done  ]
    TEST #3 - Full SYN Scan.......................................... 
    
    ***Debug: sending command: /usr/bin/sudo /usr/bin/nmap -sS -p- snort0
    [  done  ]
    TEST #4 - Full Connect() Scan.................................... 
    
    ***Debug: sending command: /usr/bin/nmap -sT -p- snort0
    [  done  ]
    TEST #5 - SQL Injection.......................................... [  done  ]
    TEST #6 - Netcat Reverse Shell................................... [  done  ]
    TEST #7 - Nikto Scan............................................. 
    
    ***Debug: sending command: /usr/bin/sudo /usr/bin/nikto -config /etc/nikto/config -h snort0 -Plugins cgi
    [  done  ]
    
    BAD TRAFFIC
    ------------
    TEST #8 - Nmap Xmas scan......................................... 
    
    ***Debug: sending command: /usr/bin/sudo /usr/bin/nmap -sX -p 80 snort0
    [  done  ]
    TEST #9 - Malformed Traffic............................................................................
    Starting Ncrack 0.4ALPHA ( http://ncrack.org ) at 2017-03-05 16:54 UTC
    
    
    Ncrack done: 1 service scanned in 9.00 seconds.
    
    Ncrack finished.
    
    Starting Nmap 6.40 ( http://nmap.org ) at 2017-03-05 16:54 UTC
    Nmap scan report for snort0 (192.168.17.30)
    Host is up (0.00045s latency).
    Not shown: 995 closed ports
    PORT     STATE SERVICE    VERSION
    21/tcp   open  ftp        vsftpd 3.0.2
    | ftp-anon: Anonymous FTP login allowed (FTP code 230)
    |_drwxr-xr-x    2 0        0               6 Nov 05 19:43 pub
    22/tcp   open  ssh        OpenSSH 6.6.1 (protocol 2.0)
    | ssh-hostkey: 2048 96:64:3a:9f:65:69:99:6d:5a:2f:c7:16:af:e8:c2:8c (RSA)
    |_256 ae:ef:54:ac:7c:13:15:74:7c:1b:84:70:cd:4d:59:c8 (ECDSA)
    80/tcp   open  http       Apache httpd 2.4.6 ((CentOS))
    | http-methods: Potentially risky methods: TRACE
    |_See http://nmap.org/nsedoc/scripts/http-methods.html
    |_http-title: Apache HTTP Server Test Page powered by CentOS
    111/tcp  open  rpcbind    2-4 (RPC #100000)
    | rpcinfo: 
    |   program version   port/proto  service
    |   100000  2,3,4        111/tcp  rpcbind
    |_  100000  2,3,4        111/udp  rpcbind
    9100/tcp open  jetdirect?
    MAC Address: 08:00:27:00:17:30 (Cadmus Computer Systems)
    No exact OS matches for host (If you know what OS is running on it, see http://nmap.org/submit/ ).
    TCP/IP fingerprint:
    OS:SCAN(V=6.40%E=4%D=3/5%OT=21%CT=1%CU=36370%PV=Y%DS=1%DC=D%G=Y%M=080027%TM
    OS:=58BC42DC%P=x86_64-redhat-linux-gnu)SEQ(SP=102%GCD=1%ISR=10A%TI=Z%TS=A)S
    OS:EQ(SP=102%GCD=1%ISR=10A%TI=Z%II=I%TS=A)OPS(O1=M5B4ST11NW6%O2=M5B4ST11NW6
    OS:%O3=M5B4NNT11NW6%O4=M5B4ST11NW6%O5=M5B4ST11NW6%O6=M5B4ST11)WIN(W1=7120%W
    OS:2=7120%W3=7120%W4=7120%W5=7120%W6=7120)ECN(R=Y%DF=Y%T=40%W=7210%O=M5B4NN
    OS:SNW6%CC=Y%Q=)T1(R=Y%DF=Y%T=40%S=O%A=S+%F=AS%RD=0%Q=)T2(R=N)T3(R=N)T4(R=Y
    OS:%DF=Y%T=40%W=0%S=A%A=Z%F=R%O=%RD=0%Q=)T5(R=Y%DF=Y%T=40%W=0%S=Z%A=S+%F=AR
    OS:%O=%RD=0%Q=)T6(R=Y%DF=Y%T=40%W=0%S=A%A=Z%F=R%O=%RD=0%Q=)T7(R=Y%DF=Y%T=40
    OS:%W=0%S=Z%A=S+%F=AR%O=%RD=0%Q=)U1(R=Y%DF=N%T=40%IPL=164%UN=0%RIPL=G%RID=G
    OS:%RIPCK=G%RUCK=G%RUD=G)IE(R=Y%DFI=N%T=40%CD=S)
    
    Network Distance: 1 hop
    Service Info: OS: Unix
    
    TRACEROUTE
    HOP RTT     ADDRESS
    1   0.45 ms snort0 (192.168.17.30)
    
    OS and Service detection performed. Please report any incorrect results at http://nmap.org/submit/ .
    Nmap done: 1 IP address (1 host up) scanned in 17.91 seconds
    
    Starting Nmap 6.40 ( http://nmap.org ) at 2017-03-05 16:54 UTC
    Nmap scan report for snort0 (192.168.17.30)
    Host is up (0.00050s latency).
    Not shown: 995 closed ports
    PORT     STATE SERVICE    VERSION
    21/tcp   open  ftp        vsftpd 3.0.2
    | ftp-anon: Anonymous FTP login allowed (FTP code 230)
    |_drwxr-xr-x    2 0        0               6 Nov 05 19:43 pub
    22/tcp   open  ssh        OpenSSH 6.6.1 (protocol 2.0)
    | ssh-hostkey: 2048 96:64:3a:9f:65:69:99:6d:5a:2f:c7:16:af:e8:c2:8c (RSA)
    |_256 ae:ef:54:ac:7c:13:15:74:7c:1b:84:70:cd:4d:59:c8 (ECDSA)
    80/tcp   open  http       Apache httpd 2.4.6 ((CentOS))
    | http-methods: Potentially risky methods: TRACE
    |_See http://nmap.org/nsedoc/scripts/http-methods.html
    |_http-title: Apache HTTP Server Test Page powered by CentOS
    111/tcp  open  rpcbind    2-4 (RPC #100000)
    | rpcinfo: 
    |   program version   port/proto  service
    |   100000  2,3,4        111/tcp  rpcbind
    |_  100000  2,3,4        111/udp  rpcbind
    9100/tcp open  jetdirect?
    MAC Address: 08:00:27:00:17:30 (Cadmus Computer Systems)
    No exact OS matches for host (If you know what OS is running on it, see http://nmap.org/submit/ ).
    TCP/IP fingerprint:
    OS:SCAN(V=6.40%E=4%D=3/5%OT=21%CT=1%CU=36087%PV=Y%DS=1%DC=D%G=Y%M=080027%TM
    OS:=58BC42F2%P=x86_64-redhat-linux-gnu)SEQ(SP=103%GCD=1%ISR=101%TI=Z%TS=A)S
    OS:EQ(SP=103%GCD=1%ISR=101%TI=Z%CI=I%TS=A)OPS(O1=M5B4ST11NW6%O2=M5B4ST11NW6
    OS:%O3=M5B4NNT11NW6%O4=M5B4ST11NW6%O5=M5B4ST11NW6%O6=M5B4ST11)WIN(W1=7120%W
    OS:2=7120%W3=7120%W4=7120%W5=7120%W6=7120)ECN(R=Y%DF=Y%T=40%W=7210%O=M5B4NN
    OS:SNW6%CC=Y%Q=)T1(R=Y%DF=Y%T=40%S=O%A=S+%F=AS%RD=0%Q=)T2(R=N)T3(R=N)T4(R=Y
    OS:%DF=Y%T=40%W=0%S=A%A=Z%F=R%O=%RD=0%Q=)T5(R=Y%DF=Y%T=40%W=0%S=Z%A=S+%F=AR
    OS:%O=%RD=0%Q=)T6(R=Y%DF=Y%T=40%W=0%S=A%A=Z%F=R%O=%RD=0%Q=)T7(R=Y%DF=Y%T=40
    OS:%W=0%S=Z%A=S+%F=AR%O=%RD=0%Q=)U1(R=Y%DF=N%T=40%IPL=164%UN=0%RIPL=G%RID=G
    OS:%RIPCK=G%RUCK=G%RUD=G)IE(R=Y%DFI=N%T=40%CD=S)
    
    Network Distance: 1 hop
    Service Info: OS: Unix
    
    TRACEROUTE
    HOP RTT     ADDRESS
    1   0.50 ms snort0 (192.168.17.30)
    
    OS and Service detection performed. Please report any incorrect results at http://nmap.org/submit/ .
    Nmap done: 1 IP address (1 host up) scanned in 17.91 seconds
    
    Starting Nmap 6.40 ( http://nmap.org ) at 2017-03-05 16:55 UTC
    Nmap scan report for snort0 (192.168.17.30)
    Host is up (0.00043s latency).
    Not shown: 995 closed ports
    PORT     STATE SERVICE    VERSION
    21/tcp   open  ftp        vsftpd 3.0.2
    | ftp-anon: Anonymous FTP login allowed (FTP code 230)
    |_drwxr-xr-x    2 0        0               6 Nov 05 19:43 pub
    22/tcp   open  ssh        OpenSSH 6.6.1 (protocol 2.0)
    | ssh-hostkey: 2048 96:64:3a:9f:65:69:99:6d:5a:2f:c7:16:af:e8:c2:8c (RSA)
    |_256 ae:ef:54:ac:7c:13:15:74:7c:1b:84:70:cd:4d:59:c8 (ECDSA)
    80/tcp   open  http       Apache httpd 2.4.6 ((CentOS))
    | http-methods: Potentially risky methods: TRACE
    |_See http://nmap.org/nsedoc/scripts/http-methods.html
    |_http-title: Apache HTTP Server Test Page powered by CentOS
    111/tcp  open  rpcbind    2-4 (RPC #100000)
    | rpcinfo: 
    |   program version   port/proto  service
    |   100000  2,3,4        111/tcp  rpcbind
    |_  100000  2,3,4        111/udp  rpcbind
    9100/tcp open  jetdirect?
    MAC Address: 08:00:27:00:17:30 (Cadmus Computer Systems)
    No exact OS matches for host (If you know what OS is running on it, see http://nmap.org/submit/ ).
    TCP/IP fingerprint:
    OS:SCAN(V=6.40%E=4%D=3/5%OT=21%CT=1%CU=43113%PV=Y%DS=1%DC=D%G=Y%M=080027%TM
    OS:=58BC430C%P=x86_64-redhat-linux-gnu)SEQ(SP=103%GCD=1%ISR=10A%TI=Z%II=I%T
    OS:S=A)SEQ(SP=103%GCD=1%ISR=10A%TI=Z%TS=A)SEQ(SP=103%GCD=1%ISR=10A%TI=Z%CI=
    OS:I%TS=A)OPS(O1=M5B4ST11NW6%O2=M5B4ST11NW6%O3=M5B4NNT11NW6%O4=M5B4ST11NW6%
    OS:O5=M5B4ST11NW6%O6=M5B4ST11)WIN(W1=7120%W2=7120%W3=7120%W4=7120%W5=7120%W
    OS:6=7120)ECN(R=Y%DF=Y%T=40%W=7210%O=M5B4NNSNW6%CC=Y%Q=)T1(R=Y%DF=Y%T=40%S=
    OS:O%A=S+%F=AS%RD=0%Q=)T2(R=N)T3(R=N)T4(R=Y%DF=Y%T=40%W=0%S=A%A=Z%F=R%O=%RD
    OS:=0%Q=)T5(R=Y%DF=Y%T=40%W=0%S=Z%A=S+%F=AR%O=%RD=0%Q=)T6(R=Y%DF=Y%T=40%W=0
    OS:%S=A%A=Z%F=R%O=%RD=0%Q=)T7(R=Y%DF=Y%T=40%W=0%S=Z%A=S+%F=AR%O=%RD=0%Q=)U1
    OS:(R=Y%DF=N%T=40%IPL=164%UN=0%RIPL=G%RID=G%RIPCK=G%RUCK=G%RUD=G)IE(R=Y%DFI
    OS:=N%T=40%CD=S)
    
    Network Distance: 1 hop
    Service Info: OS: Unix
    
    TRACEROUTE
    HOP RTT     ADDRESS
    1   0.43 ms snort0 (192.168.17.30)
    
    OS and Service detection performed. Please report any incorrect results at http://nmap.org/submit/ .
    Nmap done: 1 IP address (1 host up) scanned in 17.93 seconds
    - ***** RFIURL is not defined in nikto.conf--no RFI tests will run *****
    - ***** SSL support not available (see docs for SSL install) *****
    - Nikto v2.1.5
    ---------------------------------------------------------------------------
    + Target IP:          192.168.17.30
    + Target Hostname:    snort0
    + Target Port:        80
    + Using Encoding:     Random URI encoding (non-UTF8)
    + Start Time:         2017-03-05 16:55:44 (GMT0)
    ---------------------------------------------------------------------------
    + Server: Apache/2.4.6 (CentOS)
    + 4197 items checked: 0 error(s) and 0 item(s) reported on remote host
    + End Time:           2017-03-05 16:55:45 (GMT0) (1 seconds)
    ---------------------------------------------------------------------------
    + 1 host(s) tested
    - ***** RFIURL is not defined in nikto.conf--no RFI tests will run *****
    - ***** SSL support not available (see docs for SSL install) *****
    - Nikto v2.1.5
    ---------------------------------------------------------------------------
    + Target IP:          192.168.17.30
    + Target Hostname:    snort0
    + Target Port:        80
    + Using Encoding:     Directory self-reference (/./)
    + Start Time:         2017-03-05 16:55:49 (GMT0)
    ---------------------------------------------------------------------------
    + Server: Apache/2.4.6 (CentOS)
    + 4197 items checked: 0 error(s) and 0 item(s) reported on remote host
    + End Time:           2017-03-05 16:55:49 (GMT0) (0 seconds)
    ---------------------------------------------------------------------------
    + 1 host(s) tested
    - ***** RFIURL is not defined in nikto.conf--no RFI tests will run *****
    - ***** SSL support not available (see docs for SSL install) *****
    - Nikto v2.1.5
    ---------------------------------------------------------------------------
    + Target IP:          192.168.17.30
    + Target Hostname:    snort0
    + Target Port:        80
    + Using Encoding:     Premature URL ending
    + Start Time:         2017-03-05 16:55:53 (GMT0)
    ---------------------------------------------------------------------------
    + Server: Apache/2.4.6 (CentOS)
    + 4197 items checked: 0 error(s) and 0 item(s) reported on remote host
    + End Time:           2017-03-05 16:55:54 (GMT0) (1 seconds)
    ---------------------------------------------------------------------------
    + 1 host(s) tested
    - ***** RFIURL is not defined in nikto.conf--no RFI tests will run *****
    - ***** SSL support not available (see docs for SSL install) *****
    - Nikto v2.1.5
    ---------------------------------------------------------------------------
    + Target IP:          192.168.17.30
    + Target Hostname:    snort0
    + Target Port:        80
    + Using Encoding:     Prepend long random string
    + Start Time:         2017-03-05 16:55:58 (GMT0)
    ---------------------------------------------------------------------------
    + Server: Apache/2.4.6 (CentOS)
    + 4197 items checked: 0 error(s) and 0 item(s) reported on remote host
    + End Time:           2017-03-05 16:55:58 (GMT0) (0 seconds)
    ---------------------------------------------------------------------------
    + 1 host(s) tested
    - ***** RFIURL is not defined in nikto.conf--no RFI tests will run *****
    - ***** SSL support not available (see docs for SSL install) *****
    - Nikto v2.1.5
    ---------------------------------------------------------------------------
    + Target IP:          192.168.17.30
    + Target Hostname:    snort0
    + Target Port:        80
    + Using Encoding:     Fake parameter
    + Start Time:         2017-03-05 16:56:02 (GMT0)
    ---------------------------------------------------------------------------
    + Server: Apache/2.4.6 (CentOS)
    + 4197 items checked: 0 error(s) and 0 item(s) reported on remote host
    + End Time:           2017-03-05 16:56:02 (GMT0) (0 seconds)
    ---------------------------------------------------------------------------
    + 1 host(s) tested
    - ***** RFIURL is not defined in nikto.conf--no RFI tests will run *****
    - ***** SSL support not available (see docs for SSL install) *****
    - Nikto v2.1.5
    ---------------------------------------------------------------------------
    + Target IP:          192.168.17.30
    + Target Hostname:    snort0
    + Target Port:        80
    + Using Encoding:     TAB as request spacer
    + Start Time:         2017-03-05 16:56:07 (GMT0)
    ---------------------------------------------------------------------------
    + Server: Apache/2.4.6 (CentOS)
    + 4197 items checked: 0 error(s) and 0 item(s) reported on remote host
    + End Time:           2017-03-05 16:56:07 (GMT0) (0 seconds)
    ---------------------------------------------------------------------------
    + 1 host(s) tested
    - ***** RFIURL is not defined in nikto.conf--no RFI tests will run *****
    - ***** SSL support not available (see docs for SSL install) *****
    - Nikto v2.1.5
    ---------------------------------------------------------------------------
    + Target IP:          192.168.17.30
    + Target Hostname:    snort0
    + Target Port:        80
    + Using Encoding:     Change the case of the URL
    + Start Time:         2017-03-05 16:56:11 (GMT0)
    ---------------------------------------------------------------------------
    + Server: Apache/2.4.6 (CentOS)
    + 4197 items checked: 0 error(s) and 0 item(s) reported on remote host
    + End Time:           2017-03-05 16:56:11 (GMT0) (0 seconds)
    ---------------------------------------------------------------------------
    + 1 host(s) tested
    - ***** RFIURL is not defined in nikto.conf--no RFI tests will run *****
    - ***** SSL support not available (see docs for SSL install) *****
    - Nikto v2.1.5
    ---------------------------------------------------------------------------
    + Target IP:          192.168.17.30
    + Target Hostname:    snort0
    + Target Port:        80
    + Using Encoding:     Use Windows directory separator (\)
    + Start Time:         2017-03-05 16:56:16 (GMT0)
    ---------------------------------------------------------------------------
    + Server: Apache/2.4.6 (CentOS)
    + 4197 items checked: 0 error(s) and 0 item(s) reported on remote host
    + End Time:           2017-03-05 16:56:16 (GMT0) (0 seconds)
    ---------------------------------------------------------------------------
    + 1 host(s) tested
    - ***** RFIURL is not defined in nikto.conf--no RFI tests will run *****
    - ***** SSL support not available (see docs for SSL install) *****
    - Nikto v2.1.5
    ---------------------------------------------------------------------------
    + Target IP:          192.168.17.30
    + Target Hostname:    snort0
    + Target Port:        80
    + Start Time:         2017-03-05 16:56:20 (GMT0)
    ---------------------------------------------------------------------------
    + Server: Apache/2.4.6 (CentOS)
    + 4197 items checked: 0 error(s) and 0 item(s) reported on remote host
    + End Time:           2017-03-05 16:56:20 (GMT0) (0 seconds)
    ---------------------------------------------------------------------------
    + 1 host(s) tested
    - ***** RFIURL is not defined in nikto.conf--no RFI tests will run *****
    - ***** SSL support not available (see docs for SSL install) *****
    - Nikto v2.1.5
    ---------------------------------------------------------------------------
    + Target IP:          192.168.17.30
    + Target Hostname:    snort0
    + Target Port:        80
    + Start Time:         2017-03-05 16:56:24 (GMT0)
    ---------------------------------------------------------------------------
    + Server: Apache/2.4.6 (CentOS)
    + 4197 items checked: 0 error(s) and 0 item(s) reported on remote host
    + End Time:           2017-03-05 16:56:25 (GMT0) (1 seconds)
    ---------------------------------------------------------------------------
    + 1 host(s) tested
    ........ 
    
    ***Debug: sending scapy payload: send(IP(dst="snort0", ihl=2, version=3)/ICMP(), verbose=0)
    
    Sent 1 packets.
    [  done  ]
    TEST #10 - Land Attack........................................... 
    
    ***Debug: sending scapy payload: send(IP(src="snort0",dst="snort0")/TCP(sport=135,dport=135), verbose=0)
    
    Sent 1 packets.
    [  done  ]
    
    FRAGMENTED PACKETS
    ------------
    TEST #11 - Ping of death......................................... 
    
    ***Debug: sending scapy payload: send(fragment(IP(dst="snort0")/ICMP()/("X"*60000)), verbose=0)
    
    Sent 41 packets.
    [  done  ]
    TEST #12 - Nestea Attack 1/3..................................... 
    
    ***Debug: sending scapy payload: send(IP(dst="snort0", id=42, flags="MF")/UDP()/("X"*10), verbose=0)
    
    Sent 1 packets.
    [  done  ]
    TEST #13 - Nestea Attack 2/3..................................... 
    
    ***Debug: sending scapy payload: send(IP(dst="snort0", id=42, frag=48)/("X"*116), verbose=0)
    
    Sent 1 packets.
    [  done  ]
    TEST #14 - Nestea Attack 3/3..................................... 
    
    ***Debug: sending scapy payload: send(IP(dst="snort0", id=42, flags="MF")/UDP()/("X"*224), verbose=0)
    
    Sent 1 packets.
    [  done  ]
    
    BRUTE FORCE
    ------------
    TEST #15 - Bruteforce against FTP with ncrack.................... 
    
    ***Debug: sending command: /usr/bin/ncrack -f -U data/ncrack-users.txt -P data/ncrack-passwords.txt snort0:21
    [  done  ]
    
    EVASION TECHNIQUES
    ------------
    TEST #16 - Nmap decoy test (6th position)........................ 
    
    ***Debug: sending command: /usr/bin/sudo /usr/bin/nmap -sS -A -D 192.168.100.1,192.168.100.2,192.168.100.3,192.168.100.4,192.168.100.5,ME snort0
    [  done  ]
    TEST #17 - Nmap decoy test (7th position)........................ 
    
    ***Debug: sending command: /usr/bin/sudo /usr/bin/nmap -sS -A -D 192.168.100.1,192.168.100.2,192.168.100.3,192.168.100.4,192.168.100.5,192.168.100.6,ME snort0
    [  done  ]
    TEST #18 - Hex encoding.......................................... [  done  ]
    TEST #19 - Nmap scan with fragmentation.......................... 
    
    ***Debug: sending command: /usr/bin/sudo /usr/bin/nmap -PN -sS -A -f snort0
    [  done  ]
    TEST #20 - Nikto Random URI encoding............................. 
    
    ***Debug: sending command: /usr/bin/sudo /usr/bin/nikto -config /etc/nikto/config -h snort0 -Plugins cgi -evasion 1
    [  done  ]
    TEST #21 - Nikto Directory self reference........................ 
    
    ***Debug: sending command: /usr/bin/sudo /usr/bin/nikto -config /etc/nikto/config -h snort0 -Plugins cgi -evasion 2
    [  done  ]
    TEST #22 - Nikto Premature URL ending............................ 
    
    ***Debug: sending command: /usr/bin/sudo /usr/bin/nikto -config /etc/nikto/config -h snort0 -Plugins cgi -evasion 3
    [  done  ]
    TEST #23 - Nikto Prepend long random string...................... 
    
    ***Debug: sending command: /usr/bin/sudo /usr/bin/nikto -config /etc/nikto/config -h snort0 -Plugins cgi -evasion 4
    [  done  ]
    TEST #24 - Nikto Fake parameter.................................. 
    
    ***Debug: sending command: /usr/bin/sudo /usr/bin/nikto -config /etc/nikto/config -h snort0 -Plugins cgi -evasion 5
    [  done  ]
    TEST #25 - Nikto TAB as request spacer........................... 
    
    ***Debug: sending command: /usr/bin/sudo /usr/bin/nikto -config /etc/nikto/config -h snort0 -Plugins cgi -evasion 6
    [  done  ]
    TEST #26 - Nikto Change the case of the URL...................... 
    
    ***Debug: sending command: /usr/bin/sudo /usr/bin/nikto -config /etc/nikto/config -h snort0 -Plugins cgi -evasion 7
    [  done  ]
    TEST #27 - Nikto Windows directory separator..................... 
    
    ***Debug: sending command: /usr/bin/sudo /usr/bin/nikto -config /etc/nikto/config -h snort0 -Plugins cgi -evasion 8
    [  done  ]
    TEST #28 - Nikto Carriage return as request spacer............... 
    
    ***Debug: sending command: /usr/bin/sudo /usr/bin/nikto -config /etc/nikto/config -h snort0 -Plugins cgi -evasion A
    [  done  ]
    TEST #29 - Nikto Binary value as request spacer.................. 
    
    ***Debug: sending command: /usr/bin/sudo /usr/bin/nikto -config /etc/nikto/config -h snort0 -Plugins cgi -evasion B
    [  done  ]
    TEST #30 - Javascript Obfuscation.............................This is ApacheBench, Version 2.3 <$Revision: 1430300 $>
    Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
    Licensed to The Apache Software Foundation, http://www.apache.org/
    
    Benchmarking %target% (be patient)
    HPING snort0 (enp0s8 192.168.17.30): S set, 40 headers + 0 data bytes
    This is ApacheBench, Version 2.3 <$Revision: 1430300 $>
    Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
    Licensed to The Apache Software Foundation, http://www.apache.org/
    
    Benchmarking %target% (be patient)...PING snort0 (192.168.17.30) 56(84) bytes of data.
    64 bytes from snort0 (192.168.17.30): icmp_seq=1 ttl=64 time=0.353 ms
    
    --- snort0 ping statistics ---
    1 packets transmitted, 1 received, 0% packet loss, time 0ms
    rtt min/avg/max/mdev = 0.353/0.353/0.353/0.000 ms
    ... [  done  ]
    
    DENIAL OF SERVICE
    ------------
    TEST #31 - DoS against MSSQL..................................... 
    
    ***Debug: sending scapy payload: sr1(IP(dst="snort0")/TCP(dport=1433)/"0"*1000, verbose=0)
    
    Received 1001 packets, got 1000 answers, remaining 0 packets
    [  done  ]
    TEST #32 - ApacheBench DoS....................................... 
    
    ***Debug: sending command: /usr/bin/ab -k -c 25 -n 10000 http://%target%/
    [  done  ]
    TEST #33 - hping SYN flood....................................... 
    
    ***Debug: sending command: /usr/bin/sudo /usr/sbin/hping3 snort0 -S --faster -p 80 -I enp0s8 -c 50000 -a 1.2.3.4
    [  done  ]
    
    NORMAL USAGE
    ------------
    TEST #34 - ApacheBench 10 requests............................... 
    
    ***Debug: sending command: /usr/bin/ab -k -c 10 -n 10 http://%target%/
    [  done  ]
    TEST #35 - Standard ping......................................... 
    
    ***Debug: sending command: /usr/bin/ping -c 1 snort0
    [  done  ]
    
    
    -----------------------
    DONE. Check the report.
    -----------------------
    
    
    Webserver started at http://127.0.0.1:8080
    (use ^C to stop)
    


    WARNING: No route found for IPv6 destination :: (no default route?)
    apr_sockaddr_info_get() for %target%: Name or service not known (670002)
    
    --- snort0 hping statistic ---
    50000 packets transmitted, 0 packets received, 100% packet loss
    round-trip min/avg/max = 0.0/0.0/0.0 ms
    apr_sockaddr_info_get() for %target%: Name or service not known (670002)
    [05/Mar/2017:16:56:58] ENGINE Listening for SIGHUP.
    [05/Mar/2017:16:56:58] ENGINE Listening for SIGTERM.
    [05/Mar/2017:16:56:58] ENGINE Listening for SIGUSR1.
    [05/Mar/2017:16:56:58] ENGINE Bus STARTING
    [05/Mar/2017:16:56:58] ENGINE Started monitor thread '_TimeoutMonitor'.
    [05/Mar/2017:16:56:58] ENGINE Serving on 127.0.0.1:8080
    [05/Mar/2017:16:56:58] ENGINE Bus STARTED
    [05/Mar/2017:17:05:15] ENGINE Caught signal SIGTERM.
    [05/Mar/2017:17:05:15] ENGINE Bus STOPPING
    [05/Mar/2017:17:05:15] ENGINE HTTP Server cherrypy._cpwsgi_server.CPWSGIServer(('127.0.0.1', 8080)) shut down
    [05/Mar/2017:17:05:15] ENGINE Stopped thread '_TimeoutMonitor'.
    [05/Mar/2017:17:05:15] ENGINE Bus STOPPED
    [05/Mar/2017:17:05:15] ENGINE Bus EXITING
    [05/Mar/2017:17:05:15] ENGINE Bus EXITED
    [05/Mar/2017:17:05:15] ENGINE Waiting for child threads to terminate...


`pytbull` starts a web server and exposes a summary of the scan as html, but in this setup it finds no
alerts are triggered, apart from PSNG_TCP_PORTSCAN. Something is not right here, it is due to several reasons:
 
- the rules alerting on preprocessors are not enabled in `snort` by default. They are available from snortrules-snapshot-*.tar.gz.

- no rules specific for the tests performed by `pytbull` are enabled

- the scanners manage to evade IDS/IPS "Black Hat USA 2013 - Evading deep inspection for fun and shell" https://www.youtube.com/watch?v=BkmPZhgLmRo

# Versions


```python
%%bash
vagrant ssh snort0 -c 'rpm -q snort snort-extra daq'
```

    snort-3.0.0-0.227.a4.el7.centos.x86_64
    snort-extra-1.0.0-0.227.a4.el7.centos.x86_64
    daq-2.2.1-1.el7.centos.x86_64



```python
%%bash
vagrant --version
VBoxManage --version
cat /etc/os-release | grep PRETTY_NAME
uname -a
```

    Vagrant 1.8.6
    5.1.14r112924
    PRETTY_NAME="Ubuntu 16.04.2 LTS"
    Linux ubuntu 4.4.0-45-generic #66-Ubuntu SMP Wed Oct 19 14:12:37 UTC 2016 x86_64 x86_64 x86_64 GNU/Linux


# When done, destroy the test machines


```python
%%bash
vagrant destroy -f
```

# License

BSD 2-clause
