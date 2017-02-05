#!/usr/bin/env bash

if [ -L "${BASH_SOURCE[0]}" ]; then
	SOURCE="$(readlink "${BASH_SOURCE[0]}")"
else
	SOURCE="${BASH_SOURCE[0]}"
fi
DIR="$( cd "$( dirname "${SOURCE}" )" && pwd )"
# DIR = folder containing this script
cd "${DIR}/.."
# PWD (current directory) = project root folder

source venv/bin/activate
python maltease/cron.py

source init.inc.sh

/usr/local/bin/php import/index.php >> /tmp/finances-local.log

if [ ! -z "${MAILTO}" ]; then
	if [ -s /tmp/finances-local.log ]; then
		cat /tmp/finances-local.log | mail -s "Local Finances Import" ${MAILTO}
	fi
fi

# Don't delete /tmp/finances-local.log yet; user might want to refer to it, or get its content to send it somewhere else.
