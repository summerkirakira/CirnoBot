from flask import Flask, request, Response
import os
import json
import requests


app = Flask(__name__)
current_folder = os.path.dirname(__file__)  # get current folder absolute path
MESSAGE_IMAGE = os.path.join(current_folder, 'image')

my_header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Host': 'gchat.qpic.cn'
    }


def return_img_stream(img_local_path):
    """
    工具函数:
    获取本地图片流
    :param img_local_path:文件单张图片的本地绝对路径
    :return: 图片流
    """
    with open(img_local_path, 'rb') as f:
        image = f.read()
    resp = Response(image, mimetype="image/jpeg")
    return resp


@app.route('/', methods=["GET", "POST"])
def send_image():
    if '.' in request.args.get("id"):
        image_id = request.args.get("id").replace('{', '').replace('}', '').split('.')[0]
    else:
        image_id = request.args.get("id").replace('{', '').replace('}', '')
    image_list = os.listdir(MESSAGE_IMAGE)
    for file in image_list:
        if file.replace('{', '').replace('}', '').startswith(image_id):
            return return_img_stream(os.path.join(MESSAGE_IMAGE, file))
    return None


@app.route('/upload', methods=['POST'])
def download_image():
    a = request.get_data()
    image_lib = json.loads(a)
    image_url = image_lib['url']
    r = requests.get(image_url, headers=my_header)
    with open(os.path.join(current_folder, 'image', image_url.split('/')[-2]), 'wb') as f:
        f.write(r.content)
    return 'OK'


def create_app():
   return app


# if __name__ == "__main__":
#     from waitress import serve
#     serve(app, host="0.0.0.0", port=4500)
