from PIL import Image, ImageFont, ImageDraw
import io
import os
import logging


current_folder = os.path.dirname(__file__)  # get current folder absolute path
FONT_PATH = os.path.join(current_folder, 'font')


class Box:
    def __init__(self, width, height, background=None):
        """
        初始化基本单位ImageBox
        :param width: Box的宽度
        :param height: Box的长度
        背景颜色默认为黑色
        """
        self.width = width
        self.height = height
        if background:
            self.background_color = background
        else:
            self.background_color = (255, 255, 255)
        self.im = Image.new(mode='RGB', size=(width, height), color=self.background_color)

    def show(self):
        self.im.show()

    def set_background_image(self, image):
        """
        使用图片作为背景，此图片的size需与box的size吻合
        :param image:PIL.Image.Image图像
        :return:无
        """
        if not isinstance(image, Image.Image):
            raise ValueError("Background image must be PIL.Image.Image")
        if not (image.height == self.height and image.width == self.width):
            raise ValueError("The size of background image must be the same as box's")
        self.im = image

    def set_image(self, image, margin_left=0, margin_top=0, mode=None):
        """
        将外部Image放入Box指定位置
        :param mode: 排版样式
        :param image: PIL.Image.Image图像
        :param margin_left: 左边距
        :param margin_top: 上边距
        :return:
        """
        if not isinstance(image, Image.Image):
            raise ValueError("Inserted image must be PIL.Image.Image")
        if image.width > self.width or image.height > self.height:
            raise ValueError("Inserted image is too large")
        if mode:
            if mode == 'Center':
                margin_left = int((self.width - image.width) / 2)
                margin_top = int((self.height - image.height) / 2)
        self.im.paste(image, (margin_left, margin_top, margin_left + image.width, margin_top + image.height))

    def get_image(self):
        """
        返回Image图像
        :return: PIL.Image.Image
        """
        return self.im

    def set_alpha(self, alpha):
        self.im.putalpha(alpha)
        return self

    def get_background_fit_size(self, file_path):
        img = Image.open(file_path)
        return img.crop((0, 0, self.width, self.height))

    def get_height(self):
        return int(self.height)

    def get_width(self):
        return int(self.width)
class TextBox(Box):
    def __init__(self, width, height, background=None):
        super().__init__(width, height, background=background)
        self.text = ''

    def set_text(self, text, fill='black', font='圆简体.TTF', font_size=None, margin_left=0, margin_top=0, mode=None):
        """
        设定单元格中的字符串
        :param text: 文本
        :param fill: 填充
        :param font: 字体
        :param font_size: 字体大小
        :param margin_left: 左边距
        :param margin_top: 上边距
        :param mode: 模式
        :return:
        """
        self.text = text
        my_font = font
        if not font_size:
            font_size = int(self.height * 0.75)
        font = ImageFont.truetype(os.path.join(FONT_PATH, my_font), font_size)
        (length, height) = font.getsize(text)
        if length > self.width:
            # raise ValueError("Text is too long")
            logging.warning("Text is too long: {}".format(text))
            while True:
                font_size = int(0.9 * font_size)
                font = ImageFont.truetype(os.path.join(FONT_PATH, my_font), font_size)
                (length, height) = font.getsize(text)
                if length < self.width:
                    break
        if mode == 'Center':
            margin_top = int((self.height - height) / 2)
            margin_left = int((self.width - length) / 2)
        elif mode == 'Center Aligned':
            margin_top = int((self.height - height) / 2)
        draw = ImageDraw.Draw(self.im)
        draw.text(xy=(margin_left, margin_top), text=text, font=font, fill=fill)

    def get_text(self):
        return self.text

class CellBox(TextBox):
    def __init__(self, width, height, background=None, row=0, column=0):
        super().__init__(width, height, background=background)
        self.row = row
        self.column = column

