
from maltease.DB import DB


class Transaction:

    def __init__(self, account, unique_id, date, type, amount, name, memo):
        self.id = None  # ROWID
        self.account = account
        self.unique_id = str(unique_id)
        self.date = date.isoformat(' ')
        self.type = str(type).upper()
        self.amount = float(amount)
        self.name = str(name)
        self.memo = str(memo)

    def save(self):
        date = self.date[0:10]

        q = "SELECT 1 FROM transactions WHERE account_id = ? AND unique_id = ?"
        txn_exists = DB.get_first_value(q, (self.account.id, self.unique_id))
        if not txn_exists:
            # New transaction
            print("   [T] %s  %10s  %s" % (date, self.amount, self.name))
            q = "INSERT INTO transactions (account_id, unique_id, date, type, amount, name, memo) " \
                "VALUES (?, ?, ?, ?, ?, ?, ?)"
            DB.insert(q, (self.account.id, self.unique_id, self.date, self.type, self.amount, self.name, self.memo))
