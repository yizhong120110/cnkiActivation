# -*- coding:utf8 -*-
"""
    调用可可科技的的短信验证码平台，获取手机号-截获发往该手机号的验证码短信
    该平台通过项目名称与短信模板的Title进行匹配，截获验证码短信
"""
import requests
from urllib import parse
#全局请求头

class CaptchaRequest:
    def __init__(self, url):
        self.files = {}
        self.headers = {}
        self.body = {}
        self.resHeader = {}
        self.timeouts = {}
        self.url = url
        self.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2427.7 Safari/537.36"

    def addFilePara(self, key, value_url):
        self.files[key] = open(r"%s" % (value_url), 'rb')
        return self

    def addHeadPara(self, key, value):
        self.headers[key] = value
        return self

    def addBodyPara(self, key, value):
        self.body[key] = value
        return self
    #设置连接时间和读取时间
    def setTimeout(self, connecttimout, readtimeout):
        self.timeouts["connecttimout"] = connecttimout
        self.timeouts["readtimeout"] = readtimeout
        return self


    def get(self):
        get_url = self.url + "?" + parse.urlencode(self.body)
        print(get_url)
        if not self.timeouts:
            res = requests.get(get_url, headers=self.headers)
        else:
            timeout = (self.timeouts["connecttimout"], self.timeouts["readtimeout"])
            res = requests.get(get_url, headers=self.headers, timeout=self.timeouts)
        return res

    def post(self):
        if not self.timeouts:
            res = requests.post(self.url, files=self.files, data=self.body, headers=self.headers)
        else:
            timeout = (self.timeouts["connecttimout"], self.timeouts["readtimeout"])
            res = requests.post(self.url, files=self.files, data=self.body, headers=self.headers, timeout=self.timeout)
        return res



