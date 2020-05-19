import random

from os import path
from calendar import monthrange
from datetime import date
from typing import Tuple

from . import gen_random
from . import params
from .db import manager as db_manager

PM = params.ParamManager()
SRC_PATH = path.dirname(path.realpath(__file__))
print(f'simulator-{SRC_PATH}')
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

    created_tables = PM.get_value('created_tables') or []
    for table, database in tables.items():
        db[table] = database()
        if table not in created_tables:
            db[table].create()
            created_tables.append(table)
            # melhorar isso.
            PM.set_value('created_tables', created_tables)

    return db


def add_city(city: str, uf: str, db: dict) -> int:
    id_address = db['enderecos'].fetch_address(city, uf)
    if id_address == -1:
        db['enderecos'].add_many_registers([[city, uf]])
    return db['enderecos'].fetch_address(city, uf)


def add_client(id_address: int, year: int, db: dict) -> int:
    while True:
        cpf = gen_random.cpf()
        if db['clientes'].search_cpf(cpf) == -1:
            break
    birthdate = gen_random.birthdate(year)
    gender = gen_random.gender()
    db['clientes'].add_many_registers([[cpf, birthdate, id_address, gender]])
    return db['clientes'].search_cpf(cpf)


def add_sale(client_id: int, curr_date: str, db: dict) -> int:
    shipping = gen_random.shipping()
    pay_option = gen_random.payment()
    db['vendas'].add_many_registers([[curr_date, shipping, pay_option, client_id]])
    return db['vendas'].fetch_all_ids()[-1]


def add_sold_prods(sale_id: int, prods: list, db: dict) -> list:
    for prod in prods:
        db['prod_vend'].add_many_registers([[1, sale_id, prod]])
    prods_entries = db['prod_vend'].fetch_all_entries_from_match('id_venda', sale_id)
    return [prod[0] for prod in prods_entries]


def create_daily_new_clients(daily_clients: float, year: int, db: dict) -> int:
    new_clients = max(int(random.gauss(daily_clients, 3)), 0)
    for _ in range(new_clients):
        city, uf = gen_random.city_state(path.join(IN_PATH, 'cities_with_weights.json'))
        id_address = add_city(city, uf, db)
        add_client(id_address, year, db)

    return new_clients


def create_daily_sales(daily_sales: float, prod_per_client: float, curr_date: str, db: dict) -> Tuple[int, int]:
    sales = max(int(random.gauss(daily_sales, 3)), 0)
    total_sold_products = 0
    daily_clients = []
    for _ in range(sales):
        while True:
            client_id = random.choice(db['clientes'].fetch_all_ids())
            if client_id not in daily_clients or len(daily_clients) == len(db['clientes'].fetch_all_ids()):
                break
        prods = max(int(random.gauss(prod_per_client, 1.5)), 1)
        chosen_prods = random.choices(db['produtos'].fetch_all_ids(), k=prods)
        sale_id = add_sale(client_id, curr_date, db)
        add_sold_prods(sale_id, chosen_prods, db)
        total_sold_products += prods
        daily_clients.append(client_id)

    return sales, total_sold_products


def run_simulator(start_year: int, db: dict) -> dict:
    years = PM.get_value('years')
    total_clients = [0 for _ in range(years)]
    total_sales = [0 for _ in range(years)]
    total_sold_products = [0 for _ in range(years)]
    for year in range(years):
        base_daily_sales = PM.get_value('average_daily_sales')[year]
        if year == 0:
            base_daily_clients = PM.get_value('initial_yearly_new_clients') / DAYS_IN_YEAR
            base_prod_per_sale = PM.get_value('initial_average_products_per_sale')
        else:
            base_daily_clients = base_daily_clients * PM.get_value('yearly_client_growth')[year]
            base_prod_per_sale = base_prod_per_sale * PM.get_value('yearly_prod_sold_growth')[year]

        for month in range(12):
            seasonality = PM.get_value('trimester_seasonality')[month // 3]
            daily_clients = base_daily_clients * seasonality
            prod_per_client = base_prod_per_sale * seasonality
            avg_daily_sales = base_daily_sales * seasonality

            for day in range(monthrange(start_year + year, month + 1)[1]):
                curr_date = date(year + start_year, month + 1, day + 1).strftime('%d/%m/%Y')
                total_clients[year] += create_daily_new_clients(daily_clients, year + start_year, db)
                sales = create_daily_sales(avg_daily_sales, prod_per_client, curr_date, db)
                total_sales[year] += sales[0]
                total_sold_products[year] += sales[1]

            print(f'\n\nTotal clientes: {total_clients[year]}')
            print(f'Vendas totais: {total_sales[year]}')
            print(f'Total produtos: {total_sold_products[year]}')

    return db


def main() -> None:
    db = start_dbs()
    db['produtos'].add_from_csv(path.join(IN_PATH, 'produtos.csv'))
    db = run_simulator(2015, db)
