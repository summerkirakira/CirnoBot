from nonebot import get_driver
import nonebot
try:
    from ..nonebot_plugin_mc_info.connect import MinecraftConnector
except ImportError:
    nonebot.logger.opt(colors=True).error("<r>nonebot_plugin_mc_fun的运行依赖nonebot_plugin_mc_info, 请在商店下载并安装后重启bot...</r>")
    raise ImportError

from .listeners import *
from .config import current_folder, default_config
from .data_source import save_config_to_json, get_config
from .util import refresh_config, check_server
from .commands import *

global_config = get_driver().config
driver = get_driver()


@driver.on_startup
async def init():
    refresh_config()
    await check_server()

