import sqlite3
class DBManager:
    def __init__(self, db_name="phoenix.db"):
        self.conn = sqlite3.connect(db_name)
