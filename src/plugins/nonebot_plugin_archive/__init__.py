import nonebot
from nonebot import get_driver, on_message, Bot, on_startswith
from nonebot.adapters.onebot.v11 import Bot, Event, GroupMessageEvent, MessageSegment, Message
from nonebot.params import State
import requests
import time
import re
from nonebot.typing import T_State
from .config import Config
from nonebot.rule import Rule
from .data_source import fetch_all_entries, remove_entry, insert_new_entry, current_folder, get_config, save_config_to_yaml
import os
from .entries_picture import entries_list_photo
import random
import json


global_config = get_driver().config
database = nonebot.require("nonebot_plugin_database_connector")
sqlite = database.sqlite_pool
entries = []

driver: nonebot.Driver = nonebot.get_driver()
picture_server_url = None


def is_entry_removable() -> Rule:
    async def _is_entry_removable(bot: Bot, event: Event, state: T_State=State()) -> bool:
        global entries
        if not event.get_plaintext().startswith('.移除词条'): return False
        if isinstance(event, GroupMessageEvent):
            keyword: str = event.get_plaintext().replace('.移除词条', '').strip()
            group_id: int = event.group_id
            for i in range(len(entries)):
                if entries[i]['enabled_groups'].lower() != 'all_groups':
                    if str(group_id) not in entries[i]['enabled_groups'].split('#') or entries[i]['is_random']:
                        continue
                if entries[i]['keywords'] == keyword:
                    state['entry'] = entries[i]
                    state['entry_index'] = i
                    state['is_entry'] = True
                    return True
                if entries[i]['alias']:
                    if keyword in entries[i]['alias'].split('#'):
                        state['entry'] = entries[i]
                        state['is_entry'] = True
                        state['entry_index'] = i
                        return True
        state['is_entry'] = False
        return True

    return Rule(_is_entry_removable)


def is_entry() -> Rule:
    async def _is_entry_checker(bot: Bot, event: Event, state: T_State=State()) -> bool:
        if isinstance(event, GroupMessageEvent):
            keyword: str = event.get_plaintext().strip()
            for my_entry in entries:
                if my_entry['is_private'] and str(my_entry['creator_id']) == str(event.sender.user_id) and my_entry['keywords'] == keyword:
                    state['entry'] = my_entry
                    return True
            if keyword:
                if keyword[0] != '.':
                    return False
            if keyword and keyword[0] == '.':
                keyword = keyword[1:].strip()
            else:
                return False
            group_id: int = event.group_id
            for my_entry in entries:
                if my_entry['is_private'] and str(my_entry['creator_id']) == str(event.sender.user_id) and my_entry['keywords'] == keyword:
                    state['entry'] = my_entry
                    return True
                if my_entry['is_private']:
                    continue
                if my_entry['enabled_groups'].lower() != 'all_groups':
                    if not (event.sender.user_id == my_entry['creator_id'] and my_entry['is_private']):
                        if str(group_id) not in my_entry['enabled_groups'].split('#'):
                            continue
                if my_entry['keywords'] == keyword and not my_entry['is_private']:
                    state['entry'] = my_entry
                    return True
                if my_entry['alias'] and not my_entry['is_private']:
                    if keyword in my_entry['alias'].split('/'):
                        state['entry'] = my_entry
                        return True
        return False

    return Rule(_is_entry_checker)


def cq_url_convert(cq_url) -> str:
    matched = cq_url.group()
    print(matched)
    data = {
        'url': matched
    }
    requests.post(get_config()["image_server_url"] + '/upload', data=json.dumps(data))
    return picture_server_url + matched.split('/')[-2]


display_entries = on_message(rule=is_entry(), priority=1)
entries_modify = on_startswith('.编辑词条', priority=5)
remove_entries = on_startswith('.移除词条', rule=is_entry_removable(), priority=10)
private_entries = on_startswith('.专属词条', priority=5)
refresh_entries = on_startswith('.刷新词条', priority=5)
show_entries = on_startswith('.词条', priority=4)


@refresh_entries.handle()
async def _refresh_entries(bot: Bot, event: Event):
    global entries
    await fetch_all_entries()
    from .data_source import entries
    await bot.send(event, Message([MessageSegment.text('词条刷新成功哟～')]))


@display_entries.handle()
async def _display_entries(bot: Bot, event: Event, state: T_State=State()):
    entry = state['entry']
    content = entry['content']
    no_cache_content = re.sub(r'file=.*?url=', 'file=', content)
    if isinstance(event, GroupMessageEvent):
        await bot.call_api('send_group_msg', message=no_cache_content, group_id=event.group_id)


