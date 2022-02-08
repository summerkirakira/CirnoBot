# -*- coding: utf-8 -*-
"""
对外导出mysql连接
"""
import nonebot
from databases import Database
import os

working_dir = os.getcwd()

driver: nonebot.Driver = nonebot.get_driver()
config: nonebot.config.Config = driver.config

sqlite_opened: bool = False
sqlite_pool = Database(f"sqlite:///{os.path.join(working_dir, 'data.db')}")
nonebot.export().sqlite_pool = sqlite_pool


@driver.on_startup
async def connect_to_sqlite():
    global sqlite_opened
    if config.sqlite_host:
        await sqlite_pool.connect()
        sqlite_opened = True
        nonebot.logger.opt(colors=True).info("<y>Connect to Sqlite</y>")


@driver.on_shutdown
async def free_db():
    global sqlite_opened
    if sqlite_opened:
        await sqlite_pool.disconnect()
        sqlite_opened = False
        nonebot.logger.opt(colors=True).info("<y>Disconnect to Sqlite</y>")
