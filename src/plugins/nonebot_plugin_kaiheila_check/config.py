import os
import yaml
current_folder = os.path.dirname(__file__)


def get_config() -> dict:
    with open(os.path.join(current_folder, 'config.yaml'), "r") as file:
        return yaml.safe_load(file.read())


def save_config_to_yaml(server_info):
    with open(os.path.join(current_folder, 'config.yaml'), 'w') as f:
        f.write(yaml.dump(server_info, allow_unicode=True, sort_keys=False))