SuiteCRM RPM package
====================

This RPM provides [SuiteCRM][suitecrm] in a form that is amenable to
package management, allowing for controlled deployments and upgrades.

The upstream SuiteCRM software expects to run as a monolithic blob
with code, configuration, state, temporary scratch files, and log
files all living in a single world-writable directory.

This RPM package uses [`phpturd`][phpturd] to separate the monolithic
blob into well-defined components:

- `/usr/share/suitecrm` contains the SuiteCRM code
- `/etc/suitecrm` contains the configuration files
- `/var/lib/suitecrm` contains the state data
- `/var/cache/suitecrm` contains the temporary scratch files
- `/var/log/suitecrm` contains the log files

Running
-------

SuiteCRM is run as a `systemd` service listening for requests from
your web server via `php-fpm`.  You can enable and start the SuiteCRM
service using:

    systemctl enable --now suitecrm

The service runs as a dedicated `suitecrm` user in order to maximise
separation from other installed software.  Since SuiteCRM has no real
concept of sensible file permissions and relies upon the web server to
serve arbitrary and unspecified static files, the `apache` and `nginx`
users are added to the `suitecrm` group.

If you are using the Apache web server, then you can immediately
access SuiteCRM via the `/suitecrm` alias.

Scheduled tasks
---------------

There is a `systemd` timer to run the SuiteCRM scheduled tasks.  You
can enable and start the timer using:

    systemctl enable --now suitecrm-scheduler.timer

To run the scheduled tasks immediately, you can start the
corresponding service:

    systemctl start suitecrm-scheduler

This `systemd` timer completely replaces the `cron` job suggested by
the SuiteCRM installer.  Do not try to use `cron` to run the scheduled
tasks.

Multiple instances
------------------

You can run multiple instances of the `suitecrm` service.  For example:

    systemctl enable --now suitecrm@sales
    systemctl enable --now suitecrm@logistics

Each service listens for connections on a separate Unix domain socket
(in `/var/run/suitecrm/<instance>/php-fpm.sock`).

To expose these instances via your web server, you will need to add
appropriate directives to your web server configuration.  If you are
using the Apache web server, then you can use the `SuiteCRM` macro.
For example:

    Use SuiteCRM sales /sales/crm
    Use SuiteCRM logistics /logistics/crm

You can use the `SuiteCRM` macro within the server global
configuration or within a `VirtualHost` declaration.  For example:

    <VirtualHost *:443>
	    ServerName sales.example.com
        Use SuiteCRM sales /crm
	</VirtualHost>

Each instance has its own `systemd` timer and service for running
scheduled tasks.  For example:

    systemctl enable --now suitecrm-scheduler@sales.timer

Clearing the cache
------------------

SuiteCRM is not very well written and will frequently corrupt its own
cache.  You can clear out the cache for a particular SuiteCRM instance
using `systemctl clean`.  For example:

    systemctl stop  suitecrm
    systemctl clean suitecrm
	systemctl start suitecrm

Upgrades and modules
--------------------

All software upgrades and module installation must be done through the
system package manager (RPM).  Attempts by users to install modules or
perform upgrades using SuiteCRM's own upgrade wizard will fail since
the SuiteCRM code does not have permission to overwrite itself.  This
is intentional: the system package manager is authoritative and may
not be bypassed.

API key
-------

An API key is generated automatically for each `suitecrm` service
instance and stored in `/etc/suitecrm/<instance>/api.key`.  This
replaces the API key that SuiteCRM attempts to store unsafely by
rewriting the `ApiConfig.php` code file.

You can safely ignore any log message similar to:

    file_put_contents(Api/Core/Config/ApiConfig.php): Permission denied

Patches
-------

Patches against the upstream SuiteCRM code are maintained in a [GitHub
fork][fork].  These patches are required in addition to the directory
separation enforced using [`phpturd`][phpturd].


[suitecrm]: https://suitecrm.com
[phpturd]: https://github.com/unipartdigital/phpturd
[fork]: https://github.com/unipartdigital/SuiteCRM/tree/rpm