@entries_modify.handle()
async def _entries_modify(bot: Bot, event: Event, state: T_State=State()):
    global entries
    regex_1 = 'https://gchat.qpic.cn.*?term=[0-9]'
    regex_2 = 'https://c2cpicdw.qpic.cn.*?term=[0-9]'
    if isinstance(event, GroupMessageEvent):
        if get_config()["only_admin_can_edit"]:
            if event.sender.role != 'ADMIN' and event.sender.role != 'OWNER':
                await bot.send(event, Message([MessageSegment.text("诶？貌似只有群主和管理员才能编辑词条呢～")]))
                return
        total_raw_message = re.sub(regex_1, cq_url_convert, str(event.get_message()))
        total_raw_message = re.sub(regex_2, cq_url_convert, total_raw_message)
        total_raw_message = total_raw_message.replace('&#91;', '[')
        total_raw_message = total_raw_message.replace('&#93;', ']')
        total_raw_message = total_raw_message.replace('.编辑词条', '').split('#')
        if len(total_raw_message) < 2:
            await bot.send(event, Message([MessageSegment.text("诶？词条参数似乎有错误哦？请在【.编辑词条】后输入词条内容哦")]))
            return
        if len(total_raw_message) > 2:
            await bot.send(event, Message([MessageSegment.text("诶？词条参数似乎有错误哦？消息内只能出现一个'#'哦？")]))
            return
        keyword = total_raw_message[0].strip()
        if not keyword:
            await bot.send(event, Message([MessageSegment.text("哼，词条名不能为空哦！")]))
            return
        content = total_raw_message[1].strip()
        if len(content.split(':=>')) >= 2:
            if event.sender.user_id not in global_config.admin_list and event.sender.user_id != global_config.super_user:
                await bot.send(event, Message(MessageSegment.text('暂不支持添加参数的说～')))
                return
            parameters = content.split(':=>')[1].replace(' ', '')
            parameter_dict = {
                'creator_id': event.sender.user_id,
                'creator': event.sender.nickname,
                'content': content.split(':=>')[0],
                'keywords': keyword,
                'alias': None,
                'fuzzy_search': False,
                'is_private': False,
                'is_available': True,
                'enabled_groups': str(event.group_id),
                'is_random': False,
                'is_latest': True,
                'create_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
            }
            for parameter in parameters.split(','):
                key = parameter.split('=')[0]
                value = parameter.split('=')[1]
                if key == 'creator_id':
                    parameter_dict['creator_id'] = str(value)
                elif key == 'creator':
                    parameter_dict['creator'] = str(value)
                elif key == 'keywords':
                    parameter_dict['keywords'] = str(value)
                elif key == 'alias':
                    parameter_dict['alias'] = str(value)
                elif key == 'fuzzy_search':
                    parameter_dict['fuzzy_search'] = bool(value)
                elif key == 'is_private':
                    parameter_dict['is_private'] = bool(value)
                elif key == 'is_available':
                    parameter_dict['is_available'] = bool(value)
                elif key == 'enabled_groups':
                    parameter_dict['enabled_groups'] = str(value).replace('/', '#')
            await insert_new_entry(creator_id=parameter_dict['creator_id'], content=parameter_dict['content'],
                                   keywords=parameter_dict['keywords'], enabled_groups=parameter_dict['enabled_groups'],
                                   creator=parameter_dict['creator'], alias=parameter_dict['alias'],
                                   fuzzy_search=parameter_dict['fuzzy_search'], is_private=parameter_dict['is_private'],
                                   is_available=parameter_dict['is_available'], is_random=parameter_dict['is_random'])
            state['new_entry'] = parameter_dict
            await bot.send(event, Message([MessageSegment.text(random.choice(Config.Config.entry_modify_success))]))

        else:
            await insert_new_entry(creator_id=event.sender.user_id, content=content, keywords=keyword,
                                   enabled_groups=str(event.group_id), creator=event.sender.nickname)
            state['new_entry'] = {
                'creator_id': event.sender.user_id,
                'creator': event.sender.nickname,
                'content': content,
                'keywords': keyword,
                'alias': None,
                'fuzzy_search': False,
                'is_private': False,
                'is_available': True,
                'enabled_groups': str(event.group_id),
                'is_random': False,
                'is_latest': True,
                'create_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
            }
            await bot.send(event, Message([MessageSegment.text(random.choice(Config.Config.entry_modify_success))]))
        entries_to_del = []
        for i in range(len(entries)):
            if entries[i]['keywords'] == keyword and (str(event.group_id) in entries[i]['enabled_groups'].split('#') or
                                                      entries[i]['enabled_groups'].lower() == 'all_groups'):
                entries_to_del.append(i)
        for i in entries_to_del:
            del entries[i]
            del entries_to_del[0]
            for j in range(len(entries_to_del)):
                entries_to_del[j] -= 1
        entries.append(state['new_entry'])


@remove_entries.handle()
async def _remove_entries(bot: Bot, event: Event, state: T_State=State()):
    global entries
    if not state['is_entry']:
        await bot.send(event, Message(MessageSegment.text(random.choice(Config.Config.entry_not_legal))))
        return
    await remove_entry(state['entry'])
    del entries[state['entry_index']]
    await bot.send(event, Message(MessageSegment.text(random.choice(Config.Config.entry_remove_success))))


