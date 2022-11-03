import datetime
import os
import warnings

import BadDataCleaner
import folderHelper
from CoodiSys import TangleScrapper, BOUND_LOCATION
from phoneBookManager import PhoneBook_Manager

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
    :param USE_TREE:will return count
    :param USE_NEW_VERSION:
    :param stepLen:
    :param loc_list:
    :return:
    """
    slicer = TangleScrapper(loc_list=loc_list, stepLen=stepLen)
    a_phoneBook = PhoneBook_Manager(phoneBook_path)

    if USE_TREE:
        result = slicer.tree_slice(a_phoneBook=a_phoneBook, return_bike_info=True)  # detail return
        return result

    raise Exception  # raise Exception if no match found


# <editor-fold desc="MAIN method">


def run_every_other_interval(dict_list: list, scanStep: float = 0.0017, scanInterval: float = 180.,
                             loc_list: list = BOUND_LOCATION, notifications: bool = False, filter_ON: bool = False,
                             USE_NEW_VERSION: bool = False, WriteDownLog: bool = False, dispPlayData: bool = False):
    if scanStep < 0.0011:
        raise Exception
    if scanInterval < 60:
        warnings.warn('frequency scan interval exceeded')
        scanInterval = 60
    """
    功能：每隔两分钟获取一次高教园的所有单车信息并保存。

    """
    MODE = 1
    while True:
        try:
            round_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")  # for each init time scan
            print(f'initialized {round_timestamp}')
            nextTime = (datetime.datetime.now() + datetime.timedelta(minutes=3))
            if MODE == 1:
                Points, bikes = getAllBike(dict_list, stepLen=scanStep,
                                           loc_list=loc_list,
                                           USE_NEW_VERSION=USE_NEW_VERSION
                                           , USE_TREE=True)  # return list of all bikes with dict format
                shader = BikeDataShaders(bike_list=bikes)
                shader.distributeHotMap()

        except KeyboardInterrupt:

            print('Program EXITED')

            break


# </editor-fold>

class BikeDataShaders:

    def __init__(self, bike_list):
        self.content: list = bike_list

        pass

    def distributeHotMap(self):
        """

        :return:
        """

        pass


"""
    def display_bikes_on_map(self, area: list, mapTitle: str = None, saveImage: bool = False) -> None:

        
        # display_bikes_on_map
        # :param saveImage:
        # :param mapTitle:
        # :param area:
        # :param self: dict*n
        # 
        # :return:
        # 
        #     lat
        # |
        # |
        # |_______lng
        
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

"""

# </editor-fold>


if __name__ == "__main__":
    a = os.path.abspath(folderHelper.phoneNumber_file_name)
    print(a)
    manager = PhoneBook_Manager(book_path=a)

    manager.content[0]: object
    manager.content[0].update_token_from_net(force_update=False)

    crapper = TangleScrapper(stepLen=0.0026)
    print(crapper.loc_list)
    res = crapper.tree_slice(phoneBook_path=a)
    print(res)

    BadDataCleaner.normal_data_clean()  # bad data cleanup
