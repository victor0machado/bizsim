import json

from os import path

SRC_PATH = path.dirname(path.realpath(__file__))
CONFIG_PATH = path.join(SRC_PATH, 'config.json')


class Config():
    def __init__(self) -> None:
        self.config = _cache_config()

    def get_value(self, param: str):
        return self.config.get(param, None)

    def set_value(self, param: str, value) -> None:
        self.config[param] = value
        with open(CONFIG_PATH, 'w', encoding='utf-8') as fd:
            json.dump(self.config, fd, indent=4)


def _cache_config() -> dict:
    """Store .json file saved on CONFIG_PATH."""
    ret = {}
    with open(CONFIG_PATH, 'r', encoding='utf-8') as fd:
        ret = json.load(fd)
    return ret
