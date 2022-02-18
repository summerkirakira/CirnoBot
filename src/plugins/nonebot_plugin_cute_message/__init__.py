import nonebot
from nonebot.params import State
from nonebot import get_driver, on_message, on_notice
from nonebot.adapters.onebot.v11 import Event, GroupMessageEvent, MessageSegment, Message, Bot
from nonebot.adapters.onebot.v11 import PokeNotifyEvent
import random
import re
import os
from nonebot.rule import Rule
from nonebot.typing import T_State
from .config import Config

global_config = get_driver().config
config = Config(**global_config.dict())


export = nonebot.export()
export.emoji = Config.Config.emoji
current_folder = os.path.dirname(__file__)  # get current folder absolute path
CIRNO_PICTURE_FOLDER = os.path.join(current_folder, 'Cirno')
cirno_pic_list = os.listdir(CIRNO_PICTURE_FOLDER)
MEMO_FOLDER = os.path.join(current_folder, 'Memo')


def is_poke() -> Rule:
    async def _is_poke(bot: Bot, event: PokeNotifyEvent) -> bool:
        if event.user_id == int(bot.self_id):
            return False
        return True
    return Rule(_is_poke)


def can_reply() -> Rule:
    async def _can_reply(event: Event, state: T_State = State()) -> bool:
        input_message = event.get_plaintext()
        for key in Config.Config.basic_response_dict:
            if re.match(key, input_message):
                state['reply'] = Config.Config.basic_response_dict[key]
                return True
        return False
    return Rule(_can_reply)


poke_reaction = on_notice(rule=is_poke(), priority=20)
cute_reply = on_message(rule=can_reply(), priority=30)


@poke_reaction.handle()
async def _poke_reaction(bot: Bot, event: PokeNotifyEvent):
    if event.target_id == int(bot.self_id):
        message = random.choice(Config.Config.message_after_poke)
        message += random.choice(Config.Config.emoji) + '\n'
        with open(os.path.join(CIRNO_PICTURE_FOLDER, random.choice(cirno_pic_list)), 'rb') as f:
            image = f.read()
        await bot.send(event, Message([MessageSegment.text(message), MessageSegment.image(image)]))
        await bot.call_api('send_group_msg', group_id=event.group_id, message=f'[CQ:poke,qq={event.user_id}]')


@cute_reply.handle()
async def _cute_reply(bot: Bot, event: Event, state: T_State=State()):
    if isinstance(event, GroupMessageEvent):
        if isinstance(state['reply'], list):
            random_message = random.choice(state['reply'])
            message = []
            if random_message['text']:
                message.append(MessageSegment.text(random_message['text']))
            if random_message['image']:
                with open(os.path.join(MEMO_FOLDER, random_message['image']), 'rb') as f:
                    image = f.read()
                message.append(MessageSegment.image(image))
            if message:
                await bot.send(event, Message(message))
        else:
            message = []
            if state['reply']['text']:
                message.append(MessageSegment.text(state['reply']['text']))
            if state['reply']['image']:
                with open(os.path.join(MEMO_FOLDER, state['reply']['image']), 'rb') as f:
                    image = f.read()
                message.append(MessageSegment.image(image))
            if message:
                await bot.send(event, Message(message))

