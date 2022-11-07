#coding=utf-8
import requests
import datetime
import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

class Notify:
    def __init__(self) -> None:
        self.content = {}
        pass

    def diy_content(self, username, msg):
        current_time = datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S')
        self.content = {
            "------\n"
            "### 打卡信息\n"
            "- 用户学号：" + str(username) + "\n"
            "- 打开状态：" + str(msg) + "\n"
            "- 打卡时间：" + current_time
        }
# server酱
    def server(self, sckey, username, msg):
        self.url = 'https://sctapi.ftqq.com/' + sckey + '.send'
        self.diy_content(username, msg)
        data = {
            "text":"ZZU每日健康打卡",
            "desp":self.content
        }
        requests.post(self.url, data=data, headers={'Content-type': 'application/x-www-form-urlencoded'})

# 息知
    def xizhi(self, key, username, msg):
        self.url = f'https://xizhi.qqoq.net/{key}.send'
        self.diy_content(username, msg)
        data = {
            "title":"ZZU每日健康打卡",
            "content":self.content
        }
        requests.post(self.url, data=data, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'})

# 发送接口
    def send(self, key, username, msg):
        if key.startswith('SCT'):
            self.server(key, username, msg)
        elif key.startswith('XZ'):
            self.xizhi(key, username, msg)
        else:
            pass


if __name__ == '__main__':
    send = Notify()
    msg = "今日已打卡"
    send.send(os.environ['KEY'], os.environ['UID'], msg)