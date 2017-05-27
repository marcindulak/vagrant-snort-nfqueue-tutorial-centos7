%global real_name snort
%global github_name snort3
%global user_name snort

%global release_phase a4
%global release_build 232
# build github commit if release_commit is defined
%global github 1
%global release_commit e458ab19878d1627ac7c6474ebc24e1867475498
%global use_hash_in_name 0

Name:		snort
Version:	3.0.0
Summary:	An open source Network Intrusion Detection System (NIDS)
%if 0%{?github}
%if 0%{?use_hash_in_name}
Release:	0.%%{release_commit}%%{?dist}
%else
Release:	0.%{release_build}.%{release_phase}%{?dist}
%endif
%else
Release:	0.%{release_build}.%{release_phase}%{?dist}
%endif
License:	GPLv2 and BSD
Url:		http://www.snort.org/
%if 0%{?github}
Source0:	https://github.com/snortadmin/%{github_name}/archive/%{release_commit}.tar.gz#/%{github_name}-%{release_commit}.tar.gz
%else
Source0:	https://www.snort.org/downloads/snortplus/%{real_name}-%{version}-%{release_phase}-%{release_build}-auto.tar.gz
%endif
Source1:	%{real_name}.service
Conflicts:	snort < 3.0.0

BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libtool
BuildRequires:	pcre-devel
BuildRequires:	libpcap-devel
BuildRequires:	bison
BuildRequires:	libdnet-devel
BuildRequires:	xz-devel
BuildRequires:	flex

BuildRequires:	systemd-units
BuildRequires:	gcc-c++
BuildRequires:	hwloc-devel
BuildRequires:	luajit-devel
BuildRequires:	zlib-devel
BuildRequires:	openssl-devel
BuildRequires:	daq-devel >= 2.2.1

Requires:	daq-modules >= 2.2.1
Requires:	ethtool
Requires:	pkgconfig


# handle license on el{6,7}: global must be defined after the License field above
%{!?_licensedir: %global license %doc}


%description
Snort is the most powerful IPS in the world, setting the standard for \
intrusion detection.  So when we started thinking about what the next \
generation of IPS looked like we started from scratch. 


%prep
%if 0%{?github}
%autosetup -n %{github_name}-%{release_commit}
%else
%autosetup -n %{real_name}-%{version}-%{release_phase}
%endif
autoreconf -isvf


%build
%{_configure}	--prefix=%{_prefix} \
		--exec_prefix=%{_prefix} \
		--libdir=%{_libdir} \
		--sysconfdir=%{_sysconfdir} \
		--docdir=%{_datadir}/doc/%{name}-%{version} \
		--disable-static-daq \
		--enable-debug-msgs --enable-debug


%install
export CFLAGS="$RPM_OPT_FLAGS"
export AM_CFLAGS="$RPM_OPT_FLAGS"
make %{?_smp_mflags} install \
		prefix=$RPM_BUILD_ROOT%{_prefix} \
		exec_prefix=$RPM_BUILD_ROOT%{_exec_prefix} \
		libdir=$RPM_BUILD_ROOT%{_libdir} \
		sysconfdir=$RPM_BUILD_ROOT%{_sysconfdir} \
		docdir=$RPM_BUILD_ROOT%{_datadir}/doc/%{name}-%{version}

# get rid of la files
find $RPM_BUILD_ROOT -type f -name "*.la" -delete -print

# snort in /usr/sbin
mkdir -p $RPM_BUILD_ROOT%{_sbindir}
mv -v $RPM_BUILD_ROOT%{_bindir}/%{real_name} $RPM_BUILD_ROOT%{_sbindir}/%{real_name}

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/%{real_name}/rules
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/log/%{real_name}
mkdir -p $RPM_BUILD_ROOT%{_unitdir}
install -p -m 644 %{SOURCE1} $RPM_BUILD_ROOT%{_unitdir}/%{real_name}@.service
sed -i 's|LIBDIR|%{_libdir}|' $RPM_BUILD_ROOT%{_unitdir}/%{real_name}@.service


%pre
# Don't do all this stuff if we are upgrading
if [ $1 = 1 ] ; then
getent group %{user_name} > /dev/null || groupadd -r %{user_name}
getent passwd %{user_name} > /dev/null || \
       useradd -r -d %{_localstatedir}/log/%{user_name} -g %{user_name} \
       -s /sbin/nologin -c "%{user_name}" %{user_name}
fi

%post
%systemd_post snort@service

%preun
%systemd_preun snort@service

%postun
%systemd_postun snort@service

# Only do this if we are actually removing %%{user_name}
if [ $1 = 0 ] ; then
      getent passwd %{user_name} > /dev/null && userdel %{user_name}
      getent group %{user_name} > /dev/null && groupdel %{user_name} || :
fi


%files
%{_sbindir}/%{real_name}
%{_bindir}/%{real_name}2lua
%{_bindir}/u2boat
%{_bindir}/u2spewfoo
%dir %{_sysconfdir}/%{real_name}
%dir %{_sysconfdir}/%{real_name}/rules
%dir %{_libdir}/%{real_name}
%dir %{_libdir}/%{real_name}/daqs
%{_libdir}/%{real_name}/daqs/daq_file.so
%{_libdir}/%{real_name}/daqs/daq_hext.so
%{_libdir}/pkgconfig/%{real_name}.pc
%config(noreplace) %{_sysconfdir}/%{real_name}/sample.rules
%config(noreplace) %{_sysconfdir}/%{real_name}/file_magic.lua
%config(noreplace) %{_sysconfdir}/%{real_name}/%{real_name}_defaults.lua
%config(noreplace) %{_sysconfdir}/%{real_name}/%{real_name}.lua
%{_includedir}/%{real_name}
%attr(700,%{user_name},%{user_name}) %dir %{_localstatedir}/log/%{user_name}
%{_unitdir}/%{real_name}@.service
%doc README.md
%license COPYING LICENSE


%changelog
* Wed May 03 2017 Marcin Dulak <Marcin.Dulak@gmail.com> - 3.0.0-0.a4.232
- upstream update

* Mon Feb 06 2017 Marcin Dulak <Marcin.Dulak@gmail.com> - 3.0.0-0.a4.225
- initial version, based on snort.spec from snort.org

