<?php
namespace PPLocalFinances;
chdir(__DIR__.'/..');
require 'init.inc.php';

Importer::importTangerine();
Importer::importPCFinance();
Importer::importChaseCanada();
Importer::importBNC();

Importer::postProcess();
