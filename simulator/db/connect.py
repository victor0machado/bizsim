import sqlite3


class Connect():
    def __init__(self, db_name) -> None:
        try:
            # conectando...
            self.conn = sqlite3.connect(db_name)
            self.cursor = self.conn.cursor()
        except sqlite3.Error:
            print('Erro ao abrir o banco.')

    def close_db(self) -> None:
        if self.conn:
            self.conn.close()
            print('Conexao fechada.')

    def commit_db(self) -> None:
        if self.conn:
            self.conn.commit()
