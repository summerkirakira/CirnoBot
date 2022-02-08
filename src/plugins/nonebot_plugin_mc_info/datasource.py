from .config import current_folder
import os
import json
import yaml


def save_config_to_json(server_info):
    with open(os.path.join(current_folder, 'config.json'), 'w', encoding='utf-8') as f:
        f.write(json.dumps(server_info, ensure_ascii=False))


def save_config_to_yml(server_info):
    with open(os.path.join(current_folder, 'config.yaml'), 'w', encoding='utf-8') as f:
        f.write(yaml.dump_all(server_info, allow_unicode=True, sort_keys=False))


def get_config() -> list:
    with open(os.path.join(current_folder, 'config.yaml'), encoding='utf-8') as f:
        return [data for data in yaml.full_load_all(f.read())]
