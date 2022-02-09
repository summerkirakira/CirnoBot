import nonebot
import os
import yaml
from typing import Optional

current_folder = os.path.dirname(__file__)


def save_config_to_yaml(server_info, path):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(yaml.dump(server_info, allow_unicode=True, sort_keys=False))


def get_config(path) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f.read())


def check_config_path_valid(plugin_name: str) -> Optional[str]:
    config_path = os.path.join('src', 'plugins', plugin_name, 'config.yaml')
    if os.path.exists(config_path):
        return config_path
    else:
        return None


def load_plugins():
    bot_config = get_config('bot_config.yaml')

    if bot_config["bot_enabled"]:
        for plugin_name in bot_config["plugins_config"]:
            if bot_config["plugins_config"][plugin_name]["enabled"]:
                plugin_path = check_config_path_valid(plugin_name)
                if plugin_path:
                    if len(bot_config["plugins_config"][plugin_name].keys()) > 1 :
                        plugin_config = get_config(plugin_path)
                        for key in bot_config["plugins_config"][plugin_name]:
                            if key != 'enabled' and key != 'plugin_folder':
                                plugin_config[key] = bot_config["plugins_config"][plugin_name][key]
                        save_config_to_yaml(plugin_config, plugin_path)
                if os.path.exists(os.path.join('src', 'plugins', plugin_name)):
                    if 'plugin_folder' in bot_config["plugins_config"][plugin_name]:
                        nonebot.load_plugins(f"src/plugins/{plugin_name}")
                    else:
                        nonebot.load_plugin(f"src.plugins.{plugin_name}")
                else:
                    nonebot.load_plugin(plugin_name)
