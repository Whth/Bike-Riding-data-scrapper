import datetime
import os
import time

import matplotlib.pyplot as plt  # plt 用于显示图片

import BadDataCleaner
from CoodiSys import TangleScrapper, BOUND_LOCATION
from folderHelper import open_CurTime_folder
from phoneBook import PhoneBook

# <editor-fold desc="Data Capture Section">


"""
available_code,phoneNumber,last_phone_used_time,expired_code,LoginToken,last_LoginToken_used_time,CoolDown_time
"""


# <editor-fold desc="Function Updates">


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


def getAllBike(phoneBook_path, loc_list: list = BOUND_LOCATION,
               stepLen: float = 0.0011, USE_NEW_VERSION: bool = False, USE_TREE=False) -> dict:
    """
    no judge if the data obtained is in range
    :param phoneBook_path:
    :param USE_TREE:
    :param USE_NEW_VERSION:
    :param stepLen:
    :param loc_list:
    :return:
    """
    slicer = TangleScrapper(loc_list=loc_list, stepLen=stepLen)
    a_phoneBook = PhoneBook(phoneBook_path)

    if USE_TREE:
        result = slicer.tree_slice(a_phoneBook=a_phoneBook, return_bike_info=True)  # detail return
        return result

    raise Exception  # raise Exception if no match found


def log():
    log_dir = open_CurTime_folder(rootFolder=ROOT_FOLDER) + log_file_name
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

            allBikes = getAllBike(dict_list, stepLen=scanStep,
                                  loc_list=loc_list,
                                  USE_NEW_VERSION=USE_NEW_VERSION)  # return list of all bikes with dict format

            # <editor-fold desc="BIKES counter log">
            if WriteDownLog:  # params to control the logging


            # </editor-fold>

            restTime = (nextTime - datetime.datetime.now()).seconds
            if min_interval < restTime < max_interval:  # sleep time is always smaller than 1800 seconds
                pass
            else:
                restTime = (min_interval + max_interval) / 2
            print(f'Next scanTime is: ' + nextTime.strftime("%Y-%m-%d %H:%M") + f'## Resting {restTime}s')
            time.sleep(restTime)

            if datetime.datetime.now() > endDay:
                print('time up')
                break
        except KeyboardInterrupt:
            # write_local_phone_dict_list_to_file(dict_list)
            print('Program EXITED')

            break


# </editor-fold>

class Shaders:

    def __init__(self):
        pass

    def display_bikes_on_map(bikes_list: list, area: list, mapTitle: str = None, saveImage: bool = False) -> None:

        """
        display_bikes_on_map
        :param saveImage:
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

        figFolderName = open_CurTime_folder(ROOT_FOLDER) + 'images/'
        figAdd = figFolderName + figName
        if not os.path.exists(figFolderName):
            os.makedirs(figFolderName)  # create img folder if hadn't

        print(figAdd)
        plt.savefig(figAdd)

    plt.show()
    return


# </editor-fold>


if __name__ == "__main__":



    # </editor-fold>
    BadDataCleaner.normal_data_clean()  # bad data cleanup
