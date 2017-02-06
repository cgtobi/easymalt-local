import configparser
import json
import requests

from maltease.DB import DB


class RemoteAPI:

    @staticmethod
    def send():
        config = configparser.ConfigParser()
        config.read('maltease.ini')

        if 'remote' not in config.sections() or 'api_url' not in config['remote']:
            # Not configured
            return

        DB.connect('maltease.sqlite')

        q = "SELECT * FROM accounts"
        accounts = DB.get_all(q)

        q = "SELECT * FROM transactions"
        transactions = DB.get_all(q)

        payload = {
            'accounts': list(map(dict, accounts)),
            'transactions': list(map(dict, transactions))
        }

        api_url = config['remote']['api_url']
        headers = {'Content-type': 'application/json'}
        if 'api_auth_token' in config['remote']:
            headers['Authorization'] = 'Bearer %s' % config['remote']['api_auth_token']
        requests.post(api_url, data=json.dumps(payload), headers=headers)
