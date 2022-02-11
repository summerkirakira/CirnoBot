from nonebot import get_driver
import nonebot
from .config import Config
from .connect import MinecraftConnector
from .config import current_folder
from .datasource import save_config_to_json, get_config, save_config_to_yml
import os

driver = get_driver()
global_config = get_driver().config
export = nonebot.export()

server_list = []


@driver.on_startup
async def connect_to_mc_server():
    if not os.path.exists(os.path.join(current_folder, 'config.yaml')):
        save_config_to_yml([{"server_uri": "", "auth_key": ""}])
    global server_list
    server_configs: list = get_config()
    save_config_to_yml(server_configs)
    server_lists = []
    for server_config in server_configs:
        if server_config["server_uri"]:
            server_lists.append(MinecraftConnector(server_config["server_uri"], server_config["auth_key"]))
    export.mc_server_list = server_lists


@driver.on_shutdown
async def disconnect_to_mc_server():
    global server_list
    server_list = None
# Export something for other plugin


@export.mc
def add_server(server_uri, auth_key) -> MinecraftConnector:
    global server_lists
    new_server = MinecraftConnector(server_uri, auth_key)
    server_lists.append(new_server)
    server_configs = get_config()
    server_configs.append({'server_uri': server_uri, 'auth_key': auth_key})
    save_config_to_json(server_configs)
    return new_server


@export.mc
def delete_server(server_uri) -> bool:
    global server_lists
    for i in range(len(server_lists)):
        if server_lists[i].server_uri == server_uri:
            del server_lists[i]
            return True
    return False


