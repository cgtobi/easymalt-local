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

rm -f /tmp/finances-local.log

source venv/bin/activate
python maltease/cron.py > /tmp/finances-local.log

# Send email report?
$(python maltease/config_export.py)
if [ ! -z "${MAILTO}" ]; then
	if [ -s /tmp/finances-local.log ]; then
		cat /tmp/finances-local.log | mail -s "Local Finances Import" ${MAILTO}
	fi
fi

# Don't delete /tmp/finances-local.log yet; user might want to refer to it, or get its content to send it somewhere else.
