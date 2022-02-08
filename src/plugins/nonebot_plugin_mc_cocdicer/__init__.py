from ..nonebot_plugin_mc_info import MinecraftConnector
from .dices import rd, help_message, st, en
from .madness import ti, li
from .investigator import Investigator
from .san_check import sc
from .cards import _cachepath, cards, cache_cards, set_handler, show_handler, sa_handler, del_handler

from nonebot import get_driver
from nonebot.plugin import on_startswith

import os

driver = get_driver()


@driver.on_startup
async def _():  # 角色卡暂存目录初始化
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(_cachepath):
        with open(_cachepath, "w", encoding="utf-8") as f:
            f.write("{}")
    cards.load()


@MinecraftConnector.handle('on_player_chat')
async def _on_chat_event(message, server: MinecraftConnector):
    player_message = await server.process_player_chat(message)
    message = player_message
    message["server_uri"] = server.server_uri
    if player_message["message"].startswith(".help"):
        await rdhelphandler(player_message["message"], server)
    elif player_message["message"].startswith(".st"):
        await stcommandhandler(server)
    elif player_message["message"].startswith(".en"):
        await enhandler(player_message["message"], server)
    elif player_message["message"].startswith(".ti"):
        await ticommandhandler(server)
    elif player_message["message"].startswith(".li"):
        await licommandhandler(server)
    elif player_message["message"].startswith(".coc"):
        await cochandler(message, server)
    elif player_message["message"].startswith(".sc"):
        await schandler(message, server)
    elif player_message["message"].startswith(".r"):
        await rdcommandhandler(message, server)
    elif player_message["message"].startswith(".set"):
        await sethandler(message, server)
    elif player_message["message"].startswith(".show"):
        await showhandler(message, server)
    elif player_message["message"].startswith(".sa"):
        await sahandler(message, server)
    elif player_message["message"].startswith(".del"):
        await delhandler(message, server)


rdhelp = on_startswith(".help", priority=2, block=True)
stcommand = on_startswith(".st", priority=2, block=True)
encommand = on_startswith(".en", priority=2, block=True)
ticommand = on_startswith(".ti", priority=2, block=True)
licommand = on_startswith(".li", priority=2, block=True)
coccommand = on_startswith(".coc", priority=2, block=True)
sccommand = on_startswith(".sc", priority=2, block=True)
rdcommand = on_startswith(".r", priority=4, block=True)
setcommand = on_startswith(".set", priority=5, block=True)
showcommand = on_startswith(".show", priority=5, block=True)
sacommand = on_startswith(".sa", priority=5, block=True)
delcommand = on_startswith(".del", priority=5, block=True)


async def rdhelphandler(message: str, server: MinecraftConnector):
    args = message.replace(".help", "").strip()
    await server.broadcast(help_message(args))


async def stcommandhandler(server: MinecraftConnector):
    await server.broadcast(st())


async def enhandler(message: str, server: MinecraftConnector):
    args = str(message).replace(".en", "")[3:].strip()
    await server.broadcast(en(args))


async def rdcommandhandler(message: dict, server: MinecraftConnector):
    args = message["message"].replace(".r", "").strip()
    uid = message["uuid"]
    if args and not("." in args):
        rrd = rd(args)
        if type(rrd) == str:
            await server.broadcast(rrd)
        elif type(rrd) == list:
            await server.tell(player_uuid=uid, message=rrd[0])


async def cochandler(message: dict, server: MinecraftConnector):
    args = message["message"].replace(".coc", "").strip()
    try:
        args = int(args)
    except ValueError:
        args = 20
    inv = Investigator()
    await server.broadcast(inv.age_change(args))
    if 15 <= args < 90:
        cache_cards.update(message, inv.__dict__, save=False)
        await server.broadcast(inv.output())


async def ticommandhandler(server: MinecraftConnector,):
    await server.broadcast(ti())


async def licommandhandler(server: MinecraftConnector,):
    await server.broadcast(li())


async def schandler(message: dict, server: MinecraftConnector):
    args = message["message"].replace(".sc", "").strip().lower()
    await server.broadcast(sc(args, message=message))


async def sethandler(message: dict, server: MinecraftConnector):
    args = message["message"].replace(".set", "").strip().lower()
    await server.broadcast(set_handler(message, args))


async def showhandler(message: dict, server: MinecraftConnector):
    args = message["message"].replace(".show", "").strip().lower()
    for msg in show_handler(message, args):
        await server.broadcast(msg)


async def sahandler(message: dict, server: MinecraftConnector):
    args = message["message"].replace(".sa", "").strip().lower()
    await server.broadcast(sa_handler(message, args))


async def delhandler(message: dict, server: MinecraftConnector):
    args = message["message"].replace(".del", "").strip().lower()
    for msg in del_handler(message, args):
        await server.broadcast(msg)
