#!/bin/bash

BANK="$1"
USERNAME="$2"
PASSWORD="$3"
ANSWER="$4"
LANG="$5"

COOKIE_JAR="/tmp/${BANK}.cookies.txt"
TMP_HTML_FILE="/tmp/${BANK}.html"
DATA_FILES_PREFIX="data/${BANK}-"

if [ "${BANK}" = "chase-can" ]; then
	HOST="online.chasecanada.ca"
	URLPATH="ChaseCanada_Consumer"
elif [ "${BANK}" = "pc-fin" ]; then
	HOST="online.pcmastercard.ca"
	URLPATH="PCB_Consumer"
else
	echo "Error: unknown bank: ${BANK}"
	exit 1
fi

if [ "${LANG}" = "fr" ]; then
	DOWNLOAD_TYPE="tsv_fr"
	CURRENT_BALANCE="Solde actuel"
else
	DOWNLOAD_TYPE="tsv"
	CURRENT_BALANCE="Current Balance"
fi

#####
## Login ##

rm -f "${COOKIE_JAR}"
curl -s -H "Host: ${HOST}" -H 'Pragma: no-cache' -H 'Cache-Control: no-cache' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.67 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H 'Accept-Language: fr-CA,fr-FR;q=0.8,fr;q=0.6,en-US;q=0.4,en;q=0.2' \
    --cookie-jar "${COOKIE_JAR}" \
    "https://${HOST}/${URLPATH}/Login.do" > "${TMP_HTML_FILE}"
curl -sL -H "Host: ${HOST}" -H 'Pragma: no-cache' -H 'Cache-Control: no-cache' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.67 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H "Referer: https://${HOST}/${URLPATH}/Login.do" -H 'Accept-Language: fr-CA,fr-FR;q=0.8,fr;q=0.6,en-US;q=0.4,en;q=0.2' \
    --cookie "${COOKIE_JAR}" --cookie-jar "${COOKIE_JAR}" \
	--data "MFP=%7B%7D&IpAddress=&CallerID=&DeviceID=&username=${USERNAME}&password=${PASSWORD}" \
    "https://${HOST}/${URLPATH}/ProcessLogin.do" > "${TMP_HTML_FILE}"

TOKEN=`grep 'input.*org.apache.struts.taglib.html.TOKEN' "${TMP_HTML_FILE}" | awk -F'"' '{print $(NF-1)}'`

curl -sL -H "Host: ${HOST}" -H 'Cache-Control: max-age=0' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.67 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H "Referer: https://${HOST}/${URLPATH}/ProcessLogin.do" -H 'Accept-Language: fr-CA,fr-FR;q=0.8,fr;q=0.6,en-US;q=0.4,en;q=0.2' \
    --cookie "${COOKIE_JAR}" --cookie-jar "${COOKIE_JAR}" \
    --data "org.apache.struts.taglib.html.TOKEN=${TOKEN}&hintanswer=${ANSWER}&registerTrustedComputer=No&submitNext=Ouvrir+une+session" \
    "https://${HOST}/${URLPATH}/SecondaryAuth.do" > "${TMP_HTML_FILE}"

#####
## Balance from home page ##

BALANCE=`grep -i "${CURRENT_BALANCE}" -A 3 "${TMP_HTML_FILE}" | grep nowrap | head -1 | awk -F'>' '{print $2}' | awk '{print $1}' | awk -F'<' '{print $1}'`
echo "${BALANCE}" > "${DATA_FILES_PREFIX}balance.txt"

#####
## Download current cycle ##

curl -s -H "Host: ${HOST}" -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.67 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H "Referer: https://${HOST}/${URLPATH}/RecentActivity.do" -H 'Accept-Language: fr-CA,fr-FR;q=0.8,fr;q=0.6,en-US;q=0.4,en;q=0.2' \
    --cookie "${COOKIE_JAR}" --cookie-jar "${COOKIE_JAR}" \
    "https://${HOST}/${URLPATH}/TransHistory.do" > "${TMP_HTML_FILE}"

curl -so "${DATA_FILES_PREFIX}current.tsv" -H "Host: ${HOST}" -H 'Cache-Control: max-age=0' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.67 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H "Referer: https://${HOST}/${URLPATH}/TransHistory.do" -H 'Accept-Language: fr-CA,fr-FR;q=0.8,fr;q=0.6,en-US;q=0.4,en;q=0.2' \
    --cookie "${COOKIE_JAR}" --cookie-jar "${COOKIE_JAR}" \
    --data "org.apache.struts.taglib.html.TOKEN=${TOKEN}&downloadType=${DOWNLOAD_TYPE}&cycleDate=00" \
    "https://${HOST}/${URLPATH}/DownLoadTransaction.do"

#####
## Download last cycle

LAST_CYCLE=`grep '<option value=' "${TMP_HTML_FILE}" | grep -v selected | head -1 | awk -F'"' '{print $2}'`

curl -s -H "Host: ${HOST}" -H 'Pragma: no-cache' -H 'Cache-Control: no-cache' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.67 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H "Referer: https://${HOST}/${URLPATH}/TransHistory.do" -H 'Accept-Language: fr-CA,fr-FR;q=0.8,fr;q=0.6,en-US;q=0.4,en;q=0.2' \
    --cookie "${COOKIE_JAR}" --cookie-jar "${COOKIE_JAR}" \
    --data "org.apache.struts.taglib.html.TOKEN=${TOKEN}&cycleDate=${LAST_CYCLE}" \
    "https://${HOST}/${URLPATH}/TransHistory.do" > "${TMP_HTML_FILE}"

curl -so "${DATA_FILES_PREFIX}last.tsv" -H "Host: ${HOST}" -H 'Cache-Control: max-age=0' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.67 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H "Referer: https://${HOST}/${URLPATH}/TransHistory.do" -H 'Accept-Language: fr-CA,fr-FR;q=0.8,fr;q=0.6,en-US;q=0.4,en;q=0.2' \
    --cookie "${COOKIE_JAR}" --cookie-jar "${COOKIE_JAR}" \
    --data "org.apache.struts.taglib.html.TOKEN=${TOKEN}&downloadType=${DOWNLOAD_TYPE}&cycleDate=${LAST_CYCLE}" \
    "https://${HOST}/${URLPATH}/DownLoadTransaction.do"
