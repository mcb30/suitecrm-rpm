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
Source7:	%{name}-logrotate
Patch1:		0001-rpm-Kill-the-make_writable-function.patch
Patch2:		0002-rpm-Bypass-writability-checks-for-config.php-and-con.patch
Patch3:		0003-rpm-Store-OAuth2-encryption-key-in-a-data-file-rathe.patch
BuildArch:	noarch
BuildRequires:	findutils
BuildRequires:	sed
BuildRequires:	systemd
Requires:	httpd-filesystem
Requires:	nginx-filesystem
Requires:	logrotate
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
%autosetup -n SuiteCRM-%{version} -p 1

%build

# SuiteCRM includes an ELF executable committed to the source tree.
# Kill it with fire.
#
rm -f include/SuiteGraphs/rgraph/scripts/jsmin

# The SuiteCRM distribution zipfile includes a cache directory.  It is
# not empty.  Justified rage fills my soul.  Let the bloodshed
# commence.
#
rm -rf cache upload

# Fix file permissions
#
find . -type f -exec chmod a-x \{\} \;
chmod -R g-w,o-w .

%install

# Create relative symlink via root directory.  This is required to
# ensure that symlink contents remain valid even when viewed through
# the lens of the virtual filesystem provided by phpturd.
#
function ln_via_root() {
    target=$1
    link=$2

    ln -s -r %{buildroot} %{buildroot}${link}
    toplink=$(readlink %{buildroot}${link})
    ln -s -f -T ${toplink}${target} %{buildroot}${link}
}

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
ln_via_root %{_defaultlicensedir}/%{name}/LICENSE.txt \
	    %{_datadir}/%{name}/LICENSE.txt

# Install package files
#
install -D -m 644 %{SOURCE1} %{buildroot}%{_sysusersdir}/%{name}.conf
install -D -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/%{name}-scheduler.service
install -D -m 644 %{SOURCE3} %{buildroot}%{_unitdir}/%{name}-scheduler.timer
install -D -m 644 %{SOURCE4} %{buildroot}%{_sysconfdir}/php-fpm.d/%{name}.conf
install -D -m 644 %{SOURCE5} %{buildroot}%{_sysconfdir}/httpd/conf.d/%{name}.conf
install -D -m 644 %{SOURCE6} %{buildroot}%{_sysconfdir}/%{name}/config.php
install -D -m 644 %{SOURCE7} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

# Create www directory
#
mkdir -p %{buildroot}%{_localstatedir}/www/%{name}
mkdir -p %{buildroot}%{_localstatedir}/www/%{name}/cache
mkdir -p %{buildroot}%{_localstatedir}/www/%{name}/custom
mkdir -p %{buildroot}%{_localstatedir}/www/%{name}/install
mkdir -p %{buildroot}%{_localstatedir}/www/%{name}/upload

# Create empty placeholder files
#
touch %{buildroot}%{_sysconfdir}/%{name}/api.key
touch %{buildroot}%{_localstatedir}/www/%{name}/install/status.json

# Create symlinks within SuiteCRM tree for files stored elsewhere
#
ln_via_root %{_sysconfdir}/%{name}/config.php \
	    %{_datadir}/%{name}/config.php
ln_via_root %{_localstatedir}/log/%{name}/install.log \
	    %{_datadir}/%{name}/install.log
ln_via_root %{_localstatedir}/log/%{name}/suitecrm.log \
	    %{_datadir}/%{name}/suitecrm.log

# Create other writable directories
#
mkdir -p %{buildroot}%{_localstatedir}/lib/%{name}
mkdir -p %{buildroot}%{_localstatedir}/lib/%{name}/session
mkdir -p %{buildroot}%{_localstatedir}/lib/%{name}/wsdlcache
mkdir -p %{buildroot}%{_localstatedir}/log/%{name}

%pre
%sysusers_create_package %{name} %{SOURCE1}

%post
%systemd_post %{name}-scheduler.service
for logfile in error.log slow.log install.log suitecrm.log ; do
    # Ensure logfiles exist, to avoid dangling symlinks
    touch %{_localstatedir}/log/%{name}/${logfile}
    chown %{name}:%{name} %{_localstatedir}/log/%{name}/${logfile}
    chmod 0640 %{_localstatedir}/log/%{name}/${logfile}
done
# Generate an API key
dd if=/dev/random of=%{_sysconfdir}/%{name}/api.key bs=32 count=1

%preun
%systemd_preun %{name}-scheduler.service

%postun
%systemd_postun_with_restart %{name}-scheduler.service

%files
%doc README.md
%license LICENSE.txt
%dir %attr(0750, root, %{name}) %{_sysconfdir}/%{name}
%config(noreplace) %attr(0640, root, %{name}) %{_sysconfdir}/%{name}/config.php
%config(noreplace) %attr(0640, root, %{name}) %{_sysconfdir}/%{name}/api.key
%config(noreplace) %{_sysconfdir}/php-fpm.d/%{name}.conf
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%{_sysusersdir}/%{name}.conf
%{_unitdir}/%{name}-scheduler.service
%{_unitdir}/%{name}-scheduler.timer
%{_datadir}/%{name}
%dir %attr(0770, root, %{name}) %{_localstatedir}/lib/%{name}
%dir %attr(0770, root, %{name}) %{_localstatedir}/lib/%{name}/session
%dir %attr(0770, root, %{name}) %{_localstatedir}/lib/%{name}/wsdlcache
%dir %attr(0770, root, %{name}) %{_localstatedir}/log/%{name}
%ghost %attr(0640, %{name}, %{name}) %{_localstatedir}/log/%{name}/error.log
%ghost %attr(0640, %{name}, %{name}) %{_localstatedir}/log/%{name}/slow.log
%ghost %attr(0640, %{name}, %{name}) %{_localstatedir}/log/%{name}/install.log
%ghost %attr(0640, %{name}, %{name}) %{_localstatedir}/log/%{name}/suitecrm.log
%dir %{_localstatedir}/www/%{name}
%dir %{_localstatedir}/www/%{name}/install
%dir %attr(0770, root, %{name}) %{_localstatedir}/www/%{name}/cache
%dir %attr(0770, root, %{name}) %{_localstatedir}/www/%{name}/custom
%dir %attr(0770, root, %{name}) %{_localstatedir}/www/%{name}/upload
%attr(0660, root, %{name}) %{_localstatedir}/www/%{name}/install/status.json

%changelog
