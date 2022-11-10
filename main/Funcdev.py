import copy
import datetime
import os
import warnings

import matplotlib.pyplot as plt

import BadDataCleaner
import folderHelper
from CoodiSys import TangleScrapper, BOUND_LOCATION
from folderHelper import phoneNumber_file_path as book_Path
from phoneBookManager import PhoneBook_Manager

# <editor-fold desc="Data Capture Section">


"""
available_code,phoneNumber,last_phone_used_time,expired_code,LoginToken,last_LoginToken_used_time,CoolDown_time
"""


def getAllBike(phoneBook_path, loc_list: list = BOUND_LOCATION,
               stepLen: float = 0.0011, USE_NEW_VERSION: bool = False, USE_TREE=False):
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
        scannedPoint, bikes_dict = slicer.tree_slice(a_phoneBook=a_phoneBook, return_bike_info=True)  # detail return
        bikes_list = []
        new_bike_dict = {}
        for bikeNo in bikes_dict.keys():
            new_bike_dict['bikeNo'] = bikeNo
            new_bike_dict['lng'], new_bike_dict['lat'] = bikes_dict.get(bikeNo)[0], bikes_dict.get(bikeNo)[0]
            new_bike_dict['timeStamp'] = bikes_dict.get(bikeNo)[-1]

            bikes_list.append(copy.deepcopy(new_bike_dict))
        return scannedPoint, bikes_dict

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
                shaders = BikeDataShaders(bike_list=bikes)
                shaders.scanned_points(Points, 'L:\pycharm projects\Bike_Scrapper\RecoveredBikeData\img\s.jpg')

        except KeyboardInterrupt:

            print('Program EXITED')

            break


# </editor-fold>

class BikeDataShaders:

    def __init__(self, bike_list):
        self.bike_list: list = bike_list

        pass

    def distributeHotMap(self, points: dict):
        """
        bike distributeHotMap
        :return:
        """
        bgImg = plt.imread(folderHelper.background_img_folder + 'Fix.jpg')

        def points_to_xyList(points_list) -> tuple:
            """
            x :lng ,y :lat
            :param points_list:
            :return:
            """
            xList, yList = [], []
            for point in points_list:
                xList.append(point[0])
                yList.append(point[1])
            return xList, yList

        lng_list, lat_list = points_to_xyList(points_list=points)

        plt.imshow(bgImg)

        plt.title('SCANNED POINTS', fontweight="bold")

        plt.scatter(lng_list, lat_list, s=13, alpha=0.2)
        plt.xlabel('lng'), plt.ylabel('lat')

        plt.show()
        pass

    def bikeUsageLineMap(self, location, bikeUsage):
        pass

    @staticmethod
    def scanned_points(points, SAVE_IMG_PATH):
        """

        :param SAVE_IMG_PATH:
        :param points:
        :return:
        """
        try:
            bgImg = plt.imread(os.path.pardir + folderHelper.background_img_folder + 'Fix.jpg')
        except:
            bgImg = plt.imread('L:\pycharm projects\Bike_Scrapper\RecoveredBikeData\img\Fix.jpg')

        def points_to_xyList(points_list) -> tuple:
            """
            x :lng ,y :lat
            :param points_list:
            :return:
            """
            xList, yList = [], []
            for point in points_list:
                xList.append(point[0])
                yList.append(point[1])
            return xList, yList

        lng_list, lat_list = points_to_xyList(points_list=points)

        plt.figure(dpi=200)
        plt.title('SCANNED POINTS', fontweight="bold")

        plt.scatter(lng_list, lat_list, s=20, alpha=0.3)
        plt.xlabel('lng'), plt.ylabel('lat')
        # plt.imshow(bgImg, extent=[CoodiSys.BOUND_LOCATION[1], CoodiSys.BOUND_LOCATION[3], CoodiSys.BOUND_LOCATION[0],
        #                           CoodiSys.BOUND_LOCATION[2]])
        # plt.scatter(lng_list, lat_list, s=2000, alpha=0.6)
        plt.show()

        try:
            plt.savefig(SAVE_IMG_PATH)
        except:
            pass
        return


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
def dumpBike_data(bike_data: dict, file_dir: str) -> bool:
    """


    :param file_dir:
    :param bike_data:
    :return: True if success
    """
    path = file_dir + folderHelper.bikeData_file_name
    if not os.path.exists(file_dir):
        warnings.warn('no such file or directory')
        return False
    head = ''
    with open(path, mode='a+') as f:
        for bike in bike_data.keys():
            dataBody: list = bikes_dict.get(bike)
            line = f'{head}{dataBody[2]}\t{bike}\t{dataBody[0]}\t{dataBody[1]}'
            head = '\n'
            f.write(line)
    return True


if __name__ == "__main__":
    manager = PhoneBook_Manager(book_path=book_Path)
    # manager.update_all_token()

    crapper = TangleScrapper(stepLen=0.0017)
    print(crapper.loc_list)

    scannedPoint, bikes_dict = crapper.tree_slice(phoneBook_path=book_Path, return_bike_info=True, logON=False)
    crapper.bike_count_details(bikes_dict)
    print(len(scannedPoint))
    shader = BikeDataShaders(bikes_dict)
    timeFolder = folderHelper.open_CurTime_folder()
    shader.scanned_points(scannedPoint,
                          timeFolder + 'images/' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M') + '.png')

    dumpBike_data(bikes_dict, folderHelper.open_CurTime_folder())
    # shader.distributeHotMap()
    BadDataCleaner.normal_data_clean()  # bad data cleanup
    print(len(bikes_dict))
