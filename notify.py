#coding=utf-8
import requests
import datetime


class Notify:
    def __init__(self) -> None:
        self.content = {}
        pass

    def diy_content(self, username, msg):
        current_time = datetime.datetime.now().strftime('%Y.%m.%d-%H:%M:%S')
        self.content = {
            "------\n"
            "### 打卡信息\n"
            "- 用户学号：" + str(username) + "\n"
            "- 打开状态：" + str(msg) + "\n"
            "- 打卡时间：" + current_time
        }

    def server(self, sckey, msg):
        self.url = 'https://sctapi.ftqq.com/' + sckey + '.send'
        data = {
            "text":"ZZU每日健康打卡",
            "desp":self.content
        }
        requests.post(self.url, data=data, headers={'Content-type': 'application/x-www-form-urlencoded'})