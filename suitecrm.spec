Name:		suitecrm
Version:	7.11.13
Release:	1%{?dist}
Summary:	SuiteCRM Customer Relationship Management
License:	Affero GPLv3
URL:		https://suitecrm.com/
Source0:	https://suitecrm.com/files/162/SuiteCRM-7.11/500/SuiteCRM-%{version}.zip
BuildArch:	noarch
BuildRequires:	findutils
BuildRequires:	sed
BuildRequires:	systemd
Requires:	httpd-filesystem
Requires:	php-cli
Requires:	php-curl
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

# Construct httpd drop-in configuration file
#
cat > %{name}.conf <<EOF
Alias /suitecrm %{_localstatedir}/www/%{name}

<Directory %{_localstatedir}/www/%{name}>
    AllowOverride None
    Options -MultiViews +FollowSymlinks -Indexes
    DirectoryIndex index.php
    Require all granted
</Directory>
EOF

# Construct .user.ini file
#
cat > user.ini <<EOF
upload_max_filesize = 128M
EOF

# Construct systemd service and timer for SuiteCRM scheduler
#
cat > %{name}-scheduler.service <<EOF
[Unit]
Description=Run SuiteCRM scheduler

[Service]
Type=oneshot
User=apache
Group=apache
WorkingDirectory=%{_localstatedir}/www/%{name}
ExecStart=/usr/bin/php -f cron.php

[Install]
WantedBy=multi-user.target
EOF
cat > %{name}-scheduler.timer <<EOF
[Unit]
Description=Run SuiteCRM scheduler

[Timer]
OnUnitInactiveSec=1min
Unit=%{name}-scheduler.service

[Install]
WantedBy=multi-user.target
EOF

%install

# Install source files
#
mkdir -p %{buildroot}%{_datadir}/%{name}
cp -a * %{buildroot}%{_datadir}/%{name}/

# Remove non-source files
#
rm %{buildroot}%{_datadir}/%{name}/*.conf
rm %{buildroot}%{_datadir}/%{name}/*.json
rm %{buildroot}%{_datadir}/%{name}/*.lock
rm %{buildroot}%{_datadir}/%{name}/*.md5
rm %{buildroot}%{_datadir}/%{name}/*.xml
rm %{buildroot}%{_datadir}/%{name}/user.ini
rm %{buildroot}%{_datadir}/%{name}/LICENSE.txt
rm %{buildroot}%{_datadir}/%{name}/README.md
rm %{buildroot}%{_datadir}/%{name}/%{name}-scheduler.*

# Create www directory and symlinks
#
mkdir -p %{buildroot}%{_localstatedir}/www/%{name}
for link in Api ModuleInstall XTemplate Zend custom data include install \
		jssource lib metadata modules service soap themes vendor \
		robots.txt *.html *.php ; do
    ln -r -s %{buildroot}%{_datadir}/%{name}/${link} \
       %{buildroot}%{_localstatedir}/www/%{name}/${link}
done

# Create writable directories
#
mkdir -p %{buildroot}%{_localstatedir}/www/%{name}/cache
mkdir -p %{buildroot}%{_localstatedir}/www/%{name}/upload

# Install httpd drop-in configuration file
#
mkdir -p %{buildroot}%{_sysconfdir}/httpd/conf.d
install -m 644 %{name}.conf %{buildroot}%{_sysconfdir}/httpd/conf.d/

# Install .user.ini and config.php
#
mkdir -p %{buildroot}%{_sysconfdir}/%{name}
install -m 644 user.ini %{buildroot}%{_sysconfdir}/%{name}/
ln -r -s %{buildroot}%{_sysconfdir}/%{name}/user.ini \
   %{buildroot}%{_localstatedir}/www/%{name}/.user.ini
touch %{buildroot}%{_sysconfdir}/%{name}/config.php
ln -r -s %{buildroot}%{_sysconfdir}/%{name}/config.php \
   %{buildroot}%{_localstatedir}/www/%{name}/config.php

# Symlink to LICENSE.txt
#
ln -r -s %{buildroot}%{_defaultlicensedir}/%{name}/LICENSE.txt \
   %{buildroot}%{_localstatedir}/www/%{name}/LICENSE.txt

# Install systemd unit files
#
mkdir -p %{buildroot}%{_unitdir}
install -m 644 %{name}-scheduler.service %{buildroot}%{_unitdir}/
install -m 644 %{name}-scheduler.timer %{buildroot}%{_unitdir}/

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
%config(noreplace) %{_sysconfdir}/%{name}/user.ini
%config(noreplace) %{_sysconfdir}/%{name}/config.php
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}.conf
%{_unitdir}/%{name}-scheduler.service
%{_unitdir}/%{name}-scheduler.timer
%{_datadir}/%{name}
%dir %{_localstatedir}/www/%{name}
%{_localstatedir}/www/%{name}/.user.ini
%{_localstatedir}/www/%{name}/Api
%{_localstatedir}/www/%{name}/ModuleInstall
%{_localstatedir}/www/%{name}/XTemplate
%{_localstatedir}/www/%{name}/Zend
%{_localstatedir}/www/%{name}/custom
%{_localstatedir}/www/%{name}/data
%{_localstatedir}/www/%{name}/include
%{_localstatedir}/www/%{name}/install
%{_localstatedir}/www/%{name}/jssource
%{_localstatedir}/www/%{name}/lib
%{_localstatedir}/www/%{name}/metadata
%{_localstatedir}/www/%{name}/modules
%{_localstatedir}/www/%{name}/service
%{_localstatedir}/www/%{name}/soap
%{_localstatedir}/www/%{name}/themes
%{_localstatedir}/www/%{name}/vendor
%{_localstatedir}/www/%{name}/*.txt
%{_localstatedir}/www/%{name}/*.html
%{_localstatedir}/www/%{name}/*.php
%attr(0775, root, apache) %{_localstatedir}/www/%{name}/cache
%attr(0775, root, apache) %{_localstatedir}/www/%{name}/upload

%changelog
