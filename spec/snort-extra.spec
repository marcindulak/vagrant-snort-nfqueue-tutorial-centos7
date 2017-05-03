%global real_name snort_extra
%global github_name snort3
%global user_name snort

%global release_phase a4
%global release_build 232
# build github commit if release_commit is defined
%global github 1
%global release_commit e458ab19878d1627ac7c6474ebc24e1867475498
%global use_hash_in_name 0

Name:		snort-extra
Version:	1.0.0
Summary:	Snort Extras
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
Source0:	https://github.com/snortadmin/%{real_name}/archive/%{commit0}.tar.gz#/%{github_name}-%{release_commit}.tar.gz
%else
Source0:	https://www.snort.org/downloads/snortplus/%{real_name}-%{version}-%{release_phase}-%{release_build}-auto.tar.gz
%endif

BuildRequires:	autoconf
BuildRequires:	autoconf-archive
BuildRequires:	automake
BuildRequires:	libtool

BuildRequires:	gcc-c++
BuildRequires:	zlib-devel
BuildRequires:	daq-devel

BuildRequires:	snort >= 3.0.0


# handle license on el{6,7}: global must be defined after the License field above
%{!?_licensedir: %global license %doc}


%description
Snort is all about plugins. \
It has over 200 by default and makes it easy to add more in C++ or LuaJIT.


%prep
%if 0%{?github}
%autosetup -n %{github_name}-%{release_commit}
mv extra .extra
rm -rf *
mv .extra/* .
rm -f .extra/.gitignore
rmdir .extra
%else
%autosetup -n %{real_name}-%{version}-%{release_phase}
%endif
autoreconf -isvf


%build
%{_configure} --prefix=%{_prefix} --libdir=%{_libdir}


%install
export CFLAGS="$RPM_OPT_FLAGS"
export AM_CFLAGS="$RPM_OPT_FLAGS"
make %{?_smp_mflags} install prefix=$RPM_BUILD_ROOT%{_prefix} libdir=$RPM_BUILD_ROOT%{_libdir}

# get rid of la files
find $RPM_BUILD_ROOT -type f -name "*.la" -delete -print


%files
%dir %{_libdir}/%{real_name}
%{_libdir}/%{real_name}/codecs
%{_libdir}/%{real_name}/daqs
%{_libdir}/%{real_name}/inspectors
%{_libdir}/%{real_name}/ips_options
%{_libdir}/%{real_name}/loggers
%{_libdir}/%{real_name}/search_engines
%{_libdir}/%{real_name}/so_rules
%doc README
%license COPYING LICENSE


%changelog
* Wed May 03 2017 Marcin Dulak <Marcin.Dulak@gmail.com> - 1.0.0-0.a4.232
- upstream update

* Mon Feb 06 2017 Marcin Dulak <Marcin.Dulak@gmail.com> - 1.0.0-0.a4.225
- initial version

