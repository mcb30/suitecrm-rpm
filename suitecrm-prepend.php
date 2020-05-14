<?php

define('SUGAR_PATH', getenv('SUGAR_PATH'));
set_include_path(
    __DIR__.PATH_SEPARATOR.SUGAR_PATH.PATH_SEPARATOR.get_include_path()
);

runkit7_function_rename('chdir', 'original_chdir');
function replace_chdir($dir) {
    $newdir = preg_replace('#^'.__DIR__.'#', SUGAR_PATH, realpath($dir));
    original_chdir($newdir);
}
runkit7_function_rename('replace_chdir', 'chdir');
chdir(getcwd());
