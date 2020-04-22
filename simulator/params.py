import json

from os import path

SRC_PATH = path.dirname(path.realpath(__file__))
print(f'params-{SRC_PATH}')
PARAM_PATH = path.join(SRC_PATH, 'params.json')


class ParamManager():
    def __init__(self) -> None:
        self.manager = _cache_manager()

    def get_value(self, param: str):
        return self.manager.get(param, None)

    def set_value(self, param: str, value) -> None:
        self.manager[param] = value
        with open(PARAM_PATH, 'w', encoding='utf-8') as fd:
            json.dump(self.manager, fd, indent=4)


def _cache_manager() -> dict:
    """Store .json file saved on PARAM_PATH."""
    ret = {}
    with open(PARAM_PATH, 'r', encoding='utf-8') as fd:
        ret = json.load(fd)
    return ret
