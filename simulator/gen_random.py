"""Generate random values for different data types."""
import random
import rstr
import datetime
import json

from typing import Tuple


def gender() -> str:
    options = ['masculino', 'feminino', 'outro']
    weights = [30, 60, 10]
    return random.choices(options, weights=weights, k=1)[0]


def age() -> int:
    age = 0
    while age <= 18:
        age = int(random.normalvariate(30, random.randint(3, 10)))
    return age


def cpf() -> str:
    cpf = rstr.rstr('1234567890', 11)
    return f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}'


def phone() -> str:
    return '9{0}-{1}'.format(rstr.rstr('1234567890', 4), rstr.rstr('1234567890', 4))


def birthdate(curr_year: int) -> datetime.date:
    year = curr_year - age()
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return datetime.date(year, month, day).strftime('%d-%m-%Y')


def city_state(srcpath: str) -> Tuple:
    cities_with_weights = get_cities_with_weights(srcpath)
    cities = [tuple(elem[0:2]) for elem in cities_with_weights]
    weights = [elem[2] for elem in cities_with_weights]
    return random.choices(cities, weights=weights)[0]


def shipping() -> str:
    options = ['correios', 'transportadora', 'motoboy']
    weights = [random.randint(60, 70)]
    weights.append(random.randint(20, 30))
    weights.append(100 - weights[0] - weights[1])
    return random.choices(options, weights, k=1)[0]


def payment() -> str:
    options = ['credito', 'debito', 'transferencia']
    weights = [random.randint(50, 65)]
    weights.append(random.randint(10, 20))
    weights.append(100 - weights[0] - weights[1])
    return random.choices(options, weights, k=1)[0]


def get_cities_with_weights(srcpath: str) -> list:
    ret = []
    try:
        with open(srcpath) as fd:
            ret = json.load(fd)
    except Exception as err:
        print(f'Erro ao abrir lista de cidades!\nMensagem: {err}')

    return ret
