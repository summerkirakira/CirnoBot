from PIL import Image, ImageDraw, ImageFont
import os
import random
import time
import textwrap

from .config import current_folder


def circle_corner(img, radii):
    """
    圆角处理
    :param img: 源图象。
    :param radii: 半径，如：30。
    :return: 返回一个圆角处理后的图象。
    """

    circle = Image.new('L', (radii * 2, radii * 2), 0)  # 创建一个黑色背景的画布
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radii * 2, radii * 2), fill=255)  # 画白色圆形

    # 原图
    img = img.convert("RGBA")
    w, h = img.size

    # 画4个角（将整圆分离为4个部分）
    alpha = Image.new('L', img.size, 255)
    alpha.paste(circle.crop((0, 0, radii, radii)), (0, 0))  # 左上角
    alpha.paste(circle.crop((radii, 0, radii * 2, radii)), (w - radii, 0))  # 右上角
    alpha.paste(circle.crop((radii, radii, radii * 2, radii * 2)), (w - radii, h - radii))  # 右下角
    alpha.paste(circle.crop((0, radii, radii, radii * 2)), (0, h - radii))  # 左下角
    # alpha.show()

    img.putalpha(alpha)  # 白色区域透明可见，黑色区域不可见
    return img


def make_single_chat_image(name: str, message: str, time: str):
    nickname_font = ImageFont.truetype(os.path.join(current_folder, 'font', 'WeiRuanYaHei-1.ttf'), 30)
    text_font = ImageFont.truetype(os.path.join(current_folder, 'font', 'WeiRuanYaHei-1.ttf'), 30)
    time_font = ImageFont.truetype(os.path.join(current_folder, 'font', 'WeiRuanYaHei-1.ttf'), 15)

    single_image = Image.new(mode='RGBA', size=(800, 600))

    draw = ImageDraw.Draw(single_image)
    message_list = []

    message_box_width = 800

    message_preprocessed = ""
    for ch in message:
        if draw.textlength(message_preprocessed + ch, text_font) > message_box_width:
            message_list.append(message_preprocessed)
            message_preprocessed = ch
        else:
            message_preprocessed += ch
    if message_preprocessed:
        message_list.append(message_preprocessed)

    message_box_height = len(message_list) * 40 + 30

    image_box = Image.new('RGBA', (message_box_width + 30, message_box_height + 40), (255, 255, 255))
    message_box_draw = ImageDraw.Draw(image_box)

    nickname_color = [
        "#3399ff",
        "#ffd11a",
        "#66ccff",
        "#33cc33",
        "#ff6699",
        "#751aff",
        "#1aff1a",
        "#ff33ff",
        "#ff661a"
    ]

    message_box_draw.text((15, 7), text=name, font=nickname_font, fill=random.choice(nickname_color))
    current_position = 50
    for message in message_list:
        message_box_draw.text((15, current_position), text=message, font=text_font, fill="#000000")
        current_position += 40
    message_box_draw.text((message_box_width - draw.textlength(time, time_font), message_box_height + 10),
                          text=time, font=time_font, fill="#94918f")
    image_box = circle_corner(image_box, 20)
    return image_box


async def make_chat_image(message_list: list):
    image_box_list = []
    for message in message_list:
        send_time = time.localtime(message['time']/1000)
        time_list = time.strftime("%H:%M", send_time).split(":")
        if int(time_list[0]) > 12:
            time_string = f"下午 {int(time_list[0])-12}:{time_list[1]}"
        else:
            time_string = f"上午 {int(time_list[0])}:{time_list[1]}"

        image_box_list.append(make_single_chat_image(message["name"], message["message"], time_string))
    if not image_box_list:
        return None
    image_photo_height = 0
    for image_box in image_box_list:
        image_photo_height += image_box.height + 50
    image_photo_height -= int(60 * len(message_list) / 10)
    image_photo = Image.new("RGBA", (950, image_photo_height), (234, 225, 213))
    current_position_height = 30
    for image_box in image_box_list:
        image_photo.paste(image_box, (20, current_position_height, 20+image_box.width,
                                      current_position_height+image_box.height),
                          mask=image_box
                          )
        current_position_height += image_box.height + 40
    image_photo = circle_corner(image_photo, 40)
    image_photo.save(os.path.join(current_folder, 'font', 'chat_image.png'))
    with open(os.path.join(current_folder, 'font', 'chat_image.png'), 'rb') as f:
        return f.read()


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

    description_box_width = 1200

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
        plugin_image = Image.new("RGBA", (2000, description_box_height), color="#f2f2f3")
    else:
        plugin_image = Image.new("RGBA", (2000, description_box_height), color="#ffffff")
    message_drawer = ImageDraw.Draw(plugin_image)
    NAME_MARGIN_LEFT = 30
    NAME_BLOCK_WIDTH = 300
    VERSION_BLOCK_WIDTH = 400
    message_drawer.text((NAME_MARGIN_LEFT, name_margin_top), text=plugin_dict["name"], font=name_font, fill="#000000")

    if len(plugin_dict["version"]) > 25:
        plugin_dict["version"] = plugin_dict["version"][:25]

    message_drawer.text((NAME_MARGIN_LEFT + NAME_BLOCK_WIDTH, name_margin_top), text=plugin_dict["version"],
                        font=text_font, fill="#000000")
    if len(message_list) == 1:
        message_drawer.text((NAME_MARGIN_LEFT + NAME_BLOCK_WIDTH + VERSION_BLOCK_WIDTH, name_margin_top), text=
                            plugin_dict["description"], font=text_font, fill="#000000")
    else:
        current_position = 20
        for message in message_list:
            message_drawer.text((NAME_MARGIN_LEFT + NAME_BLOCK_WIDTH + VERSION_BLOCK_WIDTH, current_position),
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

    plugins_image = Image.new("RGBA", (2000, plugins_image_height), color="#FFFFFF")

    NAME_MARGIN_TOP = 20
    drawer = ImageDraw.Draw(plugins_image)
    drawer.text((40, NAME_MARGIN_TOP), text="插件名", font=name_font, fill="#000000")
    drawer.text((350, NAME_MARGIN_TOP), text="版本", font=name_font, fill="#000000")
    drawer.text((1200, NAME_MARGIN_TOP), text="简介", font=name_font, fill="#000000")
    current_position = 70
    for image in plugin_image_list:
        plugins_image.paste(image, (0, current_position, image.width, current_position + image.height), mask=image)
        current_position += image.height
    plugins_image.save(os.path.join(current_folder, 'font', 'plugins_image.png'))
    with open(os.path.join(current_folder, 'font', 'plugins_image.png'), 'rb') as f:
        return f.read()


if __name__ == "__main__":
    pass

