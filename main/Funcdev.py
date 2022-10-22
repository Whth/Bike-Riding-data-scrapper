import base64
import copy
import datetime
import json
import os
import time

import matplotlib.image as mpimg  # mpimg 用于读取图片
import matplotlib.pyplot as plt  # plt 用于显示图片
import numpy as np
import requests
from fake_useragent import UserAgent
from wxpusher import WxPusher

import BadDataCleaner
import CoodiSys
from CoodiSys import BOUND_LOCATION
from folderHelper import cheek_local_phone_format, sync_phone_txt, normal_format_dict, normal_format_order, \
    open_CurTime_tree_folder
from net_control.push_helper import UIDS, TOPIC_IDS
from net_control.req_misc import input_with_timeout

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

# <editor-fold desc="Data Capture Section">


DEFAULT_COOLDOWN = 0.6

"""
available_code,phoneNumber,last_phone_used_time,expired_code,LoginToken,last_LoginToken_used_time,CoolDown_time
"""


# <editor-fold desc="HAL">


# <editor-fold desc="net_work_components">
def a_random_header():
    tempHeader = copy.deepcopy(headers_with_default_UA)
    tempHeader['User-Agent'] = UserAgent().random
    return tempHeader.copy()


def sendSMSCode_ttBike(phone):
    """
    功能：输入手机号，模拟完成获取哈喽单车短信验证码的操作。
    1.传入手机号phone
    2.如果顺利，请求响应会包含base64图片验证码，否则显示异常信息
    3.显示图片验证码，弹框要求输入。如果输入的验证码正确，服务器会返回发送短信成功地响应，否则显示异常信息
    """
    secs = requests.session()

    get_code_url = 'https://api.ttbike.com.cn/auth?user.account.sendCodeV2'
    get_code_data = {"version": "4.2.3", "from": "h5", "systemCode": 63, "platform": 6,
                     "action": "user.account.sendCodeV2", "mobile": phone, "capText": ""}
    r = secs.post(get_code_url, headers=a_random_header(), data=json.dumps(get_code_data), timeout=6)  # post手机号
    status = False
    if "imageCaptcha" in r.text:  # 获取短信验证码前需要验证图片验证码，如果response包含验证码字段，则正确，否则异常
        img = json.loads(r.text)["data"]["imageCaptcha"]
        with open("captcha.png", 'wb') as tempOut:
            tempOut.write(base64.decodebytes(bytes(img[22:], "utf-8")))  # 将base64图片验证码解码保存
        captcha = mpimg.imread('captcha.png')  # 使用mpimg读取验证码
        plt.imshow(captcha)  # 在Ipython或JupyterNoetebook显示图片，便于人工输入
        plt.axis('off')
        plt.show()
        code = input('请输入图片验证码:')
        get_code_data["capText"] = code
        r = secs.post(get_code_url, headers=a_random_header(), data=json.dumps(get_code_data), timeout=6)
        if 'true' in r.text:
            print(r.text)
            print('短信验证码发送成功！')
            status = True
        else:
            print('图片验证码错误！')
    else:
        print(r.text)
    return status


def getToken_ttBike(phone, code) -> str:
    """
    功能：输入手机号和短信验证码，模拟用户登陆，获取token
    1.传入手机号和对应的短信验证码
    2.如果登陆成功，返回token，否则显示异常信息
    """
    session = requests.session()

    login_url = 'https://api.ttbike.com.cn/auth?user.account.login'
    login_data = {"version": "4.2.3", "from": "h5", "systemCode": 63, "platform": 1, "action": "user.account.login",
                  "mobile": phone, "code": code, "picCode": {"cityCode": "0577", "city": "温州市", "adCode": "330304"}}

    r = session.post(login_url, headers=a_random_header(), data=json.dumps(login_data), timeout=6)
    print(r.text)
    token = json.loads(r.text)["data"]["token"]
    print(f'获取token成功,the token is: {token}')
    return token


