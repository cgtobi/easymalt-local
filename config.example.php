<?php

$CONFIG = new stdClass;

$CONFIG->DB_ENGINE = 'mysql'; // Only 'mysql' is supported right now

$CONFIG->DB_HOST   = 'localhost';
$CONFIG->DB_USER   = 'loc_fin_user';
$CONFIG->DB_PWD    = 'some_password_here';
$CONFIG->DB_NAME   = 'finances';

// What timezone is your database server using?
$CONFIG->DB_TIMEZONE = 'America/Montreal'; // PHP format; ref: http://php.net/manual/en/timezones.php

// Un-comment to receive reports when the daily download & import job runs.
//$CONFIG->MAILTO = 'you@gmail.com';

// LOG_LEVEL_DEBUG & LOG_LEVEL_INFO: you will receive emails every day, when the daily 'download-n-import' runs
// LOG_LEVEL_WARNING & +: you will only receive emails when something goes wrong
$CONFIG->LOG_LEVEL = LOG_LEVEL_INFO;

// If you installed ofxclient somewhere else than the venv virtualenv, specify the full path to the ofxclient executable here.
$CONFIG->OFXCLIENT_EXECUTABLE = 'venv/bin/ofxclient';
