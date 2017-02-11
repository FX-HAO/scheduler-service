# coding: utf-8
import random
import requests
from cookies import cookies
from user_agent import agents

class SinaSpider():
    def __int__(self):
        self.cookies = random.choice(cookies)
        self.headers = {'user-agent': random.choice(agents)}

    @classmethod
    def verify_sina_url(cls, url):
        with requests.session() as session:
            req = requests.Request('GET', url=url, cookies=cls.cookies, headers=cls.headers)
            prepped = req.prepare()
            resp = session.send(prepped, allow_redirects=False)
            return resp