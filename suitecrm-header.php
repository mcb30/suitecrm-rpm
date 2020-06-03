<?php

# The file conf_d.php is assembled at service startup time from
# all *.php files placed in /etc/suitecrm/conf.d and
# /etc/suitecrm/<instance>/conf.d.
#
# You may place *.php files in these directories in order to
# override the configuration obtained from config.php and/or
# config_override.php


# Ensure config has been included before attempting to override it
#
require_once 'config.php';
require_once 'config_override.php';
if (isset($GLOBALS['installing'])) {
    require_once 'install/install_defaults.php';
}

# Inhibit log spam from the ElasticSearch code
#
if (empty($sugar_config['search']['ElasticSearch']['enabled'])) {
    $sugar_config['search']['ElasticSearch']['enabled'] = false;
}
