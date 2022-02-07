from nonebot.plugin import require
import os
from .config import current_folder
import json
import yaml


plugin_mc_info = require('nonebot_plugin_mc_info')


def save_config_to_json(server_info):
    with open(os.path.join(current_folder, 'config.json'), 'w') as f:
        f.write(json.dumps(server_info, ensure_ascii=False, indent=4, separators=(',', ': ')))


def save_config_to_yaml(server_info):
    with open(os.path.join(current_folder, 'config.yaml'), 'w') as f:
        f.write(yaml.dump_all(server_info, allow_unicode=True, sort_keys=False))


def save_specific_config(server_config):
    with open(os.path.join(current_folder, 'config.yaml'), "r") as file:
        old_config = [data for data in yaml.full_load_all(file.read())]
        for i in range(len(old_config)):
            if old_config[i]["server_uri"] == server_config["server_uri"]:
                old_config[i] = server_config
                save_config_to_yaml(old_config)
                return


# def get_config() -> list:
#     with open(os.path.join(current_folder, 'config.json')) as f:
#         config = json.loads(f.read())
#         with open(os.path.join(current_folder, 'config.yaml'), "w") as file:
#             file.write(yaml.safe_dump(config, allow_unicode=True, sort_keys=False))
#         return config


def get_config() -> list:
    with open(os.path.join(current_folder, 'config.yaml'), "r") as file:
        return [data for data in yaml.full_load_all(file.read())]




