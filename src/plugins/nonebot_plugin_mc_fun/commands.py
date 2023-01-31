from nonebot import on_startswith, on_message
from nonebot import Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.adapters.onebot.v11.message import MessageSegment, Message
from .data_source import save_specific_config
from .message_image_generater import make_chat_image, make_plugins_image
from .data_source import get_config, save_config_to_yaml
import time
from nonebot.plugin import require
from .util import get_group_bind_server

plugin_mc_info = require('nonebot_plugin_mc_info')

server_status = on_startswith(msg=".mc", ignorecase=True, priority=15)
# 服务器状态查询
player_search = on_startswith(".玩家查询", priority=16)
# 玩家查询
set_white_list = on_startswith(".申请白名单", priority=14)
# 申请白名单
remove_white_list = on_startswith(".踢出白名单", priority=17)
# 移除白名单
white_list_on = on_startswith(".开启白名单", priority=15)
# 打开白名单
white_list_off = on_startswith(".关闭白名单", priority=15)
# 关闭白名单
set_op = on_startswith(".添加管理员", priority=18)
# 添加OP
remove_op = on_startswith(".移除管理员", priority=19)
# 移除OP
tell = on_startswith(".转发", priority=20)
# 与服务器内玩家聊天
sync = on_message(priority=25, block=False)
# 同步消息
chat_record = on_startswith(".聊天记录", priority=20)
# 获取服务器最近十条消息
set_current_server = on_startswith(".绑定服务器", priority=18)
# 绑定优先服务器
set_entries = on_startswith(".mc词条", priority=12)
# 设定mc词条
execute_command = on_startswith(".指令", priority=16)
# 执行mc命令
get_plugin_list = on_startswith(".插件列表", priority=16)
# 获取插件列表
get_format_api_message = on_startswith(".api", priority=16)
# 使用PlaceHolderAPI格式化信息


