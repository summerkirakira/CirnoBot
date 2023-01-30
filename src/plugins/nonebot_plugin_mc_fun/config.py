from pydantic import BaseSettings
import os

current_folder = os.path.dirname(__file__)

default_config = {
    "server_uri": "",
    "server_address": "",
    "server_name": "",
    "is_focus": [],
    "superuser": [],

    "enable_placeholder_api": False,
    "show_welcome_message": False,
    "welcome_message": "§6欢迎小伙伴%player_name%加入服务器～",
    "welcome_message_broadcast": "§6欢迎小伙伴%player_name%加入服务器～",

    "auto_reply": True,
    "auto_reply_dict": {"hello": "world"},
    "auto_reply_start": ".",

    "forward_to_qq": True,
    "sync_with_qq": True,
    "forward_enabled_groups": [],

    "join_event_qq_broadcast": True,
    "join_event_qq_message": "小伙伴%player_name%加入服务器%server_name%了哦～当前服务器人数%server_online%人",
    "join_event_qq_broadcast_group": [],

    "leave_event_qq_broadcast": True,
    "leave_event_qq_message": "小伙伴%player_name%离开服务器了呢～当前服务器人数%server_online%人哦",
    "leave_event_qq_broadcast_group": [],

    "command_translator": True,
    "translate_commands": {"say": "say helloworld"},

    "server_status_display": True,

    "player_search": True,

    "white_list": True,
    "white_list_players": {},

    "allow_message_transfer": True,

    "op": True,

    "server_command": True,

    "enable_death_message": True,

    "death_message": [
        {
            "regex": "§6%player_name%§r被§6%killer_name%§r杀死了",
            "message": "§6%player_name%§r被§6%killer_name%§r杀死了",
        }
    ]

}


