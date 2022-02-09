import os
import yaml

current_folder = os.path.dirname(__file__)


def get_config() -> list:
    with open(os.path.join(current_folder, 'config.yaml'), "r", encoding='utf-8') as file:
        return [series for series in yaml.safe_load(file.read())]
