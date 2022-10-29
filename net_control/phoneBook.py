import json
import os
import time
import warnings

import requests

import req_misc


class PhoneNumber(object):
    DEFAULT_COOLDOWN = 0.6  # to restrict to max requests per seconds
    HALL_LAST_SMS_TIME = None
    phoneBooks = []

    def __init__(self, phone_number, token='_', cooldown=DEFAULT_COOLDOWN, tokenAutoUpdate: bool = True):
        """
        :param phone_number:
        :param token:phone_number:
        """

        self.phone_number = phone_number  #

        self.tokenCoolDown = cooldown

        if token:

            self.token = token
        elif tokenAutoUpdate:
            self.token = self.request_newToken(self.send_SMS())
            self.get_token()
        self.token_last_time = time.time()
        self.HALL_LAST_SMS_TIME = time.time()  # for SMS blocking

        self.tokenUsable = bool(token == '_')  # default input token is always usable

        self.phoneBooks.append(self.create_phone_number_dict())  # add to new phone_number to the book

    def update_token(self, token):
        """

        :param token:
        :return:
        """
        self.token = token
        self.token_last_time = time.time()
        return

    def syc_token_last_time(self):
        self.token_last_time = time.time()

    def syc_HALL_LAST_SMS_TIME(self):
        self.HALL_LAST_SMS_TIME = time.time()

    def get_token(self):
        """
        withCoolDown
        update token and return token
        :return: token or ''
        """
        passedTime = time.time() - self.token_last_time

        if passedTime > self.tokenCoolDown:

            print(f'{self.phone_number}: TOKEN available|| Passed time: {passedTime:.3f}s > {self.tokenCoolDown}')
            self.syc_token_last_time()  # syc and return token
            return self.token
        else:
            print(f'{self.phone_number}: token not available')

            return ''

    def get_phone_number(self, syc_sms=False):
        if syc_sms:
            self.syc_HALL_LAST_SMS_TIME()
        return self.phone_number

    def send_SMS(self, FREQ_CHECK=False) -> bool:
        print(f'FREQ_CHECK:{FREQ_CHECK}')
        """

        :return: success code 10
        """
        apiAdd = 'https://api.ttbike.com.cn/auth?user.account.sendCodeV2'
        req_load = {"version": "4.2.3", "from": "h5", "systemCode": 63, "platform": 6,
                    "action": "user.account.sendCodeV2", "mobile": self.phone_number, "capText": ""}
        head = req_misc.a_random_header()
        echo = requests.post(apiAdd, headers=head, data=json.dumps(req_load), timeout=6)

        if FREQ_CHECK:
            SMS_CD = 65
            while time.time() - self.HALL_LAST_SMS_TIME < SMS_CD:
                time.sleep(1)
                print(f'Waiting HALL_LAST_SMS_TIME remaining {SMS_CD - time.time() + self.HALL_LAST_SMS_TIME:%.f}',
                      end='\r')

        if 'ok' in echo:
            print('Message Sent')
            return True
        else:
            print('Message fail to send')
            return False

    def request_newToken(self, code) -> bool:
        """
        功能：输入手机号和短信验证码，模拟用户登陆，获取token
        1.传入手机号和对应的短信验证码
        update token
        """

        login_url = 'https://api.ttbike.com.cn/auth?user.account.login'
        login_data = {"version": "4.2.3", "from": "h5", "systemCode": 63, "platform": 1, "action": "user.account.login",
                      "mobile": self.phone_number, "code": code,
                      "picCode": {"cityCode": "0577", "city": "温州市", "adCode": "330304"}}

        r = requests.post(login_url, headers=req_misc.a_random_header(), data=json.dumps(login_data), timeout=6)

        # print(r.text)
        try:
            self.token = json.loads(r.text)["data"]["token"]
        except:
            warnings.warn('bad SMScode')
            return False
        print(f'获取token成功,the token is: {self.token}')
        return True

    def create_phone_number_dict(self):
        data_dict = {
            'phoneNumber': self.phone_number.copy(),
            'token': self.token,
            'token_last_time': self.token_last_time,
            'tokenCooldown': self.tokenCoolDown
        }
        return data_dict


class PhoneBook(object):
    """
    use a book file
    """

    def __init__(self, book_text_path):
        if os.path.exists(book_text_path):
            self.phoneBook: list = json.loads(book_text_path)
        self.phoneBook.length = len(self.phoneBook)  # store length
        print(f'phoneBook Length{self.phoneBook.length} ')

    def loop_token(self):
        """
        loop find usable token and sleep if not found
        :return:
        """

        while True:
            for phone_dict in enumerate(self.phoneBook):
                phone_dict.
            pass


