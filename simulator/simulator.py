import random

from os import path
from calendar import monthrange
from datetime import date

from . import gen_random
from . import config
from .db import manager as db_manager
from .config import SRC_PATH

CF = config.Config()
BASE_PATH = path.dirname(SRC_PATH)
IN_PATH = path.join(BASE_PATH, 'in')
DAYS_IN_YEAR = 365


def start_dbs():
    tables = {
        'produtos': db_manager.ProdutosDb,
        'enderecos': db_manager.EnderecosDb,
        'clientes': db_manager.ClientesDb,
        'vendas': db_manager.VendasDb,
        'prod_vend': db_manager.ProdVendDb
    }
    db = {}

    created_tables = CF.get_value('created_tables') or []
    for table, database in tables.items():
        db[table] = database()
        if table not in created_tables:
            db[table].create()
            created_tables.append(table)
            # melhorar isso.
            CF.set_value('created_tables', created_tables)

    return db


def add_city(city: str, uf: str) -> int:
    return 0


def add_client(cpf: str, birthdate: str, id_address: int) -> int:
    return 0


def run_simulator(start_year: int, db: dict) -> dict:
    years = CF.get_value('years')
    total_clients = [0 for _ in range(years)]
    total_sales = [0 for _ in range(years)]
    total_sold_products = [0 for _ in range(years)]
    for year in range(years):
        base_daily_sales = CF.get_value('average_daily_sales')[year]
        if year == 0:
            base_daily_clients = CF.get_value('initial_yearly_new_clients') / DAYS_IN_YEAR
            base_prod_per_sale = CF.get_value('initial_average_products_per_sale')
        else:
            base_daily_clients = base_daily_clients * CF.get_value('yearly_client_growth')[year]
            base_prod_per_sale = base_prod_per_sale * CF.get_value('yearly_prod_sold_growth')[year]

        for month in range(12):
            seasonality = CF.get_value('trimester_seasonality')[month // 3]
            daily_clients = base_daily_clients * seasonality
            prod_per_client = base_prod_per_sale * seasonality
            avg_daily_sales = base_daily_sales * seasonality

            for day in range(monthrange(start_year + year, month + 1)[1]):
                # curr_date = date(year + start_year, month + 1, day + 1).strftime('%d/%m/%Y')
                new_clients = max(int(random.gauss(daily_clients, 3)), 0)
                for _ in new_clients:
                    city, uf = gen_random.city_state(path.join(IN_PATH, 'cities_with_weights.json'))
                    id_address = add_city(city, uf)
                    cpf = gen_random.cpf()
                    birthdate = gen_random.birthdate(year + start_year)
                    add_client(cpf, birthdate, id_address)

                total_clients[year] += new_clients
                sales = max(int(random.gauss(avg_daily_sales, 3)), 0)
                total_sales[year] += sales

                # inicializar lista com <sales> campos vazios
                for _ in range(sales):
                    # sortear um cliente que nao esteja na lista criada
                    prod = max(int(random.gauss(prod_per_client, 1.5)), 1)
                    # escolher <prod> produtos da tabela de produtos
                    total_sold_products[year] += prod
                    # registrar venda

            print(f'\n\nTotal clientes: {total_clients[year]}')
            print(f'Vendas totais: {total_sales[year]}')
            print(f'Total produtos: {total_sold_products[year]}')

    return db


def main() -> None:
    db = start_dbs()
    # db['produtos'].add_from_csv(path.join(IN_PATH, 'produtos.csv'))
    db = run_simulator(2015, db)
