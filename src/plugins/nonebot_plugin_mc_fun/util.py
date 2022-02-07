import nonebot
from nonebot.log import logger
from ..nonebot_plugin_mc_info.connect import MinecraftConnector
from nonebot.plugin import require
from .config import current_folder, default_config
from .data_source import get_config, save_config_to_yaml
from nonebot.adapters.onebot.v11.exception import ActionFailed, NetworkError
import os


plugin_mc_info = require('nonebot_plugin_mc_info')


async def safe_send(send_type, type_id, message):
    """发送出现错误时, 尝试重新发送, 并捕获异常且不会中断运行"""
    for bot_id in nonebot.get_bots():
        try:
            bot = nonebot.get_bots()[bot_id]
        except KeyError:
            logger.error(f"发送失败，Bot:{bot_id}未连接")
            return

        try:
            return await bot.call_api(
                "send_" + send_type + "_msg",
                **{
                    "message": message,
                    "user_id" if send_type == "private" else "group_id": type_id,
                },
            )
        except ActionFailed as e:
            logger.error(f"发送失败，账号可能被风控，错误信息：{e.info}")
        except NetworkError as e:
            logger.error(f"发送失败，请检查网络连接，错误信息：{e.msg}")
    if len(nonebot.get_bots()) == 0:
        logger.error("Bot未连接，请检查gocq或nonebot配置")


async def message_preprocess(message, server: MinecraftConnector, enable_placeholder_api: bool, uuid=None):
    if enable_placeholder_api:
        return await server.placeholder_api(message, uuid=uuid)
    else:
        parsed_message = message
        if "%player%" in parsed_message:
            parsed_message = parsed_message.replace("%player%", await server.get_name_from_uuid(uuid))
        if "%server" in parsed_message:
            server_info = await server.get_server_info()
        if "%player_num%" in parsed_message:
            players = await server.get_players()
            parsed_message = parsed_message.replace("%player_num%", str(len(players)))
        if "%server_name%" in parsed_message:
            parsed_message = parsed_message.replace("%server_name%", server_info['name'])
        return parsed_message


def refresh_config():
    if not os.path.exists(os.path.join(current_folder, 'config.yaml')):
        config_list = []
        for server in plugin_mc_info.mc_server_list:
            new_config = default_config.copy()
            new_config["server_uri"] = server.server_uri
            config_list.append(new_config)
        save_config_to_yaml(config_list)
    else:
        configs = get_config()
        new_configs = configs
        for server in plugin_mc_info.mc_server_list:
            is_find = False
            for my_config in configs:
                if server.server_uri == my_config["server_uri"]:
                    is_find = True
            if not is_find:
                new_config = default_config.copy()
                new_config["server_uri"] = server.server_uri
                new_configs.append(new_config)
        save_config_to_yaml(new_configs)


def get_group_bind_server(group_id):
    server_configs = get_config()
    config = None
    mc_server = None
    for server_config in server_configs:
        if group_id in server_config["is_focus"]:
            config = server_config
            for server in plugin_mc_info.mc_server_list:
                if server.server_uri == config["server_uri"]:
                    mc_server = server
                    return config, mc_server
    return config, mc_server


async def check_server():
    server_configs = get_config()
    for server in plugin_mc_info.mc_server_list:
        server_plugins = await server.get_plugins()
        for plugin in server_plugins:
            if plugin["name"] == "PlaceholderAPI":
                for config in server_configs:
                    if config["server_uri"] == server.server_uri:
                        if not config["enable_placeholder_api"]:
                            nonebot.logger.opt(colors=True).warning(f"<g>在服务器: {server.server_uri}中检测到"
                                                                    f"PlaceholderAPI, 但CirnoBot设置中未开启,"
                                                                    f" 强烈推荐开启此项以解锁更多功能</g>")
                        else:
                            await server.execute_command("papi ecloud download Player")
                            await server.execute_command("papi ecloud download Server")
