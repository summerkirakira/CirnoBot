from nonebot import get_driver
import yaml
import nonebot
import subprocess
import os
import asyncio


driver = get_driver()
current_folder = os.path.dirname(__file__)


def save_config_to_yaml(server_info):
    with open(os.path.join(current_folder, 'config.yaml'), 'w') as f:
        f.write(yaml.dump(server_info, allow_unicode=True, sort_keys=False))


def get_config() -> dict:
    with open(os.path.join(current_folder, 'config.yaml'), 'r') as f:
        return yaml.safe_load(f.read())


server_process = None


@driver.on_startup
def _open_server():
    global server_process
    if not os.path.exists(os.path.join(current_folder, 'config.yaml')):
        save_config_to_yaml({"port": 4500})
    config = get_config()
    command = f"waitress-serve --port={config['port']} --call app:create_app"
    server_process = subprocess.Popen(command, cwd=current_folder, shell=True)



@driver.on_shutdown
def _kill_server():
    global server_process
    server_process.kill()
    nonebot.logger.opt(colors=True).info("<y>图片存储服务器关闭成功</y>")