import collections
import os
import re

from maltease.downloaders.downloader import Downloader


class ChaseCanadaCa(Downloader):
    host = "online.chasecanada.ca"
    urlpath = "ChaseCanada_Consumer"

    def get_institution_name(self):
        return "Chase Canada VISA"

    def get_institution_code(self):
        return os.path.basename(__file__[:-3])

    def get_required_credentials(self):
        c = collections.OrderedDict()
        c["username"] = "Username"
        c["password"] = "Password"
        c["sec_answer"] = "Answer to security question"
        return c

    def download_files(self):
        username = self.keyring_get("username")
        password = self.keyring_get("password")
        answer = self.keyring_get("sec_answer")

        self.start_session()

        # GET Login page
        url = 'https://%s/%s/Login.do' % (self.host, self.urlpath)
        self.get(url)

        # Login POST
        url = 'https://%s/%s/ProcessLogin.do' % (self.host, self.urlpath)
        r = self.post(url, headers={'Cache-Control': 'max-age=0'}, data={
            'MFP': '{}',
            'IpAddress': '',
            'CallerID': '',
            'DeviceID': '',
            'username': username,
            'password': password
        })

        match = re.search(r"<input.*?org.apache.struts.taglib.html.TOKEN.*?value=\"(.*?)\"", r.text)
        if not match:
            print("Error: Token not found in HTML.")
            return
        token = match.group(1)

        # Answer security question
        url = 'https://%s/%s/SecondaryAuth.do' % (self.host, self.urlpath)
        r = self.post(url, headers={'Cache-Control': 'max-age=0'}, data={
            'org.apache.struts.taglib.html.TOKEN': token,
            'hintanswer': answer,
            'registerTrustedComputer': 'No',
            'submitNext': 'Ouvrir une session'
        })

        # Balance from home page
        download_file_type = 'tsv'
        match = re.search(r">Current Balance:?</td>.*?>(.*?)</td>", r.text, re.MULTILINE | re.DOTALL)
        if not match:
            match = re.search(r">Solde actuel:?</td>.*?>(.*?)</td>", r.text, re.MULTILINE | re.DOTALL)
            download_file_type = 'tsv_fr'
            if not match:
                print("Error: account balance not found in HTML.")
                return
        account_balance = match.group(1)
        account_balance = re.sub('<[^>]+?>', '', account_balance)
        with open("data/%s_balance.txt" % self.get_institution_code(), "w") as balance_file:
            print(account_balance, file=balance_file)

        url = 'https://%s/%s/TransHistory.do' % (self.host, self.urlpath)
        r = self.get(url)

        match = re.search(r"<option value=\"(\d+)\">", r.text)
        previous_cycle_ts = match.group(1)

        # Current billing cycle
        url = 'https://%s/%s/DownLoadTransaction.do' % (self.host, self.urlpath)
        r = self.post(url, headers={'Cache-Control': 'max-age=0'}, data={
            'org.apache.struts.taglib.html.TOKEN': token,
            'downloadType': download_file_type,
            'cycleDate': '00'
        })
        with open("data/%s_current.tsv" % self.get_institution_code(), "w") as current_file:
            print(r.text, file=current_file)

        # Previous billing cycle
        url = 'https://%s/%s/TransHistory.do' % (self.host, self.urlpath)
        self.post(url, headers={'Cache-Control': 'max-age=0'}, data={
            'org.apache.struts.taglib.html.TOKEN': token,
            'cycleDate': previous_cycle_ts
        })
        url = 'https://%s/%s/DownLoadTransaction.do' % (self.host, self.urlpath)
        r = self.post(url, headers={'Cache-Control': 'max-age=0'}, data={
            'org.apache.struts.taglib.html.TOKEN': token,
            'downloadType': download_file_type,
            'cycleDate': previous_cycle_ts
        })
        with open("data/%s_previous.tsv" % self.get_institution_code(), "w") as current_file:
            print(r.text, file=current_file)
