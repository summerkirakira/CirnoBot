import httpx
from .config import get_config
import json


my_headers = {
        'referer': 'https://robertsspaceindustries.com/orgs',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36'
    }


async def get_kaiheila_info(url):
    async with httpx.AsyncClient() as client:
        html = await client.get(url, headers=my_headers, follow_redirects=True)
    kaihei_server_info = json.loads(html.text)
    return kaihei_server_info


async def kaihei_message_process(group_id):
    server_config = get_config()['kai_hei_api_url']
    if group_id in server_config:
        server_info = await get_kaiheila_info(server_config[group_id]['api_key'])
        message = '服务器名称：{}\n在线人数：{}人\n'.format(server_info['name'], server_info['online_count'])
        for channel in server_info['channels']:
            if 'users' in channel:
                message += '活跃频道: {}({}人)\n成员:'.format(channel['name'], len(channel['users']))
                if len(channel['users']) > 10:
                    channel['users'] = channel['users'][:9]
                for user in channel['users']:
                    message += user['nickname'] + ', '
                message = message[:-2]
                message += '\n'
        if message[-1] == '\n':
            message = message[:-1]
        if 'invitation_link' in server_config[group_id] and server_config[group_id]['invitation_link']:
            message += f"\n加入链接: {server_config[group_id]['invitation_link']}"
        return message
    else:
        return '当前本群未绑定开黑啦服务器~'
