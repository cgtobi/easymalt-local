<?php
namespace PPLocalFinances;
chdir(__DIR__.'/..');
require 'init.inc.php';

Downloader::downloadTangerine('.local_config/ofxclient-tangerine.ini');

Downloader::downloadPCFinance(
    Config::getSecure('pc_finance_username'),
    Config::getSecure('pc_finance_password'),
    Config::getSecure('pc_finance_sec_answer'),
    'fr'
);

Downloader::downloadChaseCanada(
    Config::getSecure('chase_can_username'),
    Config::getSecure('chase_can_password'),
    Config::getSecure('chase_can_sec_answer'),
    'en'
);

exec('venv/bin/python cron.py');
