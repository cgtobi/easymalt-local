#!/usr/bin/env bash

## This script will read config options from config.php, and export environment variables for each option.
## This will allow shell scripts to have access to config options.
##
## Usage: source init.inc.sh

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

php -r " \
chdir('$DIR'); \
require_once 'functions.inc.php'; \
require_once 'config.php'; \
foreach ((array) \$CONFIG as \$k => \$v) {
	echo \"export \$k=\\\"\$v\\\"\\n\";
}
" > /tmp/env.sh
source /tmp/env.sh
rm /tmp/env.sh
