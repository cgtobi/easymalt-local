from pyfindi import Downloader
import keyring
import json
import os
import re


if __name__ == '__main__':
    print("[D] Downloading 'Banque Nationale du Canada' transactions ...")
    data_dir = 'data'
    for f in os.listdir(data_dir):
        if re.search('bnc-ca-.*', f):
            os.remove(os.path.join(data_dir, f))

    username = keyring.get_password("org.maltease.local", "bnc_ca_username")
    password = keyring.get_password("org.maltease.local", "bnc_ca_password")
    sec_questions = json.loads(keyring.get_password("org.maltease.local", "bnc_ca_sec_questions"))
    Downloader().get_from_bnc_ca(username, password, sec_questions)