class Sheet:
    class Row:
        """
        数据表中的一行
        """

        def __init__(self, width: int, height_per_row: int):
            self.size_data = []  # 列的宽度比列表
            self.content = []
            self.im = None
            self.width = width  # 行宽
            self.height_per_row = height_per_row  # 每行高度

        def set_content(self, column_data):
            if not self.size_data:
                for i in range(len(column_data)):
                    self.size_data.append(1 / len(column_data))
            for i in range(len(column_data)):
                self.content.append(CellBox(width=int(self.width * self.size_data[i]), height=self.height_per_row))
                # print(self.width * self.size_data[i])
                self.content[i].set_text(column_data[i])
            return self

        def set_size(self, size_data):
            """
            列表每行占比
            :param size_data: 列的宽度比列表
            :return:
            """
            # if len(size_data) != len(self.content):
            #     raise ValueError('Size data does not match')
            self.size_data = size_data

        def get(self, position):
            if position > len(self.content):
                raise ValueError('Required column is not legal')
            return self.content[position]

        def get_size(self):
            return len(self.content)

        def set_height_per_row(self, height):
            self.height_per_row = height

    def __init__(self, column_size, height_per_cell=0):
        self.column_size = column_size
        self.title = '@Sheet_Title'
        self.length = 0
        self.column_size_list = []
        self.im = None
        self.title_cell = None
        self.height_per_cell = height_per_cell
        self.width = 0
        self.content = []
        self.information = {
            'author': 'SummerKirakira'
        }
        self.options = {
            'watermark': False
        }

    def set_title(self, title):
        self.title = title
        return self

    def set_width(self, width):
        self.width = width
        return self

    def set_column_size(self, size_list):
        """
        设置行的宽度（比例）
        :param size_list:
        :return:
        """
        if isinstance(size_list, list):
            self.column_size_list = size_list
        else:
            raise ValueError('Column size list must be list')
        return self

    def add_row(self, column_data: list):
        """
        增加一行数据
        :param column_data: List形式的data
        :return:
        """
        new_row = self.Row(self.column_size, height_per_row=self.height_per_cell)
        new_row.set_size(self.column_size_list)
        new_row.set_content(column_data)
        self.length += 1
        self.content.append(new_row)

    def get_row(self, position: int):
        """
        获得第position行的数据
        :param position:
        :return:
        """
        if position < self.length:
            raise ValueError('Required row is not legal')
        return self.content[position]

    def get_cell(self, row_position, column_position):
        return self.get_row(row_position).get(column_position)

    def save_as_image(self):
        """
        生成Image.Image格式的图片
        :return: im
        """
        if not self.content:
            raise ValueError('The Sheet is empty')
        if self.title_cell:
            sheet_height = self.title_cell.get_height()
        else:
            raise ValueError('Title is not initialized')
        for i in range(len(self.content)):
            self.content[i].set_height_per_row(self.height_per_cell)
            sheet_height += self.height_per_cell
        self.im = Image.new(size=(self.column_size, sheet_height), mode='RGB', color=(255, 255, 255))
        self.title_modify()
        self.im.paste(self.title_cell.get_image(), (0, 0, self.title_cell.get_width(), self.title_cell.get_height()))
        current_position = [0, self.title_cell.get_height()]
        for i in range(len(self.content)):
            for j in range(self.content[i].get_size()):
                current_position = self.cell_modify(row=i, column=j, position=current_position)
        return self.im

    def cell_modify(self, row: int, column: int, position: list):
        """
        自定义单元格格式，需要overwrite
        :param row: 行号
        :param column: 列号
        :param position: 当前位置，[宽度， 高度], 上一单元格右上角位置
        :return: 下一位置
        """
        cell = self.content[row].get(column)
        self.im.paste(cell.get_image(), (position[0], position[1], position[0]+cell.get_width(), position[1]+cell.get_height()))
        if len(self.column_size_list) == column + 1:  # 若为行尾则换行
            return [0, position[1] + cell.get_height()]
        else:
            return [position[0] + cell.get_width(), position[1]]

    def title_modify(self):
        """
        自定义标题格式，需要overwrite
        :return:
        """
        pass
        return self

    def show(self):
        """
        显示图像
        :return:
        """
        if isinstance(self.im, Image.Image):
            self.im.show()
        else:
            self.save_as_image()
            self.im.show()

    def get_width(self):
        return self.width

    def set_height_per_cell(self, height):
        """
        设定每个单元格的高度
        :param height: 高度
        :return:
        """
        self.height_per_cell = height
        return self

    def set_title_params(self, width, height, text):
        self.title_cell = CellBox(width=width, height=height)
        self.title_cell.set_text(text=text)
        return self

    def save(self, path):
        if not self.im:
            self.save_as_image()
        self.im.save(path)

    class RowAdder:
        def __init__(self, row_size: int):
            self.row_size = row_size
            self.column_list = []

        def send_column(self, target, data='', force_send=False):
            self.column_list.append(data)
            if force_send:
                while True:
                    if len(self.column_list) == self.row_size:
                        target.add_row(self.column_list)
                        self.column_list = []
                        return self
                    self.column_list.append('')
            if len(self.column_list) == self.row_size:
                target.add_row(self.column_list)
                self.column_list = []
            return self


