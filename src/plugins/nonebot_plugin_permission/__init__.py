from nonebot import on_message, get_driver
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
import os

from .data_source import save_config_to_yaml, get_config, current_folder


driver = get_driver()
permission_config = {}


permission_check = on_message(priority=0)


@permission_check.handle()
async def message_permission(bot: Bot, event: GroupMessageEvent):

    permission_check.block = False
    if not permission_config['permission_check']:
        return
    if event.sender.user_id in permission_config['black_list']:
        permission_check.block = True
        return
    if permission_config['only_admin_user'] and event.sender.role != 'ADMIN' and 'OWNER':
        permission_check.block = True
        return
    if int(bot.self_id) not in permission_config['group_check']:
        permission_check.block = True
        return
    if event.group_id not in permission_config['group_check'][int(bot.self_id)]:
        permission_check.block = True
        return


@driver.on_startup
def init():
    global permission_config
    if not os.path.exists(os.path.join(current_folder, 'config.yaml')):
        save_config_to_yaml({'permission_check': False,
                             'only_admin_user': False,
                             'group_check': {
                                 12345667: [
                                     12334,
                                     12334
                                 ],
                             },
                             'black_list': [
                                 123123,
                                 123234
                             ]
                             })
    permission_config = get_config()
