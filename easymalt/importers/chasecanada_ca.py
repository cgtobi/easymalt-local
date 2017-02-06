import os

from easymalt.importers.importer import TSVImporter
from easymalt.importers.models.transaction import *


class ChaseCanadaCa(TSVImporter):

    def get_institution_code(self):
        return os.path.basename(__file__[:-3])

    def skip_first_line(self):
        return True

    def balance_is_negative(self):
        return True

    def get_file_encoding(self):
        return 'latin_1'  # iso-8859-1

    def get_transaction_from_tsv(self, line, lang):
        if len(line) == 0:
            return None
        if len(line) < 9:
            print("Error: not enough fields in file: %d" % len(line))
            return None

        date = self._parse_date(line[1], lang)
        if not date:
            return None

        amount = self._parse_amount(line[2])
        if not amount:
            return None

        payee = line[3]

        memo = "%s %s %s" % (line[4], line[5], line[6])

        unique_id = line[7].strip('" ')

        if line[8] == 'C':
            type = 'CREDIT'
        elif line[8] == 'D':
            type = 'DEBIT'
        else:
            print("Error: unknown type found: %s" % line[8])
            return None

        t = Transaction(None, unique_id, date, type, amount, payee, memo)
        return t
