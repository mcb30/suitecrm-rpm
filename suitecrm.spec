Name:		suitecrm
Version:	7.11.13
Release:	1%{?dist}
Summary:	SuiteCRM Customer Relationship Management
License:	Affero GPLv3
URL:		https://suitecrm.com/
Source0:	https://suitecrm.com/files/162/SuiteCRM-7.11/500/SuiteCRM-%{version}.zip
Source1:	%{name}-sysusers.conf
Source2:	%{name}-scheduler.service
Source3:	%{name}-scheduler.timer
Source4:	%{name}-fpm.conf
Source5:	%{name}-httpd.conf
Source6:	%{name}-config.php
BuildArch:	noarch
BuildRequires:	findutils
BuildRequires:	sed
BuildRequires:	systemd
Requires:	httpd-filesystem
Requires:	nginx-filesystem
Requires:	phpturd
Requires:	php-cli
Requires:	php-curl
Requires:	php-fpm
Requires:	php-gd
Requires:	php-imap
Requires:	php-json
Requires:	php-mysqlnd
Requires:	php-pcre
Requires:	php-xml
Requires:	php-zip
Requires:	php-zlib

%description
SuiteCRM is an open source Customer Relationship Management (CRM)
application written in PHP.

%prep
%autosetup -n SuiteCRM-%{version}

%build

# SuiteCRM includes an ELF executable committed to the source tree.
# Kill it with fire.
#
rm -f include/SuiteGraphs/rgraph/scripts/jsmin

# The SuiteCRM make_writable() function is an abomination from the
# depths of hell that brings ten thousand years of shame upon its
# author.  Disembowel it gently with a railgun.
#
sed -i -E "/^function make_writable/,/^}/c \
function make_writable(\$file) {\n\
  # This code was removed for its own protection\n\
  return true;\n\
}" install/install_utils.php

# SuiteCRM obviously includes some open-coded checks for writable
# files that completely ignore SuiteCRM's own function for checking
# writability.  Why would you expect otherwise?
#
sed -i -E "s/is_writable\('\.\/config.*?'\)/true/g" \
    install/installSystemCheck.php

# Fix file permissions
#
find . -type f -exec chmod a-x \{\} \;
chmod -R g-w,o-w .

%install

# Install SuiteCRM files
#
mkdir -p %{buildroot}%{_datadir}/%{name}
cp -a * %{buildroot}%{_datadir}/%{name}/

# Remove unwanted SuiteCRM files
#
rm %{buildroot}%{_datadir}/%{name}/*.json
rm %{buildroot}%{_datadir}/%{name}/*.lock
rm %{buildroot}%{_datadir}/%{name}/*.md5
rm %{buildroot}%{_datadir}/%{name}/*.xml
rm %{buildroot}%{_datadir}/%{name}/README.md

# Replace LICENSE.txt with a symlink
#
rm %{buildroot}%{_datadir}/%{name}/LICENSE.txt
ln -r -s %{buildroot}%{_defaultlicensedir}/%{name}/LICENSE.txt \
   %{buildroot}%{_datadir}/%{name}/LICENSE.txt

# Install package files
#
install -D -m 644 %{SOURCE1} %{buildroot}%{_sysusersdir}/%{name}.conf
install -D -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/%{name}-scheduler.service
install -D -m 644 %{SOURCE3} %{buildroot}%{_unitdir}/%{name}-scheduler.timer
install -D -m 644 %{SOURCE4} %{buildroot}%{_sysconfdir}/php-fpm.d/%{name}.conf
install -D -m 644 %{SOURCE5} %{buildroot}%{_sysconfdir}/httpd/conf.d/%{name}.conf
install -D -m 644 %{SOURCE6} %{buildroot}%{_sysconfdir}/%{name}/config.php

# Create www directory and symlinks
#
mkdir -p %{buildroot}%{_localstatedir}/www/%{name}
mkdir -p %{buildroot}%{_localstatedir}/www/%{name}/cache
mkdir -p %{buildroot}%{_localstatedir}/www/%{name}/upload
ln -r -s %{buildroot}%{_sysconfdir}/%{name}/config.php \
   %{buildroot}%{_localstatedir}/www/%{name}/config.php

# Create writable directories
#
mkdir -p %{buildroot}%{_localstatedir}/lib/%{name}
mkdir -p %{buildroot}%{_localstatedir}/lib/%{name}/session
mkdir -p %{buildroot}%{_localstatedir}/lib/%{name}/wsdlcache
mkdir -p %{buildroot}%{_localstatedir}/log/%{name}

%pre
%sysusers_create_package %{name} %{SOURCE1}

%post
%systemd_post %{name}-scheduler.service

%preun
%systemd_preun %{name}-scheduler.service

%postun
%systemd_postun_with_restart %{name}-scheduler.service

%files
%doc README.md
%license LICENSE.txt
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/config.php
%config(noreplace) %{_sysconfdir}/php-fpm.d/%{name}.conf
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}.conf
%{_sysusersdir}/%{name}.conf
%{_unitdir}/%{name}-scheduler.service
%{_unitdir}/%{name}-scheduler.timer
%{_datadir}/%{name}
%attr(0775, root, %{name}) %dir %{_localstatedir}/lib/%{name}
%attr(0775, root, %{name}) %dir %{_localstatedir}/lib/%{name}/session
%attr(0775, root, %{name}) %dir %{_localstatedir}/lib/%{name}/wsdlcache
%attr(0775, root, %{name}) %dir %{_localstatedir}/log/%{name}
%ghost %{_localstatedir}/log/%{name}/error.log
%ghost %{_localstatedir}/log/%{name}/slow.log
%dir %{_localstatedir}/www/%{name}
%{_localstatedir}/www/%{name}/config.php
%attr(0775, root, %{name}) %{_localstatedir}/www/%{name}/cache
%attr(0775, root, %{name}) %{_localstatedir}/www/%{name}/upload

%changelog
