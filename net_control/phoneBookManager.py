import copy
import json
import os
import random
import time
import warnings

import requests

import req_misc


class PhoneNumber(object):
    DEFAULT_COOLDOWN = 0.6  # to restrict to max requests per seconds
    HALL_LAST_SMS_TIME = None

    def __init__(self, phone_number: str = '', token: str = '', cooldown: float = DEFAULT_COOLDOWN,
                 tokenAutoUpdate: bool = False):
        """
        :param phone_number:
        :param token:phone_number:
        """

        self.phone_number = phone_number
        self.tokenCoolDown = cooldown
        self.token = token

        if tokenAutoUpdate:  # if token is None Autoupdate it
            self.token = self.request_newToken(self.send_SMS())
            self.get_token()
        self.token_last_time = time.time()
        self.HALL_LAST_SMS_TIME = time.time()  # for SMS blocking

        self.tokenUsable = bool(token == '')  # default input token is always usable

    def update_token(self, token):
        """

        :param token:
        :return:
        """
        self.token = token
        self.token_last_time = time.time()
        self.tokenUsable = True
        return

    def update(self, phone_number: str = '', token: str = '', cooldown: float = DEFAULT_COOLDOWN):
        """

        :param phone_number:
        :param token:
        :param cooldown:
        :return:
        """
        self.phone_number = phone_number
        self.update_token(token=token)
        self.tokenCoolDown = cooldown
        return

    def syc_token_last_time(self):
        self.token_last_time = time.time()
        pass

    def syc_HALL_LAST_SMS_TIME(self):
        self.HALL_LAST_SMS_TIME = time.time()

    def get_token(self, infoON=False):
        """
        withCoolDown
        update token and return token
        :return: token or ''
        """
        if time.time() - self.token_last_time > self.tokenCoolDown:
            if infoON:
                print(f'{self.phone_number}: TOKEN available|| Passed time  > [{self.tokenCoolDown}s]')
            self.syc_token_last_time()  # syc and return token
            self.tokenUsable = True
            return self.token
        else:
            if infoON:
                print(f'{self.phone_number}: token not available', end='\r')
            self.tokenUsable = False
            return ''

    def get_phone_number(self, syc_sms=False):
        if syc_sms:
            self.syc_HALL_LAST_SMS_TIME()
        return self.phone_number

    def send_SMS(self, FREQ_CHECK=True) -> bool:
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
        print(echo.text)
        if 'ok' in echo.text:
            print('Message Sent')
            return True
        else:
            print('Message fail to send')
            return True

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
            'phoneNumber': self.phone_number,
            'token': self.token,
            'tokenUSable': self.tokenUsable,
            'token_last_time': self.token_last_time,
            'tokenCooldown': self.tokenCoolDown
        }
        return data_dict

    def update_token_from_net(self, force_update=False):
        """

        :return:
        """
        if not force_update and self.token != '':  # open force_update
            warnings.warn(f'seems token:[{self.token}] is valid ,pass')
            return True

        if self.phone_number and self.send_SMS():
            # code = req_misc.input_with_timeout('please input SMScode: ')
            code = input('please input SMScode: ')
            if code == '':
                return False
            if self.request_newToken(code=code):
                return True

        else:
            raise Exception


class PhoneBook_Manager:
    """
    use a book file
    """

    def __init__(self, book_path):
        """
        initializing read phone file time content
        :param book_path:
        """

        self.content: list = []
        if os.path.exists(book_path):
            self.book_path = book_path
            self.loadBook()  # loadBook form database
        else:
            print(f'{book_path} not Found')
            print('create book file')
            with open(os.path.abspath(book_path), mode='w+') as book:

                template_line = json.dumps(PhoneNumber().create_phone_number_dict())
                book.write(template_line)
            print('created')
            raise Exception

        print(f'phoneBook Length {len(self.content)} ')
        for i, phone in enumerate(self.content):
            print(f'{i}. {phone}')

    def loop_token(self, randomize=True):
        """
        loop find usable token and sleep if not found
        :return:
        """

        while True:

            for phoneNum in self.content:
                token = phoneNum.get_token()
                if token:
                    if randomize:
                        time.sleep(random.random())  # 1 sec float
                    return token
            print('searching for token\r', end='')

            time.sleep(0.01)

    def loadBook(self):
        """
        self.content: list
        :return:

            'phoneNumber': self.phone_number,
            'token': self.token,
            'tokenUSable': self.tokenUsable,
            'token_last_time': self.token_last_time,
            'tokenCooldown': self.tokenCoolDown
        """
        if not os.path.exists(self.book_path):
            print(f'{self.book_path} not exists')
            raise Exception

        with open(self.book_path, mode='r') as book:
            for line in book.readlines():  # for each line create an empty obj

                tempObj = PhoneNumber()  # empty object
                phone_dict = json.loads(line)
                tempObj.update(phone_number=phone_dict['phoneNumber'],
                               token=phone_dict['token'],
                               cooldown=phone_dict['tokenCooldown'])

                self.content.append(copy.deepcopy(tempObj))
        return

    def dumpBook(self):
        """
        dump to file ,create in not found
        :return:
        """
        with open(self.book_path, mode='w') as book:
            for phone in self.content:
                line = json.dumps(phone.create_phone_number_dict()) + '\n'
            book.write(line)
        return

    def updatePhone(self):
        """
        doesn't do anything, just update
        :return:
        """
