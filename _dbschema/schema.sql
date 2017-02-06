CREATE TABLE accounts (
  id INTEGER PRIMARY KEY,
  name TEXT DEFAULT NULL,
  routing_number TEXT NOT NULL DEFAULT '',
  account_number TEXT NOT NULL DEFAULT '',
  balance REAL NOT NULL DEFAULT 0.00,
  currency TEXT NOT NULL DEFAULT '',
  balance_date TEXT DEFAULT NULL
);
CREATE UNIQUE INDEX AccountUniqueness ON accounts (routing_number, account_number);

CREATE TABLE transactions (
  id INTEGER PRIMARY KEY,
  account_id INTEGER NOT NULL,
  unique_id TEXT DEFAULT '',
  date TEXT NOT NULL,
  type TEXT DEFAULT NULL,
  amount REAL NOT NULL,
  name TEXT DEFAULT NULL,
  memo TEXT DEFAULT NULL
);
CREATE UNIQUE INDEX TransactionUniqueness ON transactions (account_id, unique_id);
