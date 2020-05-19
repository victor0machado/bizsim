import json

from os import path

SRC_PATH = path.dirname(path.realpath(__file__))
print(f'params-{SRC_PATH}')
PARAM_PATH = path.join(SRC_PATH, 'params.json')


class ParamManager():
    def __init__(self, input_path: str) -> None:
        self.manager = _get_jsonfile(PARAM_PATH)
        self.get_input_data(input_path)

    def get_value(self, param: str):
        return self.manager.get(param, None)

    # Descobrir como atribui um tipo generico pra value
    def set_value(self, param: str, value) -> None:
        self.manager[param] = value
        with open(PARAM_PATH, 'w', encoding='utf-8') as fd:
            json.dump(self.manager, fd, indent=4)

    def get_input_data(self, input_path: str) -> None:
        params = _get_jsonfile(input_path)
        for param, value in params.items():
            self.set_value(param, value)


def _get_jsonfile(filepath: str) -> dict:
    """Store .json file saved on a given path."""
    ret = {}
    if path.isfile(filepath):
        with open(filepath, 'r', encoding='utf-8') as fd:
            ret = json.load(fd)
    return ret
