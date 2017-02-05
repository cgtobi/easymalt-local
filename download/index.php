<?php
namespace PPLocalFinances;
chdir(__DIR__.'/..');
require 'init.inc.php';

Downloader::downloadTangerine('.local_config/ofxclient-tangerine.ini');

passthru('source venv/bin/activate ; python maltease/cron.py');
