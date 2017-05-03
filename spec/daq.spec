%global upstream_name libdaq

Summary:	Data Acquisition Library
Name:		daq
Version:	2.2.1
Release:	1%{?dist}
License:	GPLv2
URL:		https://github.com/Xiche/%{upstream_name}
Source0:	https://github.com/Xiche/%{upstream_name}/archive/v%{version}.tar.gz#/%{upstream_name}-%{version}.tar.gz
Conflicts:	daq < 2.2.1

BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	libtool
BuildRequires:	libdnet-devel
BuildRequires:	libnetfilter_queue-devel
BuildRequires:	libpcap-devel

# handle license on el{6,7}: global must be defined after the License field above
%{!?_licensedir: %global license %doc}


%description
Snort 2.9 introduces the DAQ, or Data Acquisition library, for packet I/O.  The
DAQ replaces direct calls to libpcap functions with an abstraction layer that
facilitates operation on a variety of hardware and software interfaces without
requiring changes to Snort.


%package modules
Summary:	Dynamic DAQ modules

%description modules
Dynamic DAQ modules.


%package modules-static
Summary:	Static DAQ modules
Requires:	%{name}-modules%{?_isa} = %{version}-%{release}

%description modules-static
Static DAQ modules.


%package devel
Summary:	Development libraries and headers for %{name}
Requires:	%{name}%{?_isa} = %{version}-%{release}

%description devel
Development libraries and headers for %{name}.


%package static
Summary:	Static development libraries for %{name}
Requires:	%{name}-devel%{?_isa} = %{version}-%{release}

%description static
Static development libraries for %{name}.


%prep
%autosetup -n %{upstream_name}-%{version}
autoreconf -i


%build
# how to get rid of rpath - neither configure option or sed on libtool works?
%{_configure} --libdir=%{_libdir} --disable-rpath
%{__sed} -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
%{__sed} -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
%{__make} %{?_smp_mflags}


%install
%{__make} install prefix=$RPM_BUILD_ROOT/%{_prefix} exec_prefix=$RPM_BUILD_ROOT/%{_exec_prefix} libdir=$RPM_BUILD_ROOT/%{_libdir}
# get rid of la files
find $RPM_BUILD_ROOT -type f -name "*.la" -delete -print
# move libdaq_static_modules.a where is belongs
mv -v $RPM_BUILD_ROOT/%{_libdir}/libdaq_static_modules.a $RPM_BUILD_ROOT/%{_libdir}/%{name}


%post -n %{name} -p /sbin/ldconfig
%postun -n %{name} -p /sbin/ldconfig


%post -n %{name}-devel -p /sbin/ldconfig
%postun -n %{name}-devel -p /sbin/ldconfig


%files
%{_libdir}/libdaq.so.4
%{_libdir}/libdaq.so.4.0.1
%{_libdir}/libsfbpf.so.0
%{_libdir}/libsfbpf.so.0.0.1
%doc ChangeLog README
%license COPYING LICENSE


%files devel
%{_bindir}/daq-modules-config
%{_includedir}/daq.h
%{_includedir}/daq_api.h
%{_includedir}/daq_common.h
%{_includedir}/sfbpf.h
%{_includedir}/sfbpf_dlt.h
%{_libdir}/libdaq.so
%{_libdir}/libsfbpf.so
%license COPYING LICENSE


%files static
%{_libdir}/libdaq.a
%{_libdir}/libdaq_static.a
%{_libdir}/libsfbpf.a
%license COPYING LICENSE


%files modules
%dir %{_libdir}/%{name}
%{_libdir}/%{name}/daq_afpacket.so
%{_libdir}/%{name}/daq_dump.so
%{_libdir}/%{name}/daq_nfq.so
%{_libdir}/%{name}/daq_ipfw.so
%{_libdir}/%{name}/daq_pcap.so
%license COPYING LICENSE


%files modules-static
%{_libdir}/%{name}/libdaq_static_modules.a
%license COPYING LICENSE


%changelog
* Sat Nov 12 2016 Marcin Dulak <Marcin.Dulak@gmail.com> - 2.2.1-1
- initial version, based on Lawrence R. Rogers's daq.spec from forensics.cert.org
