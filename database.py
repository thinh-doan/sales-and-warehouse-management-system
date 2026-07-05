# Kết nối với database  
import pyodbc

class Database:
    def __init__(self):
        self.conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost;"
            "DATABASE=QL_BANHANG_KHOHANG;"
            "Trusted_Connection=yes;"
        )

    def execute(self, query, params=None):
        cursor = self.conn.cursor()

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        return cursor

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()