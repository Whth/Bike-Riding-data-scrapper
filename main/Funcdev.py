import datetime
import datetime
import os
import time

import matplotlib.pyplot as plt  # plt 用于显示图片

import BadDataCleaner
import CoodiSys
from CoodiSys import BOUND_LOCATION, rectangle_slice
from folderHelper import open_CurTime_tree_folder
from tokenManager import loop_find_available_token, update_token_status

# <editor-fold desc="Data Capture Section">


"""
available_code,phoneNumber,last_phone_used_time,expired_code,LoginToken,last_LoginToken_used_time,CoolDown_time
"""



# <editor-fold desc="Function Updates">






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

            # </editor-fold>

            if datetime.datetime.now() > endDay:
                print('time up')
                break
        except KeyboardInterrupt:
            # write_local_phone_dict_list_to_file(dict_list)
            print('Program EXITED')

            break


# </editor-fold>







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


if __name__ == "__main__":
    # <editor-fold desc="MAIN Section">

    step = 0.0017
    target_Zone = CoodiSys.BOUND_LOCATION

    rectangle_slice(target_Zone, step=step, disPlayPic=True)  # s

    run_every_other_interval(a_origin_list, loc_list=target_Zone, scanStep=step, notifications=True, filter_ON=True,
                             USE_NEW_VERSION=False, WriteDownLog=True, dispPlayData=True, scanInterval=30.)

    # </editor-fold>
    BadDataCleaner.normal_data_clean()  # bad data cleanup
