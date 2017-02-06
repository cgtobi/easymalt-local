import codecs
import csv
import datetime
import glob
import inspect
import keyring
from ofxparse import OfxParser
import os
import re
import sys

from maltease.importers.models.account import *
from maltease.importers.models.transaction import *

class Importer(object):

    # Abstract methods

    def get_institution_code(self):
        raise NotImplementedError("Class %s needs to implement get_institution_code() method" % __class__.__name__)

    def import_files(self):
        raise NotImplementedError("Class %s needs to implement import_files() method" % __class__.__name__)

    # End of abstract methods

    def __init__(self):
        DB.connect('maltease.sqlite')
        DB.init_if_needed('accounts', '_dbschema/schema.sql')


    @staticmethod
    def get_importer(code):
        module = sys.modules['maltease.importers']
        for name, obj in inspect.getmembers(module):
            try:
                if inspect.isclass(obj):
                    i = obj()
                    if hasattr(i, 'get_institution_code') and i.get_institution_code() == code:
                        return i
            except NotImplementedError:
                pass
            except TypeError:
                pass
        return None

    def keyring_get(self, name):
        keyring_name = "%s_%s" % (self.get_institution_code(), name)
        value = keyring.get_password("org.maltease.local", keyring_name)
        return value

class TSVImporter(Importer):

    # Abstract methods

    def get_transaction_from_tsv(self, line, lang):
        # Create a Transaction object from a tab-separated line (already as a list object)
        raise NotImplementedError("Class %s needs to implement get_transaction_from_tsv() method" % __class__.__name__)

    def skip_first_line(self):
        # Is the first line of the TSV file a header?
        raise NotImplementedError("Class %s needs to implement skip_first_line() method" % __class__.__name__)

    def balance_is_negative(self):
        # Return True if the balance found on the website is negative (for example, a credit card).
        raise NotImplementedError("Class %s needs to implement balance_is_negative() method" % __class__.__name__)

    def get_file_encoding(self):
        # latin-1 or utf-8?
        raise NotImplementedError("Class %s needs to implement get_file_encoding() method" % __class__.__name__)

    # End of abstract methods

    def _parse_amount(self, amount_str):
        match = re.match(r"^\$([\d,]+\.\d\d)$", amount_str)
        if match:
            return float(match.group(1).replace(',', ''))
        match = re.match(r"^\(\$([\d,]+\.\d\d)\)$", amount_str)
        if match:
            return -1 * float(match.group(1).replace(',', ''))
        match = re.match(r"^([\d ]+,\d\d) \$$", amount_str)
        if match:
            return float(match.group(1).replace(',', '.').replace(' ', ''))
        match = re.match(r"^\(([\d ]+,\d\d) \$\)$", amount_str)
        if match:
            return -1 * float(match.group(1).replace(',', '.').replace(' ', ''))
        print("Error: unparseable amount: %s" % amount_str)
        return None

    def _parse_date(self, date_str, lang):
        match = re.match(r"^(\d+)/(\d+)/(\d+)$", date_str)
        if match:
            if lang == 'fr':
                date_str = "%s-%s-%s" % (match.group(3), match.group(2), match.group(1))
            else:
                date_str = "%s-%s-%s" % (match.group(3), match.group(1), match.group(2))
            return datetime.datetime.strptime(date_str, '%Y-%m-%d')
        print("Error: unparseable date: %s" % date_str)
        return None

    def import_files(self):
        currency = self.keyring_get("currency")
        account_number = self.keyring_get("account_number")
        lang = self.keyring_get("language")

        # Balance
        for file in glob.glob("data/%s_balance.txt" % self.get_institution_code()):
            with codecs.open(file, encoding=self.get_file_encoding()) as file_obj:
                balance_str = file_obj.readline().strip()
                balance = self._parse_amount(balance_str)
                if not balance:
                    continue
                if self.balance_is_negative():
                    balance *= -1

                file_date = datetime.datetime.fromtimestamp(os.path.getmtime(file))

                a = Account(self.get_institution_code(), account_number, balance, currency, file_date)
                a.save()
                print("[I] %s" % a.name)

                # Transactions
                for file_t in glob.glob("data/%s_*.tsv" % self.get_institution_code()):
                    with codecs.open(file_t, encoding=self.get_file_encoding()) as file_obj_t:
                        first_line = True
                        for line in csv.reader(file_obj_t, delimiter="\t"):
                            if self.skip_first_line() and first_line:
                                first_line = False
                                continue

                            t = self.get_transaction_from_tsv(line, lang)
                            if not t:
                                continue
                            t.account = a
                            t.save()


class OFXImporter(Importer):

    def import_files(self):
        for file in glob.glob("data/%s_*.ofx" % self.get_institution_code()):
            with codecs.open(file) as file_obj:
                ofx = OfxParser.parse(file_obj)
                # Import bank accounts (or update their balance)
                for bank_account in ofx.accounts:
                    a = Account(bank_account.routing_number, bank_account.account_id, bank_account.statement.balance,
                                bank_account.statement.currency, bank_account.statement.end_date)
                    a.save()
                    print("[I] %s" % a.name)

                    # Import transactions
                    for txn in bank_account.statement.transactions:
                        t = Transaction(a, txn.id, txn.date, txn.type, txn.amount, txn.payee, txn.memo)
                        t.save()
