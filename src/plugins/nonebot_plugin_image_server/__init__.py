from nonebot import get_driver
import yaml
import nonebot
import subprocess
import os
import socket

driver = get_driver()
current_folder = os.path.dirname(__file__)


def save_config_to_yaml(server_info):
    with open(os.path.join(current_folder, 'config.yaml'), 'w', encoding='utf-8') as f:
        f.write(yaml.dump(server_info, allow_unicode=True, sort_keys=False))


def get_config() -> dict:
    with open(os.path.join(current_folder, 'config.yaml'), 'r', encoding='utf-8') as f:
        return yaml.safe_load(f.read())


def is_port_in_use(port: int) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


server_process = None


@driver.on_startup
def _open_server():
    global server_process
    if not os.path.exists(os.path.join(current_folder, 'config.yaml')):
        save_config_to_yaml({"port": 4500})
    config = get_config()
    command = f"waitress-serve --port={config['port']} --call app:create_app"
    check_port = is_port_in_use(config['port'])
    if check_port:
        nonebot.logger.opt(colors=True).warning("<r>端口被占用，可能原因为图片存储服务器未正常退出，不再重复创建</r>")
    else:
        server_process = subprocess.Popen(command, cwd=current_folder, shell=True)
        nonebot.logger.opt(colors=True).info("<y>图片存储服务器启动成功</y>")


@driver.on_shutdown
def _kill_server():
    global server_process
    if server_process:
        server_process.kill()
        nonebot.logger.opt(colors=True).info("<y>图片存储服务器关闭成功</y>")
    else:
        nonebot.logger.opt(colors=True).warning("<y>图片存储服务器未正常退出</y>")