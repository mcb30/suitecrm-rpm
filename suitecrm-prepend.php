<?php

# The installation is split between the distribution tree (in
# /usr/share/suitecrm) and a writable state directory (passed via the
# SUGAR_PATH environment variable).
#
# SuiteCRM's code is written in the style of an enraged toddler
# dribbling onto a keyboard, and fails to understand even basic
# concepts of separating code from data.  Patching the code (along
# with all possible third-party plugin modules) to fix this basic
# design flaw is not feasible.
#
# We instead patch the PHP core library functions to use the
# appropriate file path at runtime.  Yes, this is hideously ugly.  But
# it's elegance personified compared to anything found in the SuiteCRM
# commit log.
#
# FML.

# Set the include path to search both the distribution tree and the
# writable state directory.
#
define('SUGAR_PATH', getenv('SUGAR_PATH'));
set_include_path(
    __DIR__.PATH_SEPARATOR.SUGAR_PATH.PATH_SEPARATOR.get_include_path()
);

# Determine the actual path to be used for a requested path (which may
# be absolute or relative, and in either case may need fixing up).
#
function actual_path($requested, $writable=null) {

    # Convert to absolute path.  Brain-dead PHP breaks the semantics
    # of realpath() to return false for nonexistent files, so we can't
    # use that.
    #
    $path = $requested;
    if ($path[0] != '/') {
        $path = getcwd().'/'.$path;
    }

    # If the file exists within the distribution tree, use that.
    # Any attempt to write to files within the distribution tree will
    # fail, as intended.
    #
    # If the file does not exist within the distribution tree, then
    # use the (possibly not-yet-existent) file within the
    # writable state directory.
    #
    $path = preg_replace('#^'.SUGAR_PATH.'#', __DIR__, $path);
    if ($writable or !original_file_exists($path)) {
        $path = preg_replace('#^'.__DIR__.'#', SUGAR_PATH, $path);
    }

    return $path;
}

# Replace a builtin function
#
# In theory PHP can handle this sort of thing using closures.  In
# practice the language is so broken that attempting to do so normally
# results in an error such as "Only variables can be passed by
# reference", even when nothing is using pass-by-reference.
#
function replace_builtin($name) {
    runkit7_function_rename($name, 'original_'.$name);
    runkit7_function_rename('replace_'.$name, $name);
}

function replace_chgrp($path, $group) {
    return original_chgrp(actual_path($path), $group);
}

function replace_chmod($path, $mode) {
    return original_chmod(actual_path($path), $mode);
}

function replace_chown($path, $user) {
    return original_chown(actual_path($path), $user);
}

function replace_copy($source, $dest) {
    return original_copy(actual_path($source), actual_path($dest));
}

function replace_file_exists($path) {
    return original_file_exists(actual_path($path));
}

function replace_file_get_contents($path) {
    return original_file_get_contents(actual_path($path));
}

function replace_file_put_contents($path, $data) {
    return original_file_put_contents(actual_path($path), $data);
}

function replace_file($path) {
    return original_file(actual_path($path));
}

function replace_fileatime($path) {
    return original_fileatime(actual_path($path));
}

function replace_filectime($path) {
    return original_filectime(actual_path($path));
}

function replace_filegroup($path) {
    return original_filegroup(actual_path($path));
}

function replace_fileinode($path) {
    return original_fileinode(actual_path($path));
}

function replace_filemtime($path) {
    return original_filemtime(actual_path($path));
}

function replace_fileowner($path) {
    return original_fileowner(actual_path($path));
}

function replace_fileperms($path) {
    return original_fileperms(actual_path($path));
}

function replace_filesize($path) {
    return original_filesize(actual_path($path));
}

function replace_filetype($path) {
    return original_filetype(actual_path($path));
}

function replace_fopen($path, $mode) {
    return original_fopen($actual_path, $mode);
}

function replace_is_dir($path) {
    return original_is_dir(actual_path($path));
}

function replace_is_executable($path) {
    return original_is_executable(actual_path($path));
}

function replace_is_file($path) {
    return original_is_file(actual_path($path));
}

function replace_is_link($path) {
    return original_is_(actual_path($path));
}

function replace_is_readable($path) {
    return original_is_readable(actual_path($path));
}

function replace_is_writable($path) {
    return original_is_writable(actual_path($path));
}

function replace_is_writeable($path) {
    return original_is_writeable(actual_path($path));
}

function replace_lchgrp($path, $group) {
    return original_lchgrp(actual_path($path), $group);
}

function replace_lchown($path, $user) {
    return original_lchown(actual_path($path), $user);
}

function replace_link($target, $link) {
    return original_link(actual_path($target), actual_path($link));
}

function replace_linkinfo($path) {
    return original_linkinfo(actual_path($path));
}

function replace_lstat($path) {
    return original_lstat(actual_path($path));
}

function replace_mkdir($path, $mode=0775, $recursive=false) {
    return original_mkdir(actual_path($path, $mode, $recursive));
}

function replace_move_uploaded_file($uploaded, $path) {
    return original_move_uploaded_file($uploaded, actual_path($path));
}

function replace_pathinfo($path) {
    return original_pathinfo(actual_path($path));
}

function replace_readfile($path) {
    return original_readfile(actual_path($path));
}

function replace_readlink($path) {
    return original_readlink(actual_path($path));
}

function replace_realpath($path) {
    return original_realpath(actual_path($path));
}

function replace_rename($oldname, $newname) {
    return original_rename(actual_path($oldname), actual_path($newname));
}

function replace_rmdir($path) {
    return original_rmdir(actual_path($path));
}

function replace_stat($path) {
    return original_stat(actual_path($path));
}

function replace_symlink($target, $link) {
    return original_symlink(actual_path($target), actual_path($link));
}

function replace_tempnam($path, $prefix) {
    return original_tempnam(actual_path($path, true), $prefix);
}

function replace_touch($path) {
    return original_touch(actual_path($path));
}

function replace_unlink($path) {
    return original_unlink(actual_path($path));
}

replace_builtin('chgrp');
replace_builtin('chmod');
replace_builtin('chown');
replace_builtin('copy');
replace_builtin('file_exists');
replace_builtin('file_get_contents');
replace_builtin('file_put_contents');
replace_builtin('file');
replace_builtin('fileatime');
replace_builtin('filectime');
replace_builtin('filegroup');
replace_builtin('fileinode');
replace_builtin('filemtime');
replace_builtin('fileowner');
replace_builtin('fileperms');
replace_builtin('filetype');
replace_builtin('fopen');
replace_builtin('is_dir');
replace_builtin('is_executable');
replace_builtin('is_file');
replace_builtin('is_link');
replace_builtin('is_readable');
replace_builtin('is_writable');
replace_builtin('is_writeable');
replace_builtin('lchgrp');
replace_builtin('lchown');
replace_builtin('link');
replace_builtin('linkinfo');
replace_builtin('lstat');
replace_builtin('mkdir');
replace_builtin('move_uploaded_file');
replace_builtin('pathinfo');
replace_builtin('readfile');
replace_builtin('readlink');
replace_builtin('realpath');
replace_builtin('rename');
replace_builtin('rmdir');
replace_builtin('stat');
replace_builtin('symlink');
replace_builtin('tempnam');
replace_builtin('touch');
replace_builtin('unlink');
