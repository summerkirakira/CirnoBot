from nonebot import get_driver, on_message, Bot
from nonebot.adapters.onebot.v11 import Event, GroupMessageEvent, MessageSegment, Message
import httpx
from nonebot.params import State
from nonebot.typing import T_State
from .config import Config, save_config_to_yaml, get_config, current_folder
from nonebot.rule import Rule
import json
import os


global_config = get_driver().config
config = Config(**global_config.dict())
driver =get_driver()


async def exchange_rate(from_coin, to_coin, money):
    translib = Config.Config.trans_lib
    if from_coin in translib:
        from_coin = translib[from_coin]
    if to_coin in translib:
        to_coin = translib[to_coin]
    APPKEY = get_config()["app_key"]
    url = "http://api.tianapi.com/txapi/fxrate/index?key={}&fromcoin={}&tocoin={}&money={}".format(APPKEY, from_coin,
                                                                                                   to_coin, money)
    async with httpx.AsyncClient() as client:
        data = await client.get(url)
    json_data = json.loads(data.text)
    if json_data["code"] == 200:
        return json_data["newslist"][0]["money"]
    else:
        return "fail"


async def coin(currency, num):
    try:
        exchange = await exchange_rate(currency, "人民币", num)
        return exchange
    except:
        return None


def is_currency() -> Rule:
    async def _is_currency(bot: Bot, event: Event, state: T_State = State()) -> bool:
        if isinstance(event, GroupMessageEvent) and event.get_plaintext():
            command = event.get_plaintext().replace('.', '', 1).strip()
            for currency in Config.Config.trans_lib:
                if command.startswith(currency):
                    try:
                        state['num'] = float(command.strip().replace(currency, ''))
                        state['currency'] = currency
                        return True
                    except:
                        return False
        return False

    return Rule(_is_currency)


currency_exchange = on_message(rule=is_currency(), priority=14)


@driver.on_startup
async def init():
    if not os.path.exists(os.path.join(current_folder, "config.yaml")):
        save_config_to_yaml({"app_key": "140465c2c940be1df017185fa45a7242"})


@currency_exchange.handle()
async def _currency_exchange(bot: Bot, event: Event, state: T_State = State()):
    exchange_coin = await coin(state['currency'], state['num'])
    message = f'约合CNY:{round(float(exchange_coin), 4)}元的说～\n当前汇率{Config.Config.trans_lib[state["currency"]]}/CNY={round(float(exchange_coin) / state["num"], 4)}'
    await bot.send(event, Message([MessageSegment.text(message)]))
