<?php

namespace PPLocalFinances;

if (!empty($_GET['debug_sql']) || @$argv[$argc-1] == '--debugsql' || @$argv[$argc-2] == '--debugsql') {
    define('DEBUGSQL', TRUE);
} else {
    define('DEBUGSQL', FALSE);
}

if (!empty($_GET['debug']) || @$argv[$argc-1] == '--debug' || @$argv[$argc-2] == '--debug') {
    define('DEBUG', TRUE);
} else {
    define('DEBUG', FALSE);
}

require_once 'vendor/autoload.php';

require_once 'functions.inc.php';

try {
    DB::connect();
} catch (\Exception $ex) {
    die($ex->getMessage());
}

ini_set('error_reporting', E_ALL);
