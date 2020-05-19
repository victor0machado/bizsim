import random

from os import path
from calendar import monthrange, month_name
from datetime import date
from typing import Tuple

from . import gen_random
from . import params
from .db import manager as db_manager


SRC_PATH = path.dirname(path.realpath(__file__))
print(f'simulator-{SRC_PATH}')
BASE_PATH = path.dirname(SRC_PATH)
IN_PATH = path.join(BASE_PATH, 'in')
DAYS_IN_YEAR = 365
PM = params.ParamManager(path.join(IN_PATH, 'initial_params.json'))


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


def populate_day(day: int, month: int, year: int, stats: dict, db: dict) -> Tuple[int, int, int]:
    curr_date = date(year, month, day + 1).strftime('%d/%m/%Y')
    total_clients = create_daily_new_clients(stats['clients'], year, db)
    sales = create_daily_sales(stats['avg_sales'], stats['prods'], curr_date, db)
    return total_clients, sales[0], sales[1]


def populate_month(month: int, year: int, db: dict) -> Tuple[int, int, int]:
    seasonality = PM.get_value('trimester_seasonality')[(month - 1) // 3]
    stats = {
        'clients': PM.get_value('daily_clients') * seasonality,
        'prods': PM.get_value('prod_per_sale') * seasonality,
        'avg_sales': PM.get_value('daily_sales') * seasonality
    }

    totals = (0, 0, 0)
    for day in range(monthrange(year, month)[1]):
        daily_totals = populate_day(day, month, year, stats, db)
        totals = (totals[i] + daily_totals[i] for i in range(3))

    return totals


def set_base_stats(year) -> dict:
    PM.set_value('daily_sales', PM.get_value('average_daily_sales')[year])
    if year == 0:
        daily_clients = PM.get_value('initial_yearly_new_clients') / DAYS_IN_YEAR
        prod_per_sale = PM.get_value('initial_average_products_per_sale')
    else:
        daily_clients = PM.get_value('base_daily_clients') * PM.get_value('yearly_client_growth')[year]
        prod_per_sale = PM.get_value('base_prod_per_sale') * PM.get_value('yearly_prod_sold_growth')[year]

    PM.set_value('daily_clients', daily_clients)
    PM.set_value('prod_per_sale', prod_per_sale)
    return True


def populate_year(year: int, start_year: int, db: dict) -> Tuple[int, int, int]:
    set_base_stats(year)

    totals = (0, 0, 0)
    for month in range(1, 13):
        print(f'Comecando mes {month_name[month]}...')
        monthly_totals = populate_month(month, year + start_year, db)
        totals = (totals[i] + monthly_totals[i] for i in range(3))

    return totals


def run_simulator(start_year: int, db: dict) -> dict:
    years = PM.get_value('years')
    for year in range(years):
        print(f'\n\nComecando ano {year + start_year}...')
        yearly_totals = populate_year(year, start_year, db)

        print(f'\n\nAno {year + start_year}:')
        print(f'\nTotal clientes: {yearly_totals[0]}')
        print(f'Vendas totais: {yearly_totals[1]}')
        print(f'Total produtos vendidos: {yearly_totals[2]}')

    return db


def main() -> None:
    db = start_dbs()
    db['produtos'].add_from_csv(path.join(IN_PATH, 'produtos.csv'))
    db = run_simulator(2015, db)
