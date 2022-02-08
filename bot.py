#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import nonebot
from nonebot.adapters.onebot.v11 import Adapter as OneBotAdapter


from nonebot.log import logger, default_format
logger.add("error.log",
           rotation="00:00",
           diagnose=False,
           level="ERROR",
           format=default_format)


nonebot.init()
app = nonebot.get_asgi()

driver = nonebot.get_driver()
driver.register_adapter(OneBotAdapter)


nonebot.load_from_json("plugin_config.json", encoding="utf-8")
nonebot.load_plugin("src.plugins.nonebot_plugin_archive")

