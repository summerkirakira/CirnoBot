from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
from .config import get_config, current_folder
import nonebot

bot_config = nonebot.get_driver().config


def measure_length(text, font):
    lines = textwrap.wrap(text, width=40)
    y_text = 0
    for line in lines:
        width, height = font.getsize(line)
        y_text += width
    return y_text


def make_single_plugin_image(plugin_dict: dict, index):
    name_font = ImageFont.truetype(os.path.join(current_folder, 'font', 'WeiRuanYaHei-1.ttf'), 30)
    text_font = ImageFont.truetype(os.path.join(current_folder, 'font', 'WeiRuanYaHei-1.ttf'), 30)

    description_box_width = 1500

    message_list = []
    message_preprocessed = ""
    for ch in plugin_dict["description"]:
        if measure_length(message_preprocessed + ch, text_font) > description_box_width:
            message_list.append(message_preprocessed)
            message_preprocessed = ch
        else:
            message_preprocessed += ch
    if message_preprocessed:
        message_list.append(message_preprocessed)

    description_box_height = len(message_list) * 40 + 30
    if len(message_list) == 1:
        name_margin_top = 15
    else:
        name_margin_top = len(message_list) * 20
    if index % 2 == 0:
        plugin_image = Image.new("RGBA", (2700, description_box_height), color="#f2f2f3")
    else:
        plugin_image = Image.new("RGBA", (2700, description_box_height), color="#ffffff")
    message_drawer = ImageDraw.Draw(plugin_image)
    NAME_MARGIN_LEFT = 30
    NAME_BLOCK_WIDTH = 300
    VERSION_BLOCK_WIDTH = 400
    message_drawer.text((NAME_MARGIN_LEFT, name_margin_top), text=plugin_dict["series"], font=name_font, fill="#000000")

    message_drawer.text((NAME_MARGIN_LEFT + 300, name_margin_top), text=plugin_dict["command"],
                        font=text_font, fill="#000000")


    message_drawer.text((NAME_MARGIN_LEFT + NAME_BLOCK_WIDTH + 400, name_margin_top), text=plugin_dict["parameters"],
                        font=text_font, fill="#000000")
    if len(message_list) == 1:
        message_drawer.text((NAME_MARGIN_LEFT + NAME_BLOCK_WIDTH + VERSION_BLOCK_WIDTH + 700, name_margin_top), text=
                            plugin_dict["description"], font=text_font, fill="#000000")
    else:
        current_position = 20
        for message in message_list:
            message_drawer.text((NAME_MARGIN_LEFT + NAME_BLOCK_WIDTH + VERSION_BLOCK_WIDTH + 700, current_position),
                                text=message, font=text_font, fill="#000000")
            current_position += 40
    return plugin_image


async def make_plugins_image(plugins_list: list):
    name_font = ImageFont.truetype(os.path.join(current_folder, 'font', 'WeiRuanYaHei-1.ttf'), 30)
    plugin_image_list = []
    for i in range(len(plugins_list)):
        if 'description' not in plugins_list[i]:
            plugins_list[i]['description'] = ' '
        plugin_image_list.append(make_single_plugin_image(plugins_list[i], i))
    plugins_image_height = 70
    for image in plugin_image_list:
        plugins_image_height += image.height

    plugins_image = Image.new("RGBA", (2700, plugins_image_height), color="#FFFFFF")

    NAME_MARGIN_TOP = 20
    drawer = ImageDraw.Draw(plugins_image)
    drawer.text((100, NAME_MARGIN_TOP), text="组件", font=name_font, fill="#000000")
    drawer.text((400, NAME_MARGIN_TOP), text="命令", font=name_font, fill="#000000")
    drawer.text((1000, NAME_MARGIN_TOP), text="参数", font=name_font, fill="#000000")
    drawer.text((2000, NAME_MARGIN_TOP), text="简介", font=name_font, fill="#000000")
    current_position = 70
    for image in plugin_image_list:
        plugins_image.paste(image, (0, current_position, image.width, current_position + image.height), mask=image)
        current_position += image.height
    plugins_image.save(os.path.join(current_folder, 'font', 'plugins_image.png'))
    with open(os.path.join(current_folder, 'font', 'plugins_image.png'), 'rb') as f:
        return f.read()


async def get_help():
    command_list = get_config()
    new_list = []
    for series in command_list:
        if series['plugin_name'] not in bot_config.plugins_config:
            continue
        for command in series['commands']:
            new_list.append({
                'series': series['series'],
                'command': command['command'],
                'parameters': command['parameters'],
                'description': command['description']
            })
    return await make_plugins_image(new_list)

if __name__ == "__main__":
    command_list = get_config()
    new_list = []
    for series in command_list:
        for command in series['commands']:
            new_list.append({
                'series': series['series'],
                'command': command['command'],
                'parameters': command['parameters'],
                'description': command['description']
            })
    make_plugins_image(new_list)