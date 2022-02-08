import nonebot
import time
from nonebot import get_driver
import os
import yaml

export = nonebot.require("nonebot_plugin_database_connector")
current_folder = os.path.dirname(__file__)
sqlite = export.sqlite_pool
driver = get_driver()


async def insert_new_row(qq_id: int, bot_id: int, group: int, text_message: str, name: str,
                         permission: str):
    query = 'INSERT INTO message_records (bot_id, qq, `group`, text_message, time, name, permission) ' \
            'VALUES (:bot_id, :qq, :group, :text_message, :time, :name, :permission)'
    data = {
        'bot_id': bot_id,
        'qq': qq_id,
        'group': group,
        'text_message': text_message,
        'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time()))),
        'name': name,
        'permission': permission.upper()
    }
    await sqlite.execute(query, values=data)


def save_config_to_yaml(server_info):
    with open(os.path.join(current_folder, 'config.yaml'), 'w', encoding='utf-8') as f:
        f.write(yaml.dump(server_info, allow_unicode=True, sort_keys=False))


def get_config() -> dict:
    with open(os.path.join(current_folder, 'config.yaml'), 'r', encoding='utf-8') as f:
        return yaml.safe_load(f.read())


