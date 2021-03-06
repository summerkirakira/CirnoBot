from .investigator import Investigator
from .dices import Dices
from nonebot.adapters.onebot.v11 import Event
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from .messages import help_messages

import ujson as json

import os
import re
_cachepath = os.path.join("data", "coc_cards.json")


# def get_group_id(event: Event):
#     if type(event) is GroupMessageEvent:
#         return str(event.group_id)
#     else:
#         return "0"


class Cards():
    def __init__(self) -> None:
        self.data: dict = {}

    def save(self) -> None:
        with open(_cachepath, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False)

    def load(self) -> None:
        with open(_cachepath, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def update(self, message: dict, inv_dict: dict, qid: str = "", save: bool = True):
        group_id = message["server_uri"]
        if not self.data.get(group_id):
            self.data[group_id] = {}
        self.data[group_id].update(
            {qid if qid else message["name"]: inv_dict})
        if save:
            self.save()

    def get(self, message: dict, qid: str = "") -> dict:
        group_id = message["server_uri"]
        if self.data.get(group_id):
            if self.data[group_id].get(qid if qid else message["name"]):
                return self.data[group_id].get(qid if qid else message["name"])
        else:
            return None

    def delete(self, message: dict, qid: str = "", save: bool = True) -> bool:
        if self.get(message, qid=qid):
            if self.data[message["server_uri"]].get(qid if qid else message["name"]):
                self.data[message["server_uri"]].pop(
                    qid if qid else message["name"])
            if save:
                self.save()
            return True
        return False

    def delete_skill(self, message: dict, skill_name: str, qid: str = "", save: bool = True) -> bool:
        if self.get(message, qid=qid):
            data = self.get(message, qid=qid)
            if data["skills"].get(skill_name):
                data["skills"].pop(skill_name)
                self.update(message, data, qid=qid, save=save)
                return True
        return False


cards = Cards()
cache_cards = Cards()
attrs_dict: dict = {
    "??????": ["name", "??????", "??????"],
    "??????": ["age", "??????"],
    "??????": ["str", "??????"],
    "??????": ["con", "??????"],
    "??????": ["siz", "??????"],
    "??????": ["dex", "??????"],
    "??????": ["app", "??????"],
    "??????": ["int", "??????", "??????"],
    "??????": ["pow", "??????"],
    "??????": ["edu", "??????"],
    "??????": ["luc", "??????"],
    "??????": ["san", "??????"],
}


def set_handler(message: dict, args: str):
    if not args:
        if cache_cards.get(message):
            card_data = cache_cards.get(message)
            cards.update(message, inv_dict=card_data)
            inv = Investigator().load(card_data)
            return "???????????????????????????????????????\n" + inv.output()
        else:
            return "????????????????????????????????????coc??????????????????"
    else:
        args = args.split(" ")
        if cards.get(message):
            card_data = cards.get(message)
            inv = Investigator().load(card_data)
        else:
            return "?????????????????????????????????????????????set????????????????????????"
        if len(args) >= 2:
            for attr, alias in attrs_dict.items():
                if args[0] in alias:
                    if attr == "??????":
                        inv.__dict__[alias[0]] = args[1]
                    else:
                        try:
                            inv.__dict__[alias[0]] = int(args[1])
                        except ValueError:
                            return "??????????????????????????????"
                    cards.update(message, inv.__dict__)
                    return "???????????????%s??????%s" % (attr, args[1])
            try:
                inv.skills[args[0]] = int(args[1])
                cards.update(message, inv.__dict__)
                return "???????????????%s????????????%s" % (args[0], args[1])
            except ValueError:
                return "??????????????????????????????"


def show_handler(message: dict, args: str):
    r = []
    if not args:
        if cards.get(message):
            card_data = cards.get(message)
            inv = Investigator().load(card_data)
            r.append("?????????????????????\n" + inv.output())
        if cache_cards.get(message):
            card_data = cache_cards.get(message)
            inv = Investigator().load(card_data)
            r.append("?????????????????????\n" + inv.output())
    elif args == "s":
        if cards.get(message):
            card_data = cards.get(message)
            inv = Investigator().load(card_data)
            r.append(inv.skills_output())
    elif re.search(r"\[cq:at,qq=\d+\]", args):
        qid = re.search(r"\[cq:at,qq=\d+\]", args).group()[10:-1]
        if cards.get(message, qid=qid):
            card_data = cards.get(message, qid=qid)
            inv = Investigator().load(card_data)
            r.append("?????????????????????\n" + inv.output())
            if args[0] == "s":
                r.append(inv.skills_output())
    if not r:
        r.append("?????????/????????????")
    return r


def del_handler(message: dict, args: str):
    r = []
    args = args.split(" ")
    for arg in args:
        if not arg:
            pass
        elif arg == "c" and cache_cards.get(message):
            if cache_cards.delete(message, save=False):
                r.append("??????????????????????????????")
        elif arg == "card" and cards.get(message):
            if cards.delete(message):
                r.append("?????????????????????????????????")
        else:
            if cards.delete_skill(message, arg):
                r.append("???????????????"+arg)
    if not r:
        r.append(help_messages.del_)
    return r


def sa_handler(message: dict, args: str):
    if not args:
        return help_messages.sa
    elif not cards.get(message):
        return "????????????set??????????????????????????????????????????????????????"
    for attr, alias in attrs_dict.items():
        if args in alias:
            arg = alias[0]
            break
    card_data = cards.get(message)
    dices = Dices()
    dices.a = True
    dices.anum = card_data[arg]
    return dices.roll()
