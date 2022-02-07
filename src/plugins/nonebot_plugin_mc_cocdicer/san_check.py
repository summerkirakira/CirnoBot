from .dices import Dices
from .messages import help_messages
from .cards import cards

from nonebot.adapters.onebot.v11 import Event

import re


def number_or_dice(arg: str):
    if "d" in arg:
        d = Dices()
        dices = re.search(r"\d+d", arg)
        if dices:
            d.dices = int(dices.group()[:-1])
        faces = re.search(r"d\d+", arg)
        if faces:
            d.faces = int(faces.group()[1:])
        d.roll()
        return d
    else:
        return int(arg)


def sc(arg: str, message:dict) -> str:
    args = arg.split(" ")
    a_num = success = failure = None
    using_card = False
    for arg in args:
        if not arg:
            continue
        elif re.search(r"\/", arg):
            success = re.search(r"\d*d\d+|\d+", arg)
            failure = re.search(r"[\/]+(\d*d\d+|\d+)", arg)
        elif re.search(r"\d+", arg):
            a_num = re.search(r"\d+", arg)
    if (not success) or (not failure):
        return help_messages.sc
    if (not a_num) and cards.get(message):
        card_data = cards.get(message)
        a_num = card_data["san"]
        using_card = True
    elif a_num:
        card_data = {"san": int(a_num.group()), "name": "该调查员"}
    elif not a_num:
        return help_messages.sc
    check_dice = Dices()
    check_dice.a = True
    check_dice.anum = card_data["san"]
    success = number_or_dice(success.group())
    failure = number_or_dice(failure.group()[1:])
    r = "San Check" + check_dice.roll()[4:]
    result = success if check_dice.result <= check_dice.anum else failure
    r += "\n理智降低了"
    if type(result) is int:
        r += "%d点" % result
    else:
        r = r + result._head + str(result.result)
        result = result.result
    if result >= card_data["san"]:
        r += "\n%s陷入了永久性疯狂" % card_data["name"]
    elif result >= (card_data["san"] // 5):
        r += "\n%s陷入了不定性疯狂" % card_data["name"]
    elif result >= 5:
        r += "\n%s陷入了临时性疯狂" % card_data["name"]
    if using_card:
        card_data["san"] -= result
        cards.update(message, card_data)
    return r