@server_status.handle()
async def _server_status(bot: Bot, event: GroupMessageEvent):
    group_id = event.group_id
    server_config, server = get_group_bind_server(group_id)
    if not server_config:
        await bot.send(event, Message(MessageSegment.text("请先添加群绑定服务器哦～")))
        return
    if not server.connected:
        await bot.send(event, Message(MessageSegment.text("服务器未连接呢～")))
        return
    server_info: dict = await server.get_server_info()
    m, s = divmod(server_info['health']['uptime'], 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    if "server_name" in server_config:
        server_info["name"] = server_config["server_name"]
    message = f"服务器名称: {server_info['name']}\n服务器地址: {server_config['server_address']}\n" \
              f"服务器版本: {server_info['version'].split('(')[1].replace('MC: ', '').replace(')', '')}\n" \
              f"服务器TPS: {server_info['tps']}\n" \
              f"在线时间: {d}天{h}小时{m}分钟\n" \
              f"内存占用: {round((server_info['health']['maxMemory'] - server_info['health']['freeMemory'])/1000000000, 2)}G/" \
              f"{round(server_info['health']['maxMemory']/1000000000, 2)}G(" \
              f"{round((1-server_info['health']['freeMemory'] / server_info['health']['maxMemory']) * 100, 2)}%)\n"
    players = await server.get_players()
    player_string = ",".join([player['displayName'] for player in players])
    message += f"当前在线: {player_string}({len(players)}人)"
    await bot.send(event, Message(MessageSegment.text(message)))
    return


@player_search.handle()
async def _player_search(bot: Bot, event: GroupMessageEvent):
    player_id = event.get_plaintext().replace(".玩家查询", "").strip()
    server_config, server = get_group_bind_server(event.group_id)
    if not server_config:
        await bot.send(event, Message(MessageSegment.text("请先添加群绑定服务器哦～")))
        return
    if not server.connected:
        await bot.send(event, Message(MessageSegment.text("服务器未连接呢～")))
        return

    online_players = await server.get_players()
    all_players = await server.get_all_players()
    for player in all_players:
        key = server.get_name_key(player)
        if player[key].lower() == player_id.lower():
            for online_player in online_players:
                if online_player["uuid"] == player['uuid']:
                    player_message = f"玩家id: {online_player['displayName']}\n玩家状态: 在线\n是否管理员: {'是' if online_player['op'] else '否'}\n" \
                                     f"玩家血量: {int(online_player['health'])}({round(online_player['health'] / 20 * 100)}%)\n" \
                                     f"玩家饥饿值: {int(online_player['hunger'])}({round(online_player['hunger'] / 20 * 100)}%)\n" \
                                     f"玩家位置: {int(online_player['location'][0])},{int(online_player['location'][1])},{int(online_player['location'][2])}"
                    if server_config["enable_placeholder_api"]:
                        player_uuid = await server.get_uuid_from_name(player_id)
                        if player_uuid:
                            extra_info = await server.placeholder_api("%player_last_join%#%player_ping%",
                                                                      uuid=player_uuid)
                            [last_play_time, player_ping] = extra_info.split("#")
                            time_string = time.strftime("%m月%d日 %H时%M分", time.localtime(int(last_play_time) / 1000))
                            player_message += f"\n玩家延迟: {player_ping}ms\n最后登录: {time_string}"
                    await bot.send(event, Message(MessageSegment.text(player_message)))
                    return
            key = server.get_name_key(player)
            player_message = f"玩家id: {player[key]}\n玩家状态: 离线\n是否管理员: {'是' if player['op'] else '否'}"
            if server_config["enable_placeholder_api"]:
                player_uuid = await server.get_uuid_from_name(player_id)
                if player_uuid:
                    extra_info = await server.placeholder_api("%player_last_join%#%player_ping%", uuid=player_uuid)
                    [last_play_time, player_ping] = extra_info.split("#")
                    time_string = time.strftime("%m月%d日 %H时%M分", time.localtime(int(last_play_time) / 1000))
                    player_message += f"\n最后登录: {time_string}"
            await bot.send(event, Message(MessageSegment.text(player_message)))
            return
    await bot.send(event, Message(MessageSegment.text("未找到指定玩家呢～请检查id是否输入正确哦～")))


@set_white_list.handle()
async def _set_white_list(bot: Bot, event: GroupMessageEvent):
    player_id = event.get_plaintext().replace(".申请白名单", "").strip()
    server_config, server = get_group_bind_server(event.group_id)
    if not server_config:
        await bot.send(event, Message(MessageSegment.text("请先添加群绑定服务器哦～")))
        return
    if not server.connected:
        await bot.send(event, Message(MessageSegment.text("服务器未连接呢～")))
        return
    if not server_config["white_list"]:
        await bot.send(event, Message(MessageSegment.text("白名单未启用呢～")))
        return
    if event.sender.user_id not in server_config["white_list_players"]:
        server_config["white_list_players"][event.sender.user_id] = player_id
        response = await server.add_white_list(player_id)
        if response == "No whitelist":
            await bot.send(event, Message(MessageSegment.text("服务端白名单未启用呢～")))
            return
        save_specific_config(server_config)
        await bot.send(event, Message(MessageSegment.text(f"小伙伴申请的id:{player_id}已加入白名单了哦～")))
        return
    else:
        if player_id == server_config["white_list_players"][event.sender.user_id]:
            await server.add_white_list(player_id)
            await bot.send(event, Message(MessageSegment.text(f"小伙伴申请的id:{player_id}已在白名单内了哦～")))
            return
        old_id = server_config["white_list_players"][event.sender.user_id]
        server_config["white_list_players"][event.sender.user_id] = player_id
        await server.add_white_list(player_id)
        await server.remove_white_list(old_id)
        save_specific_config(server_config)
        await bot.send(event, Message(MessageSegment.text(f"已将小伙伴的id:{old_id}替换为{player_id}了哦～")))
        return


@remove_white_list.handle()
async def _remove_white_list(bot: Bot, event: GroupMessageEvent):
    player_id = event.get_plaintext().replace(".踢出白名单", "").strip()
    server_config, server = get_group_bind_server(event.group_id)
    if not server_config:
        await bot.send(event, Message(MessageSegment.text("请先添加群绑定服务器哦～")))
        return
    if not server.connected:
        await bot.send(event, Message(MessageSegment.text("服务器未连接呢～")))
        return
    if not server_config["white_list"]:
        await bot.send(event, Message(MessageSegment.text("白名单未启用呢～")))
        return
    if event.sender.user_id in server_config["superuser"]:
        await server.remove_white_list(player_id)
        await bot.send(event, Message(MessageSegment.text(f"玩家{player_id}移除白名单成功哦～")))
        return
    else:
        await server.remove_white_list(player_id)
        await bot.send(event, Message(MessageSegment.text(f"小伙伴没有权限这么做呢～")))
        return


@set_op.handle()
async def _set_op(bot: Bot, event: GroupMessageEvent):
    player_id = event.get_plaintext().replace(".添加管理员", "").strip()
    sender_id = event.sender.user_id
    server_config, server = get_group_bind_server(event.group_id)
    if not server_config:
        await bot.send(event, Message(MessageSegment.text("请先添加群绑定服务器哦～")))
        return
    if not server.connected:
        await bot.send(event, Message(MessageSegment.text("服务器未连接呢～")))
        return
    if not server_config["op"]:
        await bot.send(event, Message(MessageSegment.text("当前未启用op设置呢～")))
        return
    if sender_id in server_config["superuser"]:
        await server.set_op(player_id)
        await bot.send(event, Message(MessageSegment.text(f"已将{player_id}设为服务器管理员～")))
        return
    else:
        await bot.send(event, Message(MessageSegment.text(f"小伙伴没有权限执行此操作呢～")))
        return


@remove_op.handle()
async def _remove_op(bot: Bot, event: GroupMessageEvent):
    player_id = event.get_plaintext().replace(".移除管理员", "").strip()
    sender_id = event.sender.user_id
    server_config, server = get_group_bind_server(event.group_id)
    if not server_config:
        await bot.send(event, Message(MessageSegment.text("请先添加群绑定服务器哦～")))
        return
    if not server.connected:
        await bot.send(event, Message(MessageSegment.text("服务器未连接呢～")))
        return
    if not server_config["op"]:
        await bot.send(event, Message(MessageSegment.text("当前未启用op设置呢～")))
        return
    if sender_id in server_config["superuser"]:
        await server.remove_op(player_id)
        await bot.send(event, Message(MessageSegment.text(f"已将{player_id}移除服务器管理员～")))
        return
    else:
        await bot.send(event, Message(MessageSegment.text(f"小伙伴没有权限执行此操作呢～")))
        return


@tell.handle()
async def _tell(bot: Bot, event: GroupMessageEvent):
    message = event.get_plaintext().replace(".转发", "").strip()
    server_config, server = get_group_bind_server(event.group_id)
    if not server_config:
        await bot.send(event, Message(MessageSegment.text("请先添加群绑定服务器哦～")))
        return
    if not server.connected:
        await bot.send(event, Message(MessageSegment.text("服务器未连接呢～")))
        return
    if not server_config["allow_message_transfer"]:
        await bot.send(event, Message(MessageSegment.text("消息转接服务未开启的说～")))
        return
    sender_nickname = event.sender.nickname
    await server.broadcast(f"<{sender_nickname}> {message}")
    await bot.send(event, Message(MessageSegment.text("消息转发成功的说～")))
    return


@chat_record.handle()
async def _chat_record(bot: Bot, event: GroupMessageEvent):
    server_config, server = get_group_bind_server(event.group_id)
    if not server_config:
        await bot.send(event, Message(MessageSegment.text("请先添加群绑定服务器哦～")))
        return
    if not server.connected:
        await bot.send(event, Message(MessageSegment.text("服务器未连接呢～")))
        return
    if len(server.player_chat) == 0:
        await bot.send(event, Message(MessageSegment.text("当前聊天记录为空呢～")))
        return
    image = await make_chat_image(server.player_chat if len(server.player_chat) < 10 else server.player_chat[-10:])
    if image:
        await bot.send(event, Message(MessageSegment.image(image)))
        return
    else:
        await bot.send(event, Message(MessageSegment.text("由于未知原因生成出错了呢～")))
        return


@set_current_server.handle()
async def _set_current_server(bot: Bot, event: GroupMessageEvent):
    if event.sender.role == "ADMIN" or "OWNER":
        server_configs = get_config()
        server_uri = event.get_plaintext().replace(".绑定服务器", "").strip()
        if not server_uri:
            server_uri = "placeholder"
        if not server_configs:
            await bot.send(event, Message(MessageSegment.text("当前未配置服务器呢～请在配置文件中添加端口和密钥哦～")))
            return
        is_find = False
        for config in server_configs:
            if config["server_uri"] == server_uri or server_uri == config["server_address"]:
                if event.group_id in config["is_focus"]:
                    config["is_focus"].remove(event.group_id)
                config["is_focus"].append(event.group_id)
                is_find = True
                break
        if not is_find:
            server_string = "\n".join([config["server_uri"] for config in server_configs])
            message = f"未找到指定的服务器呢～当前已配置服务器:\n{server_string}\n请小伙伴注意输入端口号哦～"
            await bot.send(event, Message(MessageSegment.text(message)))
            return
        else:
            for config in server_configs:
                if not (config["server_uri"] == server_uri or server_uri == config["server_address"]):
                    if event.group_id in config["is_focus"]:
                        config["is_focus"].remove(event.group_id)
            save_config_to_yaml(server_configs)
            await bot.send(event, Message(MessageSegment.text(f"群绑定服务器已更换为了{server_uri}的说～")))
            return
    else:
        await bot.send(event, Message(MessageSegment.text("仅管理员和群主可以切换服务器的说～")))
        return


@white_list_on.handle()
async def _white_list_on(bot: Bot, event: GroupMessageEvent):
    server_config, server = get_group_bind_server(event.group_id)
    if not server_config:
        await bot.send(event, Message(MessageSegment.text("请先添加群绑定服务器哦～")))
        return
    if not server.connected:
        await bot.send(event, Message(MessageSegment.text("服务器未连接呢～")))
        return
    if event.sender.user_id in server_config["superuser"]:
        await server.white_list_on()
        await bot.send(event, Message(MessageSegment.text("服务器白名单已开启的说～")))
        return
    else:
        await bot.send(event, Message(MessageSegment.text("小伙伴权限不足哦～")))
        return


@white_list_off.handle()
async def _white_list_off(bot: Bot, event: GroupMessageEvent):
    server_config, server = get_group_bind_server(event.group_id)
    if not server_config:
        await bot.send(event, Message(MessageSegment.text("请先添加群绑定服务器哦～")))
        return
    if not server.connected:
        await bot.send(event, Message(MessageSegment.text("服务器未连接呢～")))
        return
    if event.sender.user_id in server_config["superuser"]:
        await server.white_list_off()
        await bot.send(event, Message(MessageSegment.text("服务器白名单关闭了哦～")))
        return
    else:
        await bot.send(event, Message(MessageSegment.text("小伙伴权限不足哦～")))
        return


@set_entries.handle()
async def _set_entries(bot: Bot, event: GroupMessageEvent):
    server_config, server = get_group_bind_server(event.group_id)
    if not server_config:
        await bot.send(event, Message(MessageSegment.text("请先添加群绑定服务器哦～")))
        return
    if not server.connected:
        await bot.send(event, Message(MessageSegment.text("服务器未连接呢～")))
        return
    if not server_config["auto_reply"]:
        await bot.send(event, Message(MessageSegment.text("MC词条未开启的说～")))
        return
    message = event.get_plaintext().replace(".mc词条", "").strip()
    parameter_list = message.split('#')
    if len(parameter_list) != 2:
        await bot.send(event, Message(MessageSegment.text("请小伙伴检查词条参数是否正确哦～词条和内容用'#'分隔且内容内不能出现'#'哦～")))
        return
    server_config["auto_reply_dict"][parameter_list[0]] = parameter_list[1]
    save_specific_config(server_config)
    await bot.send(event, Message(MessageSegment.text("MC词条编辑成功哦～")))
    return


@execute_command.handle()
async def _execute_command(bot: Bot, event: GroupMessageEvent):
    server_config, server = get_group_bind_server(event.group_id)
    if not server_config:
        await bot.send(event, Message(MessageSegment.text("请先添加群绑定服务器哦～")))
        return
    if not server.connected:
        await bot.send(event, Message(MessageSegment.text("服务器未连接呢～")))
        return
    command = event.get_plaintext().replace(".指令", "").strip()
    if not server_config["server_command"]:
        await bot.send(event, Message(MessageSegment.text("服务器指令被关闭了哦～")))
        return
    if event.sender.user_id not in server_config["superuser"]:
        await bot.send(event, Message(MessageSegment.text("小伙伴权限不足的说～")))
        return
    await server.execute_command(command.replace('/', ''))
    await bot.send(event, Message(MessageSegment.text(f"指令执行成功的说～{'执行指令无需使用/哦～' if '/' in command else ''}")))
    return


@get_plugin_list.handle()
async def _get_plugin_list(bot: Bot, event: GroupMessageEvent):
    server_config, server = get_group_bind_server(event.group_id)
    if not server_config:
        await bot.send(event, Message(MessageSegment.text("请先添加群绑定服务器哦～")))
        return
    if not server.connected:
        await bot.send(event, Message(MessageSegment.text("服务器未连接呢～")))
        return
    if event.sender.user_id not in server_config["superuser"]:
        await bot.send(event, Message(MessageSegment.text("小伙伴权限不足呢～")))
        return
    image = await make_plugins_image(await server.get_plugins())
    await bot.send(event, Message(MessageSegment.image(image)))


@sync.handle()
async def _sync_with_qq(bot: Bot, event: GroupMessageEvent):
    server_config, server = get_group_bind_server(event.group_id)
    if not server_config:
        return
    if not server.connected:
        return
    sender_nickname = (await bot.call_api(api="get_group_member_info", group_id=event.group_id, user_id=event.sender.user_id))["card"]
    message = event.get_plaintext()
    if "sync_with_qq" not in server_config or server_config["sync_with_qq"]:
        group_id: int = event.group_id
        group_info = await bot.call_api('get_group_info', group_id=group_id)
        await server.broadcast(f"「{group_info['group_name']}」<{sender_nickname}> {message}")


@get_format_api_message.handle()
async def _get_format_api_message(bot: Bot, event: GroupMessageEvent):
    server_config, server = get_group_bind_server(event.group_id)
    if not server_config:
        await bot.send(event, Message(MessageSegment.text("请先添加群绑定服务器哦～")))
        return
    if not server.connected:
        await bot.send(event, Message(MessageSegment.text("服务器未连接呢～")))
        return
    if event.sender.user_id not in server_config["superuser"]:
        await bot.send(event, Message(MessageSegment.text("小伙伴权限不足呢～")))
        return
    if not server_config["enable_placeholder_api"]:
        await bot.send(event, Message(MessageSegment.text("PlaceHolderAPI未开启呢～")))
        return
    try:
        message = await server.placeholder_api(event.get_plaintext().replace(".api", "").strip())
        await bot.send(event, Message(MessageSegment.text(message)))
    except Exception as e:
        await bot.send(event, Message(MessageSegment.text(f"格式化消息失败了呢～{e}")))
        return

