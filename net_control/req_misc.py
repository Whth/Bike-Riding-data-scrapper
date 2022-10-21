import time

import numpy as np
import requests
from func_timeout import func_set_timeout, exceptions


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
