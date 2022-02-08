from nonebot import get_driver, Bot, on_message, require
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.rule import Rule
from .data_source import insert_new_row, current_folder, save_config_to_yaml, get_config
import os

database = require("nonebot_plugin_database_connector")
sqlite = database.sqlite_pool

driver = get_driver()

record_dict = {}


def enabled_record_checker() -> Rule:
    async def _enabled_record_checker(bot: Bot, event: GroupMessageEvent) -> bool:
        if int(bot.self_id) in record_dict and \
                event.group_id in record_dict[int(bot.self_id)]:
            return True
        return False

    return Rule(_enabled_record_checker)


insert_message = on_message(priority=-1, rule=enabled_record_checker())


@insert_message.handle()
async def _insert_message(bot: Bot, event: GroupMessageEvent):
    insert_message.block = False
    await insert_new_row(qq_id=event.sender.user_id, bot_id=int(bot.self_id), group=event.group_id,
                         text_message=str(event.get_message()), name=event.sender.nickname,
                         permission=event.sender.role)


@driver.on_startup
async def init_message_recorder():
    global record_dict
    if not os.path.exists(os.path.join(current_folder, 'config.yaml')):
        save_config_to_yaml({1234567: [1234567, 12345678]})
    record_dict = get_config()
    query = '''
    CREATE TABLE IF NOT EXISTS `message_records`
    (
    id integer PRIMARY KEY autoincrement,
    bot_id int(19),
    qq int(20),
    `group` int(20),
    text_message text,
    `time` text,
    `name` text,
    `permission` text
    );'''
    await sqlite.execute(query)