def getBikes_improved(point_coordinates: list, token: str, USE_NEW_VERSION=False) -> list:
    """
    功能：获取某一经纬度周边500(?)米的所有单车信息
    1.传入经纬度和token值
    2.如果顺利，返回经纬度周围500米的所有单车信息，否则显示异常信息
    """

    get_bike_data = {"version": "4.2.3", "from": "h5", "systemCode": 63, "platform": 1,
                     "action": "user.ride.nearBikes",
                     "lng": point_coordinates[0], "lat": point_coordinates[1],
                     "currentLng": point_coordinates[0], "currentLat": point_coordinates[1],
                     "cityCode": "0577", "adCode": "330304", "token": token
                     }

    get_bike_data_new = {
        "version": "6.17.0", "from": "h5", "systemCode": 63, "platform": 1,
        "action": "user.ride.nearBikes",
        "lng": point_coordinates[0], "lat": point_coordinates[1],
        "currentLng": point_coordinates[0], "currentLat": point_coordinates[1],
        "adCode": "330304", "cityCode": "0577", "token": token,
        "ticket": "MTY3MjQxMjQ3Mg==.su9UiPSWh6VGUPHMqk8tpmD3wpgVr8eB464cPOT/J9o="
    }
    if USE_NEW_VERSION:
        get_bike_data = get_bike_data_new

    get_bike_url = 'https://api.ttbike.com.cn/api?user.ride.nearBikes'
    bikeData_return = requests.post(get_bike_url, headers=a_random_header(), data=json.dumps(get_bike_data), timeout=20)
    print(f'Server Echoing status:{bikeData_return}')
    Bike_raw_data_dict = json.loads(bikeData_return.text)  # return type is dict

    """

    passCode = 0
    expiredCode = 133
    """

    if Bike_raw_data_dict['data']:
        return Bike_raw_data_dict['data']  # a list

    else:
        # print(bikeData_return.text)
        print(f'## BAD TOKEN ## : {token}')
        return [token]


# </editor-fold>


def get_SMS_Code_Manually() -> int:
    """
    Get the SMS code
    """
    print('needing human configuration')
    SMScode = int(input_with_timeout('Please input the SMScode: '))
    if SMScode is None:
        print('no response,skip input')
        return 0000
    return SMScode


def load_local_phone_dict_list():
    """
    load local phone dict list
    :return:
    """
    local_phone_dict_list = []

    with open(f'{phoneNumber_file_name}', 'r') as f:

        for i in range(get_all_lines_count()):
            line = f.readline()

            if line == '\n' and line == '':
                print(f'skip blank lines')
                continue
            print(f'loading line :{line}')
            tempDict = copy.deepcopy(normal_format_dict)
            line_list = line.split()  # converting strings to list
            for order_place in range(len(normal_format_order)):  # converting list to dict
                order_place_type = type(tempDict[normal_format_order[order_place]])
                tempDict[normal_format_order[order_place]] = order_place_type(line_list[order_place])
            local_phone_dict_list.append(tempDict)
        print('All lines were converted successfully\n###################################\n\n\n')
    return local_phone_dict_list


def write_local_phone_dict_list_to_file(dict_list: list, address=f'{phoneNumber_file_name}'):
    """
    write local phone dict list to file
    :param dict_list:
    :param address:
    :return:
    """
    # print(f'writing {dict_list}\n to file {address}\n##############################')
    show_dict_list(dict_list)
    with open(address, 'w') as f:
        for phone_data_dict in dict_list:
            spaceC = ''
            for order_place in normal_format_order:
                f.write(spaceC + str(phone_data_dict[order_place]))
                if spaceC == '':
                    spaceC = ' '
            f.write('\n')
    print('All Written!')


# </editor-fold>


# <editor-fold desc="Function Updates">


