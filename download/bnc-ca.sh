#!/bin/bash

BANK="bnc-ca"

COOKIE_JAR="/tmp/${BANK}.cookies.txt"
TMP_HTML_FILE="/tmp/${BANK}.html"
DATA_FILES_PREFIX="data/${BANK}-"

USERNAME="$1"
PASSWORD="$2"
if [ $# -gt 2 ]; then
	QUESTION1="$3"
	ANSWER1="$4"
fi
if [ $# -gt 4 ]; then
	QUESTION2="$5"
	ANSWER2="$6"
fi
if [ $# -gt 6 ]; then
	QUESTION3="$7"
	ANSWER3="$8"
fi

rm -f "${COOKIE_JAR}"

# GET Login page
curl -s -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.67 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H 'Accept-Language: fr-CA,fr-FR;q=0.8,fr;q=0.6,en-US;q=0.4,en;q=0.2' \
    -H 'Referer: https://bvi.bnc.ca/index/bnc/index.html' \
    --cookie-jar "${COOKIE_JAR}" \
    'https://bvi.bnc.ca/auth/Login?GAREASONCODE=-1&GARESOURCEID=SbipBncC&GAURI=https://bvi.bnc.ca/bnc/page%3FaliasDispatcher%3Dstartup&Reason=-1&APPID=SbipBncC&URI=https://bvi.bnc.ca/bnc/page%3FaliasDispatcher%3Dstartup' \
    > "${TMP_HTML_FILE}"

# Login POST
curl -sL -H 'Cache-Control: max-age=0' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.67 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H 'Accept-Language: fr-CA,fr-FR;q=0.8,fr;q=0.6,en-US;q=0.4,en;q=0.2' \
	-H 'Referer: https://bvi.bnc.ca/auth/Login?GAREASONCODE=-1&GARESOURCEID=SbipBncC&GAURI=https://bvi.bnc.ca/bnc/page%3FaliasDispatcher%3Dstartup&Reason=-1&APPID=SbipBncC&URI=https://bvi.bnc.ca/bnc/page%3FaliasDispatcher%3Dstartup' \
	--data "AUTHMETHOD=UserPassword&HiddenURI=https%3A%2F%2Fbvi.bnc.ca%2Fbnc%2Fpage%253FaliasDispatcher%253Dstartup&Parameter1=1440x900&Parameter2=NA&LOCALE=fr_CA&usr_name=${USERNAME}&HiddenURI=https%3A%2F%2Fbvi.bnc.ca%2Fbnc%2Fpage%253FaliasDispatcher%253Dstartup&GARESOURCEID=SbipBncC&pageGenTime=1485216433153&LOCALE=fr_CA&card_number=&usr_name_display=${USERNAME}&name_desc=&usr_password=${PASSWORD}" \
	--cookie "${COOKIE_JAR}" --cookie-jar "${COOKIE_JAR}" \
	'https://bvi.bnc.ca/auth/Login' \
	> "${TMP_HTML_FILE}"
iconv -f iso-8859-1 -t UTF-8 "${TMP_HTML_FILE}" > "${TMP_HTML_FILE}.tmp" && mv "${TMP_HTML_FILE}.tmp" "${TMP_HTML_FILE}"

ACCOUNT_URLS=(`grep "list.*Row.*a.href" "${TMP_HTML_FILE}" | awk -F'"' '{print $2}'`)
if [ ${#ACCOUNT_URLS[@]} -eq 0 ]; then
	# No accounts found; need to answer security question
	
	grep 'Question' "${TMP_HTML_FILE}" -A 2 | grep "${QUESTION1}" >/dev/null
	if [ $? -eq 0 ]; then
		ANSWER="${ANSWER1}"
	else
		grep 'Question' "${TMP_HTML_FILE}" -A 2 | grep "${QUESTION2}" >/dev/null
		if [ $? -eq 0 ]; then
			ANSWER="${ANSWER2}"
		else
			grep 'Question' "${TMP_HTML_FILE}" -A 2 | grep "${QUESTION3}" >/dev/null
			if [ $? -eq 0 ]; then
				ANSWER="${ANSWER3}"
			else
				echo "Error: security questions not found in page."
				exit 1
			fi
		fi
	fi
	
	# Answer security question
	curl -sL -H 'Cache-Control: max-age=0' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.67 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H 'Accept-Language: fr-CA,fr-FR;q=0.8,fr;q=0.6,en-US;q=0.4,en;q=0.2' \
		-H 'Referer: https://bvi.bnc.ca/bnc/page?aliasDispatcher=startup' \
		--data "sharedSecret%5B0%5D.sharedSecretAnswer=${ANSWER}&bindDevice=false" \
		--cookie "${COOKIE_JAR}" --cookie-jar "${COOKIE_JAR}" \
		'https://bvi.bnc.ca/bnc/page?aliasDispatcher=startup' \
		> "${TMP_HTML_FILE}"
	iconv -f iso-8859-1 -t UTF-8 "${TMP_HTML_FILE}" > "${TMP_HTML_FILE}.tmp" && mv "${TMP_HTML_FILE}.tmp" "${TMP_HTML_FILE}"

	ACCOUNT_URLS=(`grep "list.*Row.*a.href" "${TMP_HTML_FILE}" | awk -F'"' '{print $2}'`)
fi

# List accounts
for i in `seq 0 1 ${#ACCOUNT_URLS[@]}`; do
	if [ ${i} -lt ${#ACCOUNT_URLS[@]} ]; then
		ACCOUNT_URLS=(`grep "list.*Row.*a.href" "${TMP_HTML_FILE}" | awk -F'"' '{print $2}'`)
		ACCOUNT_URL=${ACCOUNT_URLS[$i]}
		
		ACCOUNT_NUMBER=`echo "${ACCOUNT_URL}" | awk -F'=' '{print $4}' | awk -F'&' '{print $1}'`
		
		echo "[A] ${ACCOUNT_NUMBER}"
		
		curl -s -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.67 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H 'Accept-Language: fr-CA,fr-FR;q=0.8,fr;q=0.6,en-US;q=0.4,en;q=0.2' \
			-H 'Referer: https://bvi.bnc.ca/bnc/page?aliasDispatcher=startup' \
			--cookie "${COOKIE_JAR}" --cookie-jar "${COOKIE_JAR}" \
		    "https://bvi.bnc.ca${ACCOUNT_URL}" \
			> "${TMP_HTML_FILE}"
		iconv -f iso-8859-1 -t UTF-8 "${TMP_HTML_FILE}" > "${TMP_HTML_FILE}.tmp" && mv "${TMP_HTML_FILE}.tmp" "${TMP_HTML_FILE}"
		
		grep 'Aucune transaction' "${TMP_HTML_FILE}" >/dev/null
		if [ $? -ne 0 ]; then
			# Download OFX file
			KOOK_TOKEN=`grep 'name="kookToken"' "${TMP_HTML_FILE}" | head -1 | awk -F'"' '{print $(NF-1)}'`
			curl -so "${DATA_FILES_PREFIX}${ACCOUNT_NUMBER}.ofx" -H 'Cache-Control: max-age=0' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.67 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H 'Accept-Language: fr-CA,fr-FR;q=0.8,fr;q=0.6,en-US;q=0.4,en;q=0.2' \
				-H "Referer: https://bvi.bnc.ca${ACCOUNT_URL}" \
				--data "aliasDispatcher=bankHistoryExt&cAliasDispatcher=bankingStatement&sortId=1&key=${ACCOUNT_NUMBER}&accountKey=${ACCOUNT_NUMBER}&refreshOnly=false&kookToken=${KOOK_TOKEN}&inProgress=0&msgBoxToDisplay=&type=1&Acckey=${ACCOUNT_NUMBER}&optionId=1&chkRow=1&txtFieldDelim=%3B&txtDecimalDelim=.&cboDateFormat=dd-mm-yyyy&txtExtension=DN&optExportType=3" \
				--cookie "${COOKIE_JAR}" --cookie-jar "${COOKIE_JAR}" \
				'https://bvi.bnc.ca/bnc/page'
		fi
		
		# Back to Historique
		MAIN_URL="https://bvi.bnc.ca`grep 'Bilan' "${TMP_HTML_FILE}" | awk -F'"' '{print $6}'`"
		curl -s -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.67 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H 'Accept-Language: fr-CA,fr-FR;q=0.8,fr;q=0.6,en-US;q=0.4,en;q=0.2' \
			-H "Referer: https://bvi.bnc.ca${ACCOUNT_URL}" \
			--cookie "${COOKIE_JAR}" --cookie-jar "${COOKIE_JAR}" \
			"${MAIN_URL}" \
			> "${TMP_HTML_FILE}"
		iconv -f iso-8859-1 -t UTF-8 "${TMP_HTML_FILE}" > "${TMP_HTML_FILE}.tmp" && mv "${TMP_HTML_FILE}.tmp" "${TMP_HTML_FILE}"
	fi
done
