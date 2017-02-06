
from easymalt.DB import DB


class Account:

    def __init__(self, routing_number, account_number, balance, currency, balance_date):
        self.id = None  # ROWID
        self.name = None
        self.routing_number = str(routing_number)
        self.account_number = str(account_number)
        self.balance = float(balance)
        self.currency = str(currency).upper()
        self.balance_date = balance_date.isoformat(' ')

    def save(self):
        q = "INSERT OR IGNORE INTO accounts (routing_number, account_number, balance, currency, balance_date) " \
            "VALUES (?, ?, ?, ?, ?) "
        DB.insert(q, (self.routing_number, self.account_number, self.balance, self.currency, self.balance_date))

        q = "UPDATE accounts SET balance = ?, balance_date = ? WHERE id = ?"
        DB.execute(q, (self.balance, self.balance_date, self.id))

        q = "SELECT id, IFNULL(name, account_number) AS name FROM accounts " \
            "WHERE routing_number = ? AND account_number = ?"
        row = DB.get_first(q, (self.routing_number, self.account_number))
        self.id = int(row['id'])
        self.name = row['name']
