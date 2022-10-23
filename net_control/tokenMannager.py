import time

from Funcdev import massive_Update_phone_data_dict_list
from folderHelper import get_lines_with_content_Count


class PhoneNumber(object):
    DEFAULT_COOLDOWN = 0.6  # to restrict to max requests per seconds
    HALL_LAST_SMS_TIME = None

    def __init__(self, phone_number, token='', cooldown=DEFAULT_COOLDOWN):
        """
        :param phone_number:
        :param token:phone_number:
        """
        self.HALL_LAST_SMS_TIME = time.time()  # for SMS blocking

        self.phone_number = phone_number  #

        self.token = token
        self.token_last_time = time.time()

        self.tokenCoolDown = cooldown
        self.tokenUsable = bool(token)  # default input token is always usable

    def update_token(self, token):
        """

        :param token:
        :return:
        """
        self.token = token
        self.token_last_time = time.time()
        return

    def syc_last_time(self):
        self.token_last_time = time.time()

    def get_token(self):
        """
        withCoolDown
        update token and return token
        :return: token or ''
        """
        passedTime = time.time() - self.token_last_time

        if passedTime > self.tokenCoolDown:

            print(f'{self.phone_number}: TOKEN available|| Passed time: {passedTime:.3f}s > {self.tokenCoolDown}')
            self.syc_last_time()  # syc and return token
            return self.token
        else:
            print(f'{self.phone_number}: token not available')

            return ''


class Manager(object, PhoneNumber):
    def __init__(self, file):





def loop_find_available_token(dict_list: list, failCounterON=False) -> dict:
    """
    operate on original data and return the token s dict
    :param dict_list:
    :param failCounterON:
    :return: token s dict with origin data use info
    """
    fail_count = 0
    while True:
        for dict_serial in range(len(dict_list)):

            if check_token_coolDown(dict_list[dict_serial]):
                token = dict_list[dict_serial][normal_format_order[3]]
                print(f'Found an available token : {token}')
                update_token_status(dict_list[dict_serial], token, expired_code=0)
                # write_local_phone_dict_list_to_file(dict_list)
                return dict_list[dict_serial]
            else:
                fail_count += 1
                print(f'##fail to find a token for {fail_count} times##', end='\r')
                time.sleep(0.01)

        if failCounterON and fail_count >= 5 * get_lines_with_content_Count():
            print(f'fail_count exceeds limitation'
                  f'\n############################'
                  f'\n############################')
            massive_Update_phone_data_dict_list(dict_list)
            break

        # normal_sleep(DEFAULT_COOLDOWN / 3)


def update_token_status(phone_data_dict: dict, token: str = '', expired_code=0):
    phone_data_dict[normal_format_order[3]] = token
    phone_data_dict[normal_format_order[4]] = expired_code
    phone_data_dict[normal_format_order[5]] = time.time()
    return phone_data_dict


def update_phone_status(phone_data_dict: dict, available_code):
    phone_data_dict[normal_format_order[1]] = available_code
    phone_data_dict[normal_format_order[2]] = time.time()
    return phone_data_dict
