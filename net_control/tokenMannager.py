import time
import warnings

from CoodiSys import BOUND_LOCATION
from Funcdev import getBikes_improved, massive_Update_phone_data_dict_list
from folderHelper import normal_format_order, get_lines_with_content_Count


def token_echo_test(test_token, test_point=(BOUND_LOCATION[0], BOUND_LOCATION[1])):
    if test_token is None:
        test_token = input(f'input token')
    print(f'token is {test_token}')
    if test_point is None:
        point_str = input('input point:')
        test_point = point_str.split(',')
        print(f'{test_point}')
    Bikes = list(getBikes_improved(test_point, test_token))
    print(f'###################################\n{Bikes[0]}\n###########################################\n')
    print(f'the total count of detect {len(Bikes)}')
    return Bikes


def check_token_usable_with_net(token: str, test_point: list = (120.68976, 27.91788)) -> bool:
    """
    Check if the token is usable with the net
    :param token:
    :param test_point:
    :return:
    """
    if getBikes_improved(test_point, token=token)[0] == token:
        warnings.warn(f'BAD TOKEN!!,the {token} is NOT usable')
        return False
    else:
        print(f'OK,the {token} is usable')

        return True


def check_token_coolDown(data_dict: dict):
    passedTime = time.time() - data_dict[normal_format_order[5]]

    # breakpoint()
    if passedTime > data_dict[normal_format_order[6]]:

        print(f'{data_dict[normal_format_order[0]]}: TOKEN available|| Passed time: {passedTime:.3f}s')
        return True
    else:
        # print(f'{data_dict[normal_format_order[0]]}: token not available')

        return False


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