def rectangle_slice(loc_list: list = BOUND_LOCATION, step=0.0009,
                    disPlayPic: bool = False) -> list:
    """
    attention: This function will not function properly when called with a line_liked tangle,demanding img improvements
    BOUND_LOCATION: defined in the other docs
    :param disPlayPic:
    :param step:
    :param loc_list: containing two conner coordinates
    :return: node_list containing point within the rectangle defined by two conner

    lat
    |
    |
    |_______lng
    """
    node_list = []
    Node = [0, 0]
    # print(f'{loc_list}')
    latRange = np.arange(loc_list[1], loc_list[3], step)
    lngRange = np.arange(loc_list[0], loc_list[2], step)

    total_nodes_counter = len(lngRange) * len(latRange)
    print(f'the monitoring area contains {total_nodes_counter}')
    for i in range(len(lngRange)):
        for j in range(len(latRange)):
            tempNode = copy.deepcopy(Node)
            tempNode[0] = lngRange[i]  # x
            tempNode[1] = latRange[j]  # y
            node_list.append(tempNode.copy())
    if disPlayPic:
        data_display_multiplier = 1

        plt.figure(figsize=(len(lngRange) / 1.2, len(latRange) / 1.2), dpi=130)

        plt.axis('equal')

        for node in node_list:
            plt.scatter(node[0], node[1], s=5)
            plt.scatter(node[0] * data_display_multiplier, node[1] * data_display_multiplier, alpha=0.5, s=2000)
        plt.grid()
        plt.suptitle(f"({len(lngRange)}X{len(latRange)}) {len(node_list)} Points", x=0.12, y=0.98, fontsize=16,
                     color='red')
        plt.title(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
        plt.xlabel(f'Longitude (deg*{data_display_multiplier})', loc='left')
        plt.ylabel(f'Latitude (deg*{data_display_multiplier})', loc='top')
        plt.show()
    return node_list


def multiTangle_slice(node_list: list, loc_list: list, disPlayPic: bool = False):
    """

    :param node_list:
    :param loc_list:
    :param disPlayPic:
    :return:
    """

    pass


def check_point_in_tangle(point: list, tangle: list) -> bool:
    """

    :param point:
    :param tangle:
    :return:
    """
    inRange = False
    if tangle[0] < point[0] < tangle[2]:  # x lock
        if tangle[1] < point[1] < tangle[3]:  # y lock
            inRange = True

    return inRange


def bikeDict_to_location(bikeDict: dict):
    return [float(bikeDict.get('lng')), float(bikeDict.get('lat'))]


def filter_point_in_tangle(bikeList: list, tangle: list) -> list:
    """
    lat
    |
    |
    |_______lng

    :param bikeList:
    :param tangle:
    :return:

    """
    inRangeBikeList = []

    for bikeDict in bikeList:
        bikeLocation = bikeDict_to_location(bikeDict)
        if check_point_in_tangle(bikeLocation, tangle=tangle):
            inRangeBikeList.append(bikeDict)
    return inRangeBikeList


def filter_rubbished_point(bikeList: list, USING_METHOD: int = 1) -> int:
    """
    remove rubbished_point
    :param USING_METHOD:
    :param bikeList:
    :return: Cleaned list Length
    """

    print(f'!!Cleaning bad data!!\n'
          f'list Length: {len(bikeList)}')
    if USING_METHOD == 1:
        removed_counter = 0
        for bikeDictSerial in range(len(bikeList)):  # creating serial number
            if bikeList[bikeDictSerial].get('bikeNo')[0] == '2':  # finding element using get method dont a[]==
                del bikeList[bikeDictSerial]
                removed_counter += 1
            else:
                continue
        print(f'!!Removed [{removed_counter}] bikes!!\n'
              f'Cleaned list Length: {len(bikeList)}\n'
              f'_______________________________')
        return len(bikeList)


# </editor-fold>


def get_all_bikes(dict_list: list, loc_list: list = BOUND_LOCATION,
                  stepLen: float = 0.0008, USE_NEW_VERSION: bool = False) -> list:
    """
    no judge if the data obtained is in range
    :param USE_NEW_VERSION:
    :param stepLen:
    :param dict_list:
    :param loc_list:
    :return:
    """
    allBikes = []  # store result

    points_list = rectangle_slice(loc_list=loc_list, step=stepLen)  # area slice

    token_s_dict = loop_find_available_token(dict_list)
    points_list_len = len(points_list)

    extractStartTime = datetime.datetime.now()  # time Consumptions calc

    point_serial = 0
    for point in points_list:
        startFrame = time.time()
        # print(f'Going with Point {point_serial}/{points_list_len}: {point}........')    #for debugging purposes

        bike_raw_list = getBikes_improved(point, token_s_dict[normal_format_order[3]],
                                          USE_NEW_VERSION=USE_NEW_VERSION)

        if bike_raw_list[0] == token_s_dict[normal_format_order[3]]:  # return equal token suggesting fail getBikes

            update_token_status(token_s_dict, expired_code=1)  # update bad token status

            updateResult = '## FAIL ##'

        else:
            allBikes.extend(bike_raw_list)
            update_token_status(token_s_dict, token=token_s_dict[normal_format_order[3]])
            updateResult = 'Success'

        print(
            f'point {point_serial}/{points_list_len}: {point} ,{updateResult},using {(time.time() - startFrame):.4f}s\r\n'
            f'--------------------------------')
        point_serial += 1
        token_s_dict = loop_find_available_token(dict_list)
    livingTIme = datetime.datetime.now() - extractStartTime
    print(f'#################################\n'
          f'Consumed time: {livingTIme.seconds}s\n'
          f'Average time per point : {(livingTIme.seconds / points_list_len):.3f}s'
          f'\n#################################\n')

    return allBikes


def writeRes(allBikes, timestamp, storage_dir=ROOT_FOLDER, return_details=False):
    """
    功能：将单车数据追加写入文本文件存储,自动去重
    :param return_details:
    :param storage_dir:
    :param allBikes:
    :param timestamp:
    :return:
    """
    dataFileName = 'allBikes.txt'

    fine_bike_dict_list = []
    duplicated_bike_dict_list = []
    for bike_data_dict_temp in allBikes:

        bike_data_dict = {'bikeNo': bike_data_dict_temp.get('bikeNo'),
                          'lat': bike_data_dict_temp.get('lat'),
                          'lng': bike_data_dict_temp.get('lng')}
        if bike_data_dict in fine_bike_dict_list:
            duplicated_bike_dict_list.append(bike_data_dict)

        else:
            fine_bike_dict_list.append(bike_data_dict)

    print(f'#############################\n'
          f'Duplicated and removed Bikes: {len(duplicated_bike_dict_list)}\n'
          f'#############################')
    # print(duplicated_bike_dict_list)
    print(f'#############################\n'
          f'Detected bikes: {len(fine_bike_dict_list)}\n'
          f'#############################')
    # print(fine_bike_dict_list)
    with open(open_CurTime_tree_folder(rootFolder=storage_dir) + dataFileName, 'a+') as f:
        for bike_data_dict in fine_bike_dict_list:
            f.write(str(timestamp) + '\t')
            f.write(('\t'.join([bike_data_dict['bikeNo'], bike_data_dict['lat'], bike_data_dict['lng']])))
            f.write('\n')
        print(timestamp + 'write done.')
    if return_details:
        return [len(fine_bike_dict_list), len(duplicated_bike_dict_list)]


# <editor-fold desc="MAIN method">
def run_every_other_interval(dict_list: list, scanStep: float = 0.0017, scanInterval: float = 180.,
                             lastingDays: float = 1.,
                             loc_list: list = BOUND_LOCATION, notifications: bool = False, filter_ON: bool = False,
                             USE_NEW_VERSION: bool = False, WriteDownLog: bool = False, dispPlayData: bool = False):
    if scanStep < 0.001:
        raise Exception
    """
    功能：每隔两分钟获取一次高教园的所有单车信息并保存。

    """
    log_file_name = 'bikes_variant.log'
    if scanInterval == 0:
        raise
    max_interval = 2 * scanInterval
    min_interval = scanInterval / 2

    endDay = datetime.datetime.now() + datetime.timedelta(days=lastingDays)
    while True:
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            print('########################################################\n'
                  '##########################START#########################\n'
                  '########################################################')
            nextTime = (datetime.datetime.now() + datetime.timedelta(minutes=3))
            print(timestamp)

            allBikes = get_all_bikes(dict_list, stepLen=scanStep,
                                     loc_list=loc_list,
                                     USE_NEW_VERSION=USE_NEW_VERSION)  # return list of all bikes with dict format

            # <editor-fold desc="Filter">

            filter_rubbished_point(allBikes)

            if filter_ON:

                filtered_bikes = filter_point_in_tangle(allBikes, tangle=loc_list)
            else:
                filtered_bikes = allBikes
            # </editor-fold>

            bike_count_detail = [0] * 2
            bike_count_detail = writeRes(filtered_bikes, timestamp, return_details=True)
            if dispPlayData:
                print(f'Proceeding with data on map')
                display_bikes_on_map(allBikes, area=loc_list, saveImage=True)

            # <editor-fold desc="BIKES counter log">
            if WriteDownLog:  # params to control the logging
                log_dir = open_CurTime_tree_folder(rootFolder=ROOT_FOLDER) + log_file_name
                log_content = {
                    'totalDetectedBikes_within': bike_count_detail[0],
                    'duplicatedBikes': bike_count_detail[1],
                    'totalDetectedBikes': bike_count_detail[0] + bike_count_detail[1],
                    'timestamp': timestamp
                }

                if not os.path.exists(log_dir):  # check if the log file exists
                    with open(log_dir, mode='w'):
                        pass
                with open(log_dir, mode='a') as log:
                    for content_ele in log_content.keys():
                        log.write(f'{log_content[content_ele]}\t')
                    log.write('\n')

            # </editor-fold>

            restTime = (nextTime - datetime.datetime.now()).seconds
            if min_interval < restTime < max_interval:  # sleep time is always smaller than 1800 seconds
                pass
            else:
                restTime = (min_interval + max_interval) / 2
            print(f'Next scanTime is: ' + nextTime.strftime("%Y-%m-%d %H:%M") + f'## Resting {restTime}s')
            time.sleep(restTime)
            # <editor-fold desc="Wx commit sec">
            if notifications:
                WxPusher.send_message(f'NormalFormatDBikes: {bike_count_detail[0]}\n'
                                      f'DuplicatedBikes: {bike_count_detail[1]}\n'
                                      f'ALL AREA TotalDetected: {bike_count_detail[0] + bike_count_detail[1]}\n'


                                      f'timestamp: {timestamp}\n'
                                      f'NextCheckTime: {nextTime.strftime("%Y-%m-%d %H:%M")}',
                                      uids=UIDS,
                                      topic_ids=TOPIC_IDS,
                                      token='AT_7gneRS02ois8YkgVWeCS0Q9iEV3Lq4Xl')
            # </editor-fold>

            if datetime.datetime.now() > endDay:
                print('time up')
                break
        except KeyboardInterrupt:
            # write_local_phone_dict_list_to_file(dict_list)
            print('Program EXITED')

            break




# </editor-fold>

# <editor-fold desc="TEST section">


def getTokenTest(test_times=1):
    for i in range(test_times):
        phone = input('请输入手机号：')
        sendSMSCode_ttBike(phone)
        code = input('请输入收到的验证码：')
        token = getToken_ttBike(phone, code)
        print(f'The token of [{phone}] is :  {token}\n############################')


def show_dict_list(dict_list: list) -> None:
    """
    display_bike list string
    :param dict_list:
    :return:
    """
    print('################################################################')
    for a_dict in dict_list:
        print(a_dict)
    print('################################################################\n')
    return


def display_bikes_on_map(bikes_list: list, area: list, mapTitle: str = None, saveImage: bool = False) -> None:
    """
    display_bikes_on_map
    :param mapTitle:
    :param area:
    :param bikes_list: dict*n

    :return:

        lat
    |
    |
    |_______lng
    """
    completeCount = 0
    bikes_list_len = len(bikes_list)
    data_display_multiplier = 1.0
    plt.figure(dpi=110)
    plt.grid(True)
    plt.axis('equal')

    timeStamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')

    # <editor-fold desc="labeling">
    if mapTitle:

        plt.title(mapTitle)
    else:
        plt.title(f'[{area[0]:.2f},{area[1]:.2f}] || [{area[2]:.2f},{area[3]:.2f}]')
    plt.xlabel(f'Longitude (deg*{data_display_multiplier})', loc='right')
    plt.ylabel(f'Latitude (deg*{data_display_multiplier})', loc='top')
    plt.suptitle(timeStamp + f'AllBikes: {bikes_list_len}')
    # </editor-fold>

    bike_lng = []  # bike_location_list
    bike_lat = []
    for bike in bikes_list:
        bike_lng.append(float(bike['lng']))
        bike_lat.append(float(bike['lat']))
        # print(f'putting bike on map\n'
        #       f'{bike}', end='\n')
        completeCount += 1
        print(f'data map processing {completeCount / bikes_list_len:.3f}%', end='\r')

    print(f'data map processing 100%')
    plt.scatter(bike_lng, bike_lat, alpha=0.8, s=8)

    if saveImage:
        figName = timeStamp + '.png'

        figFolderName = open_CurTime_tree_folder(ROOT_FOLDER) + 'images/'
        figAdd = figFolderName + figName
        if not os.path.exists(figFolderName):
            os.makedirs(figFolderName)  # create img folder if hadn't

        print(figAdd)
        plt.savefig(figAdd)

    plt.show()
    return


# </editor-fold>

def token_expired_check_timecheck(phone_data_dict: dict):
    """
    Check if phone data is expired
    """
    # 24 hr=86400 sed
    expire_time = 24 * 60 * 60

    if type(phone_data_dict[normal_format_order[3]]) != str:
        phone_data_dict[normal_format_order[4]] = 0  # no token, no expires
        return False
    elif time.time() - phone_data_dict[normal_format_order[2]] > expire_time:
        # token generated time should be the same as the last_phone_used_time
        print('a token has expired, please refresh')

        '''
        since dont know the exact expired_time so the line below is commented out
        '''
        # phone_data_dict[normal_format_order[4]]=1 #exceeds expired_time
        return True

    return False


def check_token_available(data_dict: dict):
    passedTime = time.time() - data_dict[normal_format_order[5]]

    # breakpoint()
    if passedTime > data_dict[normal_format_order[6]]:

        print(f'{data_dict[normal_format_order[0]]}: TOKEN available|| Passed time: {passedTime:.3f}s')
        return True
    else:
        # print(f'{data_dict[normal_format_order[0]]}: token not available')

        return False


def check_token_usable_with_net(token: str, test_point: list = (120.68976, 27.91788)) -> bool:
    """
    Check if the token is usable with the net
    :param token:
    :param test_point:
    :return:
    """
    if getBikes_improved(test_point, token=token)[0] == token:
        print(f'BAD TOKEN!!,the {token} is NOT usable')
        return False
    else:
        print(f'OK,the {token} is usable')

        return True


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

            if check_token_available(dict_list[dict_serial]):
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


def update_signal_data_dict(a_data_dict: dict, withTokenTest=True):
    phoneNumber = a_data_dict[normal_format_order[0]]
    print(f'\tUpdating phone {phoneNumber} data')
    sendSMSCode_ttBike(phoneNumber)  # matching SMScode with phoneNumber
    print('\tSending SMS Msg')
    update_phone_status(a_data_dict, available_code=0)
    print('\tUpdating phone status')
    SMScode_input = get_SMS_Code_Manually()
    print(f'the input code is {SMScode_input}\n'
          f'###################################')

    if SMScode_input != 0:
        print('\tGetting token form the server')
        token = getToken_ttBike(phoneNumber, SMScode_input)

        print('\tUpdating token status')
        update_token_status(a_data_dict, token)
        a_data_dict[normal_format_order[3]] = token
        return a_data_dict
    else:
        print(f'bad input code: {SMScode_input}')
        raise


def massive_Update_phone_data_dict_list(dict_list: list, safeUpdate=True) -> list:
    """Update phone data dict list"""
    if safeUpdate and cheek_local_phone_format() > 0:
        print('Sync local cache')
        sync_phone_txt()

    for a_data_dict in dict_list.copy():
        update_signal_data_dict(a_data_dict)

    print('###########\n'
          'ALL Updated\n'
          '###########')
    show_dict_list(dict_list)
    return dict_list


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


# </editor-fold>


if __name__ == "__main__":

    if cheek_local_phone_format() > 0:
        sync_phone_txt()
    a_origin_list = load_local_phone_dict_list()
    show_dict_list(a_origin_list)


    # <editor-fold desc="MAIN Section">

    step = 0.0017
    target_Zone = CoodiSys.BOUND_LOCATION

    rectangle_slice(target_Zone, step=step, disPlayPic=True)  # s

    run_every_other_interval(a_origin_list, loc_list=target_Zone, scanStep=step, notifications=True, filter_ON=True,
                             USE_NEW_VERSION=False, WriteDownLog=True, dispPlayData=True, scanInterval=30.)

    # </editor-fold>
    BadDataCleaner.normal_data_clean()  # bad data cleanup
