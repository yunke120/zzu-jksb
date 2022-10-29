#! usr/bin/python

from bs4 import BeautifulSoup
import requests
import json
import os
import re
from notify import Notify

session = requests.session()

def read_json(json_file):
    obj = []
    try:
        obj = json.load(open(json_file, 'r', encoding='utf-8'))
    except FileNotFoundError:
        print(f'{json_file} not found')
    return obj

def get_user_info(json_file):
    users = []
    try:
        USERS = os.environ['UID']
        PWD = os.environ['UPW']
        SCKEY = os.environ['SCKEY']
        user_list = USERS.split('&')
        pwd_list = PWD.split('&')
        sckey_list = SCKEY.split('&')
        # assert len(user_list) == len(pwd_list)
        for u, p, k in zip(user_list,pwd_list,sckey_list):
            user = dict()
            user['uid'] = u
            user['upw'] = p
            user['sckey'] = k
            users.append(user)
    except KeyError:
        users = read_json(json_file)

    return users

def get_hh28():
    url = 'https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/first0?fun2=&door='
    header = {
        'Host': 'jksb.v.zzu.edu.cn',
        'Referer': 'https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/login',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
    }
    res = session.get(url=url, headers=header)
    html = res.text
    soup = BeautifulSoup(html, 'lxml')
    hh28 = soup.find('input',{'name':'hh28'}).get('value')
    return hh28

# 登录
def login(user_data, key):
    url = "https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/login"
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
        'Referer': 'https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/first0?fun2=&door=',
        'Origin': 'https://jksb.v.zzu.edu.cn',
        'Host': 'jksb.v.zzu.edu.cn'
    }
    data = {
        'uid':user_data['uid'],
        'upw':user_data['upw'],
        'smbtn':'进入健康状况上报平台',
        'hh28':key
    }
    msg = "login failed"
    res = session.post(url=url, data=data, headers=header)
    if res.status_code != 200:
        return msg
    res.encoding = 'utf-8'
    html = res.text
    soup = BeautifulSoup(html, 'lxml')
    content = soup.find('script').text
    url1 = re.search('"https.*?"', content)
    if url1 is None:
        return msg

    url1 = url1.group()[1:-1]
    header2 = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    'Referer': 'https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/login',
    'Host': 'jksb.v.zzu.edu.cn'
    }
    res = session.get(url=url1, headers=header2)
    res.encoding = 'utf-8'
    html = res.text
    soup = BeautifulSoup(html, 'lxml')
    url2 = soup.find('iframe', {'id':'zzj_top_6s'}).get('src')
    return url1, url2

# 获取通行证
def get_permit_data(refer, url):
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
        'Referer': refer,
        'Host': 'jksb.v.zzu.edu.cn'
    }
    res = session.get(url=url, headers=header)
    res.encoding = 'utf-8'
    html = res.text
    soup = BeautifulSoup(html, 'lxml')
    state = soup.select('#bak_0 > div:nth-child(5) > span')[0].get_text()
    data = dict()
    if state == "今日您已经填报过了":
        pass
    else:
        input_list = soup.find_all('input')
        
        for i in input_list:
            if (data.__contains__(i.attrs.get('name'))):
                l = list()
                l.append(data[i.attrs.get('name')])
                l.append(i.attrs.get('value'))
                data[i.attrs.get('name')] = l
            else:
                data[i.attrs.get('name')] = i.attrs.get('value')
    return data


# 开始填报
def ready_submit(data, refer):
    header = {
        'Host': 'jksb.v.zzu.edu.cn',
        'Origin': 'https://jksb.v.zzu.edu.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
        'Referer': refer
    }
    url = 'https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/jksb'
    res = session.post(url=url, data=data, headers=header)
    res.encoding = 'utf-8'
    html = res.text
    soup = BeautifulSoup(html, 'lxml')
    input_ = soup.find_all('input', {'type':'hidden'})
    submit_data = dict()
    for i in input_:
        submit_data[i.attrs.get('name')] = i.attrs.get('value')
    return submit_data


def parse_submit_data(data, json_file):
    submit_data = read_json(json_file)
    submit_data.update(data)
    return submit_data

# 提交
def submit(data):
    url = 'https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/jksb'
    header = {
        'Host': 'jksb.v.zzu.edu.cn',
        'Origin': 'https://jksb.v.zzu.edu.cn',
        'Referer': 'https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/jksb',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
    }
    res = session.post(url=url, data=data, headers=header)
    res.encoding = 'utf-8'
    html = res.text
    soup = BeautifulSoup(html, 'lxml')
    r = soup.select('#bak_0 > div:nth-child(2) > div:nth-child(2) > div:nth-child(2) > div:nth-child(2)')[0]
    result = r.get_text().replace(" ", "")
    return result

    # c = soup.select('#bak_0 > div:nth-child(2) > div:nth-child(2) > div:nth-child(4) > div:nth-child(2)')[0]
    # url1 = re.search('\'https.*?\'', str(c))
    # print(url1.group()[1:-1])


if __name__ == '__main__':
    server = Notify()
    users = get_user_info('user.json')
    for user in users:
        hh28 = get_hh28()
        refer, url = login(user, hh28)
        permit_data = get_permit_data(refer, url)
        if permit_data: # 如果未填报则开始填报
            submit_data = ready_submit(data=permit_data, refer=url)
            submit_data = parse_submit_data(submit_data, 'submit_data.json')
            result = submit(submit_data)
            server.server(user['sckey'], user['uid'], result)
        else:
            print("今日您已经填报过了")