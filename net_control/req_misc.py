import copy
import time

import numpy as np
import requests
from fake_useragent import UserAgent
from func_timeout import func_set_timeout, exceptions

headers_with_default_UA = {"Accept": "application/json, text/plain, */*", "Accept-Encoding": "br, gzip, deflate",
                           "Accept-Language": "zh-cn",
                           "Connection": "close",
                           "Content-Length": "131",
                           "Content-Type": "text/plain;charset=UTF-8",
                           "Host": "api.ttbike.com.cn",
                           "Origin": "http://m.ttbike.com.cn",
                           "Referer": "http://m.ttbike.com.cn/ebike-h5/latest/index.html",
                           "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 "
                                         "(KHTML, "
                                         "like Gecko) Version/12.0 MQQBrowser/8.8.2 Mobile/16A5345f Safari/604.1 "
                                         "MttCustomUA/2 "
                                         "QBWebViewType/1 WKType/1"}
headers_with_default_UA_new = {
    'accept': 'application/json, text/plain, */*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'content-length': '325',
    'content-type': 'text/plain;charset=UTF-8',
    'origin': 'http://m.ttbike.com.cn',
    'referer': 'http://m.ttbike.com.cn/',
    'requestid': '3BFuzxLoDOwqO4D',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': ''
}


@func_set_timeout(300)
def input_with_timeout_work_sec(display_message):
    """
    Input function that waits for input to complete.
    """
    return input(display_message)


def input_with_timeout(display_message):
    try:
        return input_with_timeout_work_sec(display_message)
    except exceptions.FunctionTimedOut:
        print('\ninput timed out')
        return None


def normal_sleep(location=0.8):
    """
    Pause normal timeout.
    location:the approximate timeout
    """
    wait_time = np.random.normal(location, 0.7)
    while wait_time < 0.64:
        wait_time += 0.32
    while wait_time > 4.0:
        wait_time -= 0.32
    print(f'sleep pass {wait_time} sec')
    time.sleep(wait_time)
    return


def a_random_header():
    tempHeader = copy.deepcopy(headers_with_default_UA)
    tempHeader['User-Agent'] = UserAgent().random
    return tempHeader.copy()


class WeatherCop(object):
    """
    get you the current weather information

    中国气象局
    url=https://weather.cma.cn/
    """
    TARGET_URL = 'https://weather.cma.cn'

    def __init__(self):
        self.req()
        pass

    def req(self):
        print(requests.get(self.TARGET_URL).text)


if __name__ == '__main__':
    WeatherCop()
