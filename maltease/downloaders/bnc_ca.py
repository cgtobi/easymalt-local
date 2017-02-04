import collections
import time
import re

from maltease.downloaders.downloader import Downloader


class BncCa(Downloader):

    def get_institution_name(self):
        return "Banque Nationale du Canada"

    def get_institution_code(self):
        return "bnc-ca"

    def get_required_credentials(self):
        c = collections.OrderedDict()
        c["username"] = "Username"
        c["password"] = "Password"
        c["question1"] = "Security question #1 (one word that is only in this question)"
        c["answer1"] = "Answer to security question #1"
        c["question2"] = "Security question #2 (one word that is only in this question)"
        c["answer2"] = "Answer to security question #2"
        c["question3"] = "Security question #3 (one word that is only in this question)"
        c["answer3"] = "Answer to security question #3"
        return c

    def download_files(self):
        username = self.keyring_get("username")
        password = self.keyring_get("password")
        security_questions_answers = {
            self.keyring_get("question1"): self.keyring_get("answer1"),
            self.keyring_get("question2"): self.keyring_get("answer2"),
            self.keyring_get("question3"): self.keyring_get("answer3")
        }

        self.start_session(first_referer='https://bvi.bnc.ca/index/bnc/index.html')

        # GET Login page
        url = 'https://bvi.bnc.ca/auth/Login?GAREASONCODE=-1&GARESOURCEID=SbipBncC&GAURI=https://bvi.bnc.ca/bnc/page%3FaliasDispatcher%3Dstartup&Reason=-1&APPID=SbipBncC&URI=https://bvi.bnc.ca/bnc/page%3FaliasDispatcher%3Dstartup'
        self.get(url)

        # Login POST
        url = 'https://bvi.bnc.ca/auth/Login'
        r = self.post(url, headers={'Cache-Control': 'max-age=0'}, data={
            'Parameter1': '1440x900',
            'Parameter2': 'NA',
            'HiddenURI': 'https://bvi.bnc.ca/bnc/page%3FaliasDispatcher%3Dstartup',
            'GARESOURCEID': 'SbipBncC',
            'pageGenTime': int(time.time()),
            'LOCALE': 'fr_CA',
            'card_number': '',
            'name_desc': '',
            'AUTHMETHOD': 'UserPassword',
            'usr_name': username,
            'usr_name_display': username,
            'usr_password': password
        })

        accounts = re.findall(r"list.*?Row.*?a.href=\"(.*?)\"", r.text)
        if not accounts:
            match = re.search(r"<td.*?Question.*?</td>.*?<td.*?>(.*?)</td>", r.text, re.MULTILINE | re.DOTALL)
            if not match:
                print("Error: security question not found in HTML.")
                return
            the_question = match.group(1)

            the_answer = None
            for a_question, an_answer in security_questions_answers.items():
                if a_question in the_question:
                    the_answer = an_answer
                    break
            if not the_answer:
                print("Error: couldn't find a matching answer to the security question: %s" % the_question)
                return

            # Answer security question
            url = 'https://bvi.bnc.ca/bnc/page?aliasDispatcher=startup'
            r = self.post(url, headers={'Cache-Control': 'max-age=0'}, data={
                'sharedSecret[0].sharedSecretAnswer': the_answer,
                'bindDevice': 'false',
            })

            accounts = re.findall(r"list.*?Row.*?a.href=.(.*?). ", r.text)

        for account_url in accounts:
            match = re.search(r"key=(.*?)&", account_url)
            account_number = match.group(1)
            print("[A] %s" % account_number)

            url = "https://bvi.bnc.ca%s" % account_url
            r = self.get(url)

            match = re.search(r"<a.*?href=\"(.*?)\" .*?Bilan", r.text, re.IGNORECASE)
            main_url = match.group(1)

            if not re.search(r"Aucune transaction", r.text, re.MULTILINE):
                # Download OFX file
                match = re.search(r"name=\"kookToken\".*?value=\"(.*?)\"", r.text)
                kook_token = match.group(1)
                url = 'https://bvi.bnc.ca/bnc/page'
                r = self.post(url, data={
                    'aliasDispatcher': 'bankHistoryExt',
                    'cAliasDispatcher': 'bankingStatement',
                    'sortId': '1',
                    'key': account_number,
                    'accountKey': account_number,
                    'refreshOnly': 'false',
                    'kookToken': kook_token,
                    'inProgress': '0',
                    'msgBoxToDisplay': '',
                    'type': '1',
                    'Acckey': account_number,
                    'optionId': '1',
                    'chkRow': '1',
                    'txtFieldDelim': ';',
                    'txtDecimalDelim': '.',
                    'cboDateFormat': 'dd-mm-yyyy',
                    'txtExtension': 'DN',
                    'optExportType': '3'
                })
                with open("data/bnc-ca-%s.ofx" % account_number, "w") as ofx_file:
                    print(r.text, file=ofx_file)

            # Back to Historique
            url = "https://bvi.bnc.ca%s" % main_url
            self.get(url)