class KeywordsSheet(Sheet):
    def set_title_params(self, width, height, text):
        self.title_cell = CellBox(width=width, height=height)
        self.title_cell.set_text(text=text, mode='Center', fill=(51, 204, 255), font='卡牌少女拼音体.TTF', font_size=100)
        return self

    def cell_modify(self, row: int, column: int, position: list):
        """
        自定义单元格格式，需要overwrite
        :param row: 行号
        :param column: 列号
        :param position: 当前位置，[宽度， 高度], 上一单元格右上角位置
        :return: 下一位置
        """
        cell = self.content[row].get(column)
        if column % 2 == 0:
            if row % 2 == 0:
                new_cell = TextBox(width=cell.get_width(), height=cell.get_height(), background=(221, 255, 255))
            else:
                new_cell = TextBox(width=cell.get_width(), height=cell.get_height(), background=(238, 255, 255))
        else:
            if row % 2 == 0:
                new_cell = TextBox(width=cell.get_width(), height=cell.get_height(), background='#EFFBFB')
            else:
                new_cell = TextBox(width=cell.get_width(), height=cell.get_height())
        new_cell.set_text(mode='Center', text=cell.get_text(), font='圆简体.TTF')
        self.im.paste(new_cell.get_image(),
                      (position[0], position[1], position[0] + cell.get_width(), position[1] + cell.get_height()))
        if len(self.column_size_list) == column + 1:  # 若为行尾则换行
            return [0, position[1] + cell.get_height()]
        else:
            return [position[0] + cell.get_width(), position[1]]


def entries_list_photo(group_id: int, entries: list):
    my_sheet = KeywordsSheet(column_size=1600, height_per_cell=50)
    my_sheet.set_title_params(width=1600, height=150, text='词条一览')
    my_sheet.set_column_size([0.25, 0.25, 0.25, 0.25])
    key_dict = []
    for entry in entries:
        if entry['enabled_groups'] == 'all_groups' or str(group_id) in entry['enabled_groups'].split('#'):
            key_dict.append(entry['keywords'])
    row_add = Sheet.RowAdder(4)
    for keyword in key_dict:
        if '#' not in keyword and '涅' not in keyword and keyword:
            row_add.send_column(my_sheet, keyword)
    row_add.send_column(my_sheet, force_send=True)
    imgByteArr = io.BytesIO()
    my_sheet.save(os.path.join(current_folder, 'show_entries.jpg'))
    # my_sheet.save('Resources/Images/EntriesPhoto/output.jpg')
    with open(os.path.join(current_folder, 'show_entries.jpg'), 'rb') as f:
        img = f.read()
    return img
