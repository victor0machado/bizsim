import sqlite3
import json
import csv

from os import path

from . import connect
from . import schemas

SRC_PATH = path.dirname(path.realpath(__file__))


class database():
    def __init__(self, name: str) -> None:
        self.path = path.join(SRC_PATH, 'db', f'{name}.db')
        self.db = connect.Connect(self.path)
        self.name = name
        self.schema = None
        self.insert_cmd = ''
        self.column_names = self.fetch_column_names()

    def close_connection(self) -> None:
        self.db.close_db()

    def create(self) -> bool:
        if self.schema is None:
            print(f'Erro na criacao da tabela! Esquema nao reconhecido!')
            return False

        print(f'Criando tabela {self.schema[0]}...')
        try:
            self.db.cursor.executescript(self.schema[1])
            self.db.commit_db()
        except sqlite3.Error:
            print(f'Aviso: erro na criacao da tabela {self.schema[0]}.')
            return False

        print('Tabela criada com sucesso.')
        self.column_names = self.fetch_column_names()
        return True

    def add_many_registers(self, values: list) -> bool:
        """Add several registers to a db.
        values: list containing lists with single entries"""
        try:
            self.db.cursor.executemany(self.insert_cmd, values)
            self.db.commit_db()
            print(f'Dados inseridos com sucesso na tabela {self.name}: {len(values)} registros.')
        except sqlite3.IntegrityError:
            print("Aviso: erro na inclusao dos dados no banco.")
            return False

        return True

    def fetch_all_entries(self) -> list:
        sql = f'SELECT * FROM {self.name} ORDER BY {self.column_names[0]}'
        exe = self.db.cursor.execute(sql)
        return exe.fetchall()

    def fetch_all_ids(self) -> list:
        entries = self.fetch_all_entries()
        return [entry[0] for entry in entries]

    def fetch_all_entries_from_match(self, column: str, value) -> list:
        sql = f"SELECT * FROM {self.name} WHERE {column}="
        if isinstance(value, str):
            sql += f"'{value}'"
        else:
            sql += f"{value}"
        exe = self.db.cursor.execute(sql)
        return exe.fetchall()

    def fetch_column_names(self) -> list:
        sql = f'PRAGMA table_info({self.name})'
        exe = self.db.cursor.execute(sql)
        return [column[1] for column in exe.fetchall()]

    def pretty_entries(self, entries: list) -> list:
        ret = []
        for entry in entries:
            ret.append({self.column_names[i]: entry[i] for i in range(len(entry))})

        return ret

    def export_to_json(self, outpath: str) -> bool:
        entries = self.fetch_all_entries()
        obj_to_json = self.pretty_entries(entries)
        try:
            with open(outpath, 'w') as fd:
                json.dump(obj_to_json, fd, indent=4)
            return True
        except Exception as err:
            print(f'Ocorreu um erro!\nMensagem: {err}')
            return False

    @staticmethod
    def _import_from_csv(inputpath: str) -> list:
        entries = []
        with open(inputpath, newline='', encoding='utf8') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=';')
            entries = [row for row in spamreader]

        return entries

    def add_from_csv(self, inputpath: str) -> bool:
        entries = self._import_from_csv(inputpath)
        return self.add_many_registers(entries)


class ClientesDb(database):
    def __init__(self):
        super().__init__('clientes')
        self.schema = schemas.clientes
        self.insert_cmd = """
            INSERT INTO clientes (cpf, nascimento, id_endereco, genero)
            VALUES (?,?,?,?)
        """

    def search_cpf(self, value: str) -> int:
        ret = self.fetch_all_entries_from_match('cpf', value)
        if ret:
            return ret[0][0]
        else:
            return -1


class ProdutosDb(database):
    def __init__(self):
        super().__init__('produtos')
        self.schema = schemas.produtos
        self.insert_cmd = """
            INSERT INTO produtos (modelo, cor, tamanho, preco)
            VALUES (?,?,?,?)
        """


class VendasDb(database):
    def __init__(self):
        super().__init__('vendas')
        self.schema = schemas.vendas
        self.insert_cmd = """
            INSERT INTO vendas (data_venda, frete, meio_pgto, id_cliente)
            VALUES (?,?,?,?)
        """


class ProdVendDb(database):
    def __init__(self):
        super().__init__('prod_vend')
        self.schema = schemas.prod_vend
        self.insert_cmd = """
            INSERT INTO prod_vend (quantidade, id_venda, id_produto)
            VALUES (?,?,?)
        """


class EnderecosDb(database):
    def __init__(self):
        super().__init__('enderecos')
        self.schema = schemas.enderecos
        self.insert_cmd = """
            INSERT INTO enderecos (cidade, uf)
            VALUES (?,?)
        """

    def fetch_address(self, city: str, uf: str) -> int:
        sql = f"SELECT * FROM {self.name} WHERE cidade='{city}' and uf='{uf}'"
        exe = self.db.cursor.execute(sql)
        ret = exe.fetchall()
        if ret:
            return ret[0][0]
        return -1