@private_entries.handle()
async def _private_entries(bot: Bot, event: Event, state: T_State=State()):
    global entries
    regex_1 = 'https://gchat.qpic.cn.*?term=[0-9]'
    regex_2 = 'https://c2cpicdw.qpic.cn.*?term=[0-9]'
    if isinstance(event, GroupMessageEvent):
        total_raw_message = re.sub(regex_1, cq_url_convert, str(event.get_message()))
        total_raw_message = re.sub(regex_2, cq_url_convert, total_raw_message)
        total_raw_message = total_raw_message.replace('&#91;', '[')
        total_raw_message = total_raw_message.replace('&#93;', ']')
        total_raw_message = total_raw_message.replace('.专属词条', '').split('#')
        if len(total_raw_message) != 2:
            await bot.send(event, Message([MessageSegment.text("诶？词条参数似乎有错误哦？消息内只能出现一个'#'哦？")]))
            return
        keyword = total_raw_message[0].strip()
        if not keyword:
            await bot.send(event, Message([MessageSegment.text("哼，词条名不能为空哦！")]))
            return
        content = total_raw_message[1].strip()
        if len(content.split(':=>')) >= 2:
            parameters = content.split(':=>')[1].replace(' ', '')
            parameter_dict = {
                'creator_id': event.sender.user_id,
                'creator': event.sender.nickname,
                'content': content.split(':=>')[0],
                'keywords': keyword,
                'alias': None,
                'fuzzy_search': False,
                'is_private': True,
                'is_available': True,
                'enabled_groups': str(event.group_id),
                'is_random': False,
                'is_latest': True,
                'create_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
            }
            for parameter in parameters.split(','):
                key = parameter.split('=')[0]
                value = parameter.split('=')[1]
                if key == 'creator_id':
                    parameter_dict['creator_id'] = str(value)
                elif key == 'creator':
                    parameter_dict['creator'] = str(value)
                elif key == 'keywords':
                    parameter_dict['keywords'] = str(value)
                elif key == 'alias':
                    parameter_dict['alias'] = str(value)
                elif key == 'fuzzy_search':
                    parameter_dict['fuzzy_search'] = bool(value)
                elif key == 'is_private':
                    parameter_dict['is_private'] = bool(value)
                elif key == 'is_available':
                    parameter_dict['is_available'] = bool(value)
                elif key == 'enabled_groups':
                    parameter_dict['enabled_groups'] = str(value).replace('/', '#')
            await insert_new_entry(creator_id=parameter_dict['creator_id'], content=parameter_dict['content'],
                                   keywords=parameter_dict['keywords'], enabled_groups=parameter_dict['enabled_groups'],
                                   creator=parameter_dict['creator'], alias=parameter_dict['alias'],
                                   fuzzy_search=parameter_dict['fuzzy_search'], is_private=parameter_dict['is_private'],
                                   is_available=parameter_dict['is_available'], is_random=parameter_dict['is_random'])
            state['new_entry'] = parameter_dict
            await bot.send(event, Message([MessageSegment.text(random.choice(Config.Config.entry_modify_success))]))

        else:
            await insert_new_entry(creator_id=event.sender.user_id, content=content, keywords=keyword,
                                   enabled_groups=str(event.group_id), creator=event.sender.nickname, is_private=True)
            state['new_entry'] = {
                'creator_id': event.sender.user_id,
                'creator': event.sender.nickname,
                'content': content,
                'keywords': keyword,
                'alias': None,
                'fuzzy_search': False,
                'is_private': True,
                'is_available': True,
                'enabled_groups': str(event.group_id),
                'is_random': False,
                'is_latest': True,
                'create_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
            }
            await bot.send(event, Message([MessageSegment.text(random.choice(Config.Config.entry_modify_success))]))
        entries_to_del = []
        for i in range(len(entries)):
            if entries[i]['keywords'] == keyword and (str(event.group_id) in entries[i]['enabled_groups'].split('#') or
                                                      entries[i]['enabled_groups'].lower() == 'all_groups') and entries[i]['creator_id'] == str(event.sender.user_id):
                entries_to_del.append(i)
        for i in entries_to_del:
            del entries[i]
            del entries_to_del[0]
            for j in range(len(entries_to_del)):
                entries_to_del[j] -= 1
        entries.append(state['new_entry'])


@show_entries.handle()
async def _show_entries(bot: Bot, event: Event):
    if isinstance(event, GroupMessageEvent):
        await bot.send(event, Message(MessageSegment.image(entries_list_photo(event.group_id, entries))))


@driver.on_startup
async def init_archive():
    if not os.path.exists(os.path.join(current_folder, 'config.yaml')):
        save_config_to_yaml({"image_server_url": "http://localhost:4500",
                             "only_admin_can_edit": False})
    global picture_server_url, entries
    picture_server_url = f'{get_config()["image_server_url"]}/?id='
    query = '''
    CREATE TABLE IF NOT EXISTS `archive`
    (
    creator_id TEXT,
    create_time TEXT,
    content TEXT,
    is_private INTEGER,
    creator TEXT,
    is_available INTEGER,
    enabled_groups TEXT,
    keywords TEXT,
    alias TEXT,
    fuzzy_search INTEGER,
    is_latest INTEGER,
    is_random INTEGER
    );'''
    await sqlite.execute(query)
    entries = await fetch_all_entries()

