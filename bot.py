#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import nonebot
from nonebot.adapters.onebot.v11 import Adapter as OneBotAdapter
import cirno_util
from cirno_util import get_config


from nonebot.log import logger, default_format
logger.add("error.log",
           rotation="00:00",
           diagnose=False,
           level="ERROR",
           format=default_format)

config = get_config('bot_config.yaml')
nonebot.init(**config)
app = nonebot.get_asgi()

driver = nonebot.get_driver()
driver.register_adapter(OneBotAdapter)


cirno_util.load_plugins()

if __name__ == '__main__':
    nonebot.run()

