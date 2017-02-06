import sqlite3


class DB:
    conn = None

    @staticmethod
    def connect(database):
        if DB.conn:
            DB.conn.close()
        DB.conn = sqlite3.connect(database=database, isolation_level=None)
        DB.conn.row_factory = sqlite3.Row

    @staticmethod
    def insert(q, args=None):
        cursor = DB.execute(q, args)
        return cursor.lastrowid

    @staticmethod
    def execute(q, args=None):
        if args.__class__.__name__ != 'tuple':
            # args needs to be a tuple
            args = (args,)
        cursor = DB.conn.cursor()
        cursor.execute(q, args)
        return cursor

    @staticmethod
    def get_first(q, args=None):
        cursor = DB.execute(q, args)
        row = cursor.fetchone()
        if not row:
            return row
        return row

    @staticmethod
    def get_first_value(q, args=None):
        row = DB.get_first(q, args)
        if not row:
            return row
        return row[0]

    @staticmethod
    def get_all(q, args=None):
        cursor = DB.execute(q, args)
        rows = cursor.fetchall()
        if not rows:
            return rows
        return rows

    @staticmethod
    def get_all_values(q, args=None):
        rows = DB.get_all(q, args)
        if not rows:
            return rows
        results = []
        for row in rows:
            results.append(row[0])
        return results
