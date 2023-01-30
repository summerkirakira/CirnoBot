import threading

import asyncio
import json
import time
import re
from functools import wraps
from typing import Optional, Dict, List
from loguru import logger

import websockets
from websockets.exceptions import ConnectionClosedError, InvalidStatusCode
import nonebot
import httpx


class MinecraftConnector:
    listener_dict: dict = {
        'on_player_chat': [],
        'on_player_login': [],
        'on_player_disconnected': [],
        'on_player_execute_command': [],
        'on_player_death': [],
        'on_server_log': []
    }
    player_name_key_list = ["Name", "displayName", "name"]

    def get_name_key(self, player: dict) -> str:
        """
        获取玩家的name key
        :param player:
        :return:
        """
        for key in self.player_name_key_list:
            if key in player:
                return key
        return "Name"

    def __init__(self, server_uri: str, auth_key: str):
        self.server_uri: str = server_uri
        self.auth_key: str = auth_key
        self.server_info: Optional[str] = None
        self.connected: bool = True
        self.player_chat: List[dict] = []
        self.command_list: List[dict] = []
        self.login_event: List[dict] = []
        self.logout_event: List[dict] = []
        self.player_death: List[dict] = []
        self.players: List[dict] = []
        self.online_players: List[dict] = []
        if not self.test_connection():
            self.connected = False
            self.ws_tread = self.WebSocketThread(self._ws_connect)
            self.ws_tread.start()
        else:
            self.ws_tread = self.WebSocketThread(self._ws_connect)
            self.ws_tread.start()
            nonebot.logger.opt(colors=True).success(f"<g>与服务器: {server_uri}的Ping test成功！</g>")

    async def get_uuid_from_name(self, name) -> Optional[str]:
        """
        从玩家的name获取uuid
        :param name:
        :return: Optional[str]
        """
        for player in self.players:
            key = self.get_name_key(player)
            if key not in player:
                continue
            if player[key].lower() == name.lower():
                return player["uuid"]
        self.players = await self.get_all_players()
        for player in self.players:
            key = self.get_name_key(player)
            if key not in player:
                continue
            if player[key].lower() == name.lower():
                return player["uuid"]
        return None

    async def get_name_from_uuid(self, uuid: str) -> str:
        """
        从玩家的uuid获取name
        :param uuid: str
        :return: str
        """
        for player in self.players:
            if player["uuid"] == uuid:
                key = self.get_name_key(player)
                return player[key]
        self.players = await self.get_all_players()
        for player in self.players:
            if player["uuid"] == uuid:
                key = self.get_name_key(player)
                return player[key]
        return '未知'

    async def process_player_chat(self, message) -> dict:
        """
        格式化服务器日志中的玩家消息
        :param message: str
        :return: dict
        """
        send_time = message["timestampMillis"]
        message = message["message"]
        player_name = message.split(" ")[0].replace('<', '').replace('>', '')
        message_content = message[:-3].replace(f"<{player_name}> ", "") if "[m" in message else message.replace(f"<{player_name}> ", "")
        player_uuid = await self.get_uuid_from_name(player_name)
        return {
            "name": player_name,
            "message": message_content,
            "uuid": player_uuid,
            "time": send_time
        }

    @classmethod
    async def process_player_death(cls, message, death_configs) -> str:
        """
        格式化服务器日志中的玩家死亡日志
        :param message: str
        :param death_configs: dict
        :return: dict
        """

        for death_config in death_configs:
            regex = death_config["regex"]
            death_message = death_config["message"]
            from_parameters = re.findall(r"%(.*?)%", regex)
            new_regex = re.sub(r"%(.*?)%", r"(.*?)", regex)
            if re.match(new_regex, message):
                matched = re.finditer(new_regex, message)
                for index, match in enumerate(matched):
                    from_para = from_parameters[index]
                    death_message.replace(f"%{from_para}%", match)
                return death_message
        return message

    @classmethod
    def is_death_message(cls, message: str) -> bool:
        """
        判断是否是死亡消息
        :param message: str
        :return: bool
        """
        if 'was killed' in message:
            return True
        if 'discovered floor was lava' in message:
            return True
        if 'fell out of the world' in message:
            return True
        if 'was pricked to death' in message:
            return True
        if 'was shot by an arrow' in message:
            return True
        return False

    async def process_commands(self, message) -> dict:
        """
        格式化服务器日志中的玩家命令日志
        :param message:
        :return:
        """
        message = message["message"]
        player_name = message.split(" ")[0]
        command_content = message.split(" ")[-1].replace("/", "")
        player_uuid = await self.get_uuid_from_name(player_name)
        return {
            "name": player_name,
            "command": command_content,
            "uuid": player_uuid
        }

    class WebSocketThread(threading.Thread):
        def __init__(self, fun):
            self.fun = fun
            threading.Thread.__init__(self)

        def run(self):
            asyncio.run(self.fun())

    @classmethod
    def handle(cls, listener_type: str):
        def _handle(func):
            cls.listener_dict[listener_type].append(func)

            @wraps(func)
            def wrapper(*args, **kwargs):
                rs = func(*args, **kwargs)
                return rs

            return wrapper

        return _handle

    async def _ws_connect(self):
        """
        Websocket连接件
        :return:
        """
        while True:
            try:
                async with websockets.connect(f"ws://{self.server_uri}/v1/ws/console",
                                              extra_headers={"Cookie": f"x-servertap-key={self.auth_key}"}
                                              ) as websocket:
                    nonebot.logger.opt(colors=True).success(f"<g>与服务器: {self.server_uri}的Websocket连接建立成功...</g>")
                    self.connected = True
                    while True:
                        self.connected = True
                        log = await websocket.recv()
                        message = json.loads(log)
                        if int(round(time.time() * 1000)) - message["timestampMillis"] > 10000:
                            # 超过5s的记录将不会执行
                            continue
                        logger.info(f"收到服务器[{self.server_uri}]的消息: {message['message']}")
                        message["message"] = message["message"].strip()
                        if message["message"].startswith("["):
                            message["message"] = message["message"].split("]")[-1].strip()
                        if "logged in with entity id" in message["message"] and 'minecraft' in message["loggerName"]:
                            self.login_event.append(message)
                            for listener in self.listener_dict['on_player_login']:
                                await listener(message=message, server=self)
                        elif 'lost connection' in message['message']:
                            self.logout_event.append(message)
                            for listener in self.listener_dict['on_player_disconnected']:
                                await listener(message=message, server=self)
                        elif message['message'].startswith('<'):
                            self.player_chat.append(await self.process_player_chat(message))
                            for listener in self.listener_dict['on_player_chat']:
                                await listener(message=message, server=self)
                        elif 'issued server command' in message['message']:
                            self.command_list.append(message)
                            for listener in self.listener_dict['on_player_execute_command']:
                                await listener(message=message, server=self)
                        elif 'DedicatedServer' in message['loggerName'] and self.is_death_message(message['message']):
                            self.player_death.append(message)
                            for listener in self.listener_dict['on_player_death']:
                                await listener(message=message, server=self)
                        else:
                            for listener in self.listener_dict['on_server_log']:
                                await listener(message=message, server=self)
            except ConnectionClosedError as e:
                self.connected = False
                nonebot.logger.opt(colors=True).warning(f"<y>服务器: {self.server_uri}关闭连接(可能原因：服务器被关闭), 将在10秒后重试...</y>")
                await asyncio.sleep(10)
            except ConnectionRefusedError as e:
                self.connected = False
                nonebot.logger.opt(colors=True).warning(f"<y>服务器: {self.server_uri}连接被拒绝(可能原因：服务器未开启，插件端口配置错误), 将在10秒后重试...</y>")
                await asyncio.sleep(10)
            except InvalidStatusCode as e:
                nonebot.logger.opt(colors=True).warning(
                    f"<y>服务器: {self.server_uri}连接404(可能原因：服务器未开启，插件端口配置错误), 将在10秒后重试...</y>")
                await asyncio.sleep(10)
            except Exception as e:
                self.connected = False
                nonebot.logger.opt(colors=True).warning(f"<y>服务器: {self.server_uri}连接失败(未知原因), 将在10秒后重试...</y>")
                nonebot.logger.exception(e)
                await asyncio.sleep(10)

    def test_connection(self) -> bool:
        """
        测试连接可用性
        :return: bool
        """
        try:
            httpx.get(f"http://{self.server_uri}/v1/ping", headers={"key": self.auth_key})
            return True
        except httpx.RequestError:
            if self.connected:
                nonebot.logger.opt(colors=True).warning(
                    f"<y>Connect to Minecraft server: {self.server_uri} failed! Please check config.</y>")
            return False

    async def get_server_info(self) -> dict:
        """
        获取服务器信息
        :return: dict
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://{self.server_uri}/v1/server", headers={"key": self.auth_key})
            server_info = json.loads(response.text)
            if self.server_info:
                server_info['name'] = self.server_info['name']
            return server_info

    async def get_players(self) -> list:
        """
        获取当前在线玩家
        :return: list
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"http://{self.server_uri}/v1/players", headers={"key": self.auth_key})
                self.online_players = json.loads(response.text)
                return self.online_players
        except Exception as e:
            # nonebot.logger.exception(e)
            return self.online_players

    async def get_worlds(self) -> dict:
        """
        获取服务器中的世界
        :return: list
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://{self.server_uri}/v1/worlds", headers={"key": self.auth_key})
            return json.loads(response.text)

    async def get_specific_world(self, world_uuid: str) -> dict:
        """
        获取特定世界信息
        :param world_uuid:
        :return:
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://{self.server_uri}/v1/worlds/{world_uuid}",
                                        headers={"key": self.auth_key})
            return json.loads(response.text)

    async def save_world(self, world_uuid: str):
        """
        存储特定的世界
        :param world_uuid: str
        :return:
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(f"http://{self.server_uri}/v1/worlds/{world_uuid}/save",
                                         headers={"key": self.auth_key})
            return json.loads(response.text)

    async def get_score_board(self) -> dict:
        """
        获取记分板
        :return:
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://{self.server_uri}/v1/scoreboard", headers={"key": self.auth_key})
            return json.loads(response.text)

    async def get_specific_score_board(self, name: str) -> dict:
        """
        获取特定记分项
        :param name:
        :return:
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://{self.server_uri}/v1/scoreboard/{name}",
                                        headers={"key": self.auth_key})
            return json.loads(response.text)

    async def get_ops(self) -> list:
        """
        获取服务器当前的OP
        :return: list
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://{self.server_uri}/v1/ops", headers={"key": self.auth_key})
            return json.loads(response.text)

    async def set_op(self, name: str) -> dict:
        """
        根玩家名字设定OP
        :param name:
        :return:
        """
        response = await self.execute_command(f"op {name}")
        return response

    async def remove_op(self, name) -> dict:
        """
        移除特定管理员
        :param name:
        :return:
        """
        response = await self.execute_command(f"deop {name}")
        return response

    async def get_all_players(self) -> list:
        """
        获取服务器所有玩家，包括离线玩家
        :return:
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://{self.server_uri}/v1/players/all", headers={"key": self.auth_key})
            return json.loads(response.text)

    async def get_inventory(self, player_uuid: str, world_uuid: str) -> dict:
        """
        获取特定玩家在特定世界中的背包
        :param player_uuid: str
        :param world_uuid: str
        :return: dict
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://{self.server_uri}/v1/players/{player_uuid}/{world_uuid}/inventory",
                                        headers={"key": self.auth_key})
            return json.loads(response.text)

    async def broadcast(self, message: str) -> dict:
        """
        在服务器公频广播消息
        :param message: str
        :return: dict
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(f"http://{self.server_uri}/v1/chat/broadcast", headers={"key": self.auth_key},
                                         data={"message": message})
            if '500' in response.text:
                response = await self.execute_command(f'say {message}')
                return response
            else:
                return response.text

    async def tell(self, player_uuid: str, message: str) -> dict:
        """
        向指定玩家发送消息
        :param player_uuid: str
        :param message: str
        :return: dict
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(f"http://{self.server_uri}/v1/chat/tell", headers={"key": self.auth_key},
                                         data={"playerUuid": player_uuid, "message": message})
            return json.loads(response.text)

    async def get_plugins(self) -> list:
        """
        获取服务器当前插件列表
        :return: list
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://{self.server_uri}/v1/plugins", headers={"key": self.auth_key})
            return json.loads(response.text)

    async def get_white_list(self) -> list:
        """
        获取当前白名单
        :return: list
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://{self.server_uri}/v1/server/whitelist", headers={"key": self.auth_key})
            return json.loads(response.text)

    async def white_list_on(self) -> dict:
        """
        获取白名单
        :return: dict
        """
        response = await self.execute_command("whitelist on")
        return response

    async def white_list_off(self) -> dict:
        """
        关闭白名单
        :return: dict
        """
        response = await self.execute_command("whitelist off")
        return response

    async def add_white_list(self, name: str) -> dict:
        """
        根据玩家名字添加白名单
        :param name:
        :return:
        """
        response = await self.execute_command(f"whitelist add {name}")
        return response

    async def remove_white_list(self, name: str) -> dict:
        """
        根据玩家名字移除白名单
        :param name: str
        :return: dict
        """
        response = await self.execute_command(f"whitelist remove {name}")
        return response

    async def execute_command(self, command: str, time: int = 100000) -> dict:
        """
        在服务器执行特定命令
        :param command: 命令，无需/
        :param time: 作用未知
        :return: dict
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f"http://{self.server_uri}/v1/server/exec", headers={"key": self.auth_key},
                                             data={
                                                 "command": command,
                                                 "time": time
                                             })
                return response.text
            except httpx.ReadTimeout as e:
                return {'msg': "this command has no return"}

    async def placeholder_api(self, message: str, uuid=None) -> dict:
        """
        根据placeholderAPI字符串获取处理后的字符串, 当使用%player%时 uuid 为目标玩家
        :param message: str
        :param uuid: str
        :return: str
        """
        async with httpx.AsyncClient() as client:
            if uuid:
                data = {
                    'message': message,
                    'uuid': uuid
                }
            else:
                data = {
                    'message': message
                }
            response = await client.post(f"http://{self.server_uri}/v1/placeholders/replace",
                                         headers={"key": self.auth_key},
                                         data=data)
            return json.loads(response.text)



