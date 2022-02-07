from PIL import Image, ImageDraw, ImageFont
import os
import random
import time

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


if __name__ == "__main__":

    test_data = {
        "name": "Summerkirakira",
        "message": "群星虽然是很不错的科幻游戏，制度上仍存在着君主制、独裁制",
        "time": 1644165981880
    }
    test_list = []
    for i in range(10):
        test_list.append(test_data)
    make_chat_image(test_list)

