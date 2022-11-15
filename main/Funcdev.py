import copy
import datetime
import os
import random
import time
import warnings

import matplotlib.pyplot as plt

import folderHelper
import push_helper
from CoodiSys import TangleScrapper, BOUND_LOCATION, DataSorter, AREA_PARK_LOC
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
    """
    lat
    |
    |
    |_______lng
    """

    def __init__(self, bikeNo_dict=None, scanned_points=None):
        if bikeNo_dict:
            self.bikeNo_dict: dict = bikeNo_dict
        if scanned_points:
            self.scanned = scanned_points
        self.bgImg = plt.imread(folderHelper.background_img_folder + 'Fix.jpg')

        pass

    def update_dataset(self, bikeNo_dict=None, scanned_points=None):
        if bikeNo_dict:
            self.bikeNo_dict: dict = bikeNo_dict
        if scanned_points:
            self.scanned = scanned_points

    def distributeHotMap(self, bikeNo_dict: dict, timeStamp, SAVE_IMG_PATH=''):
        """
        bike distributeHotMap
        :return:
        """

        def BikeNo_dict_to_XY(bikeNo_dict) -> tuple:
            """
            x :lng ,y :lat
            :param bikeNo_dict:
            :return:
            """
            xList, yList = [], []
            for bikeNo in bikeNo_dict:
                xList.append(float(bikeNo_dict.get(bikeNo)[0]))
                yList.append(float(bikeNo_dict.get(bikeNo)[1]))
            return xList, yList

        lng_list, lat_list = BikeNo_dict_to_XY(bikeNo_dict=self.bikeNo_dict)

        plt.figure(dpi=200)
        plt.imshow(self.bgImg, extent=self.extent_format(BOUND_LOCATION))

        plt.title('SCANNED BIKES', fontweight="bold")
        plt.suptitle(f'{timeStamp}||{len(bikeNo_dict)} BIKES')

        plt.scatter(lng_list, lat_list, marker='.', s=3, alpha=0.8, c='r')
        plt.xlabel('lng'), plt.ylabel('lat')

        plt.ticklabel_format(style='scientific')
        if SAVE_IMG_PATH:
            print(f'Save distributeHotMap img at {SAVE_IMG_PATH}')
            plt.savefig(SAVE_IMG_PATH)
        plt.show()
        pass

    def scanned_points(self, points, timeStamp, SAVE_IMG_PATH=''):
        """

        :param SAVE_IMG_PATH:
        :param points:
        :return:
        """

        def points_to_xyList(points_list) -> tuple:
            """
            x :lng ,y :lat
            :param points_list:
            :return:
            """
            xList = []
            yList = []
            for point in points_list:
                xList.append(point[0])
                yList.append(point[1])
            return xList, yList

        lng_list, lat_list = points_to_xyList(points_list=points)

        plt.figure(dpi=200)
        plt.imshow(self.bgImg, extent=self.extent_format(BOUND_LOCATION))  # insert AREA_divide_img

        plt.title('SCANNED POINTS', fontweight="bold")
        plt.suptitle(f'{timeStamp}||{len(points)} points')

        plt.scatter(lng_list, lat_list, marker='o', s=350, alpha=0.16, c='r')
        plt.xlabel('lng'), plt.ylabel('lat')

        plt.ticklabel_format(style='scientific')
        # plt.scatter(lng_list, lat_list, s=2000, alpha=0.6)

        if SAVE_IMG_PATH:
            print(f'Save scanned_points img at {SAVE_IMG_PATH}')
            plt.savefig(SAVE_IMG_PATH)
        plt.show()

        return

    def AREA_divide_img(self, AREA_list: list):
        """

        :param AREA_list:
        :return:
        """
        fig, ax = plt.figure(dpi=200)

        plt.imshow(self.bgImg, extent=self.extent_format(BOUND_LOCATION))

        def node_list(AREA: list):
            temp = []
            temp.append([AREA[0], AREA[1]])
            temp.append([AREA[0], AREA[3]])

            temp.append([AREA[2], AREA[3]])
            temp.append([AREA[2], AREA[1]])
            return temp

        def node_list_to_xy(nodes: list):
            lng = []
            lat = []
            for node in nodes:
                lng.append(node[0])
                lat.append(node[1])
            return lng, lat

        for i in range(len(AREA_list)):
            AREA = AREA_list[i]
            park = AREA_PARK_LOC[i]
            rect = plt.Rectangle(park, width=AREA[2] - AREA[0], height=AREA[3] - AREA[1])
            ax.add_patch(rect)
        ax.tight_layout()
        plt.show()

    def bikeCountLineMap(self, location, bikeUsage_list):
        """

        :param bikeUsage_list: [count]
        :param location:

        :return:
        """

        print(f'Drawing {location}')
        plt.figure(dpi=350)
        plt.suptitle(f'{location}')
        plt.xlabel('time')
        plt.ylabel('bikeCount')

        plt.xticks()

        plt.tick_params(axis='both', labelsize=4)

        pass

    @staticmethod
    def extent_format(loc_list):
        return loc_list[0], loc_list[2], loc_list[1], loc_list[3]


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

    with open(path, mode='a+') as f:
        for bike in bike_data.keys():
            dataBody: list = bikes_dict.get(bike)
            line = f'{dataBody[2]}\t{bike}\t{dataBody[0]}\t{dataBody[1]}\t\n'

            f.write(line)
    return True


def Countdown(seconds):
    while seconds > 0:
        seconds -= 1
        time.sleep(1)
        print(f'\rREMAINING {seconds}s to reACTIVATE', end='')
    return


if __name__ == "__main__":
    manager = PhoneBook_Manager(book_path=book_Path)
    manager.update_all_token()
    pusher = push_helper.WxPusher_comp()

    crapper = TangleScrapper(stepLen=0.00146)
    shader = BikeDataShaders()
    # shader.AREA_divide_img(INVESTIGATE_AREA)

    while True:
        try:
            try:
                scannedPoint, bikes_dict = crapper.tree_slice(phoneBook_path=book_Path, return_bike_info=True,
                                                              logON=False,
                                                              SEARCH_ALL=True)
            except:
                print("Exception")
                Countdown(60 + 60 * random.random())
                continue

            timeStamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')
            sorter = DataSorter(bikes_dict, timeStamp=timeStamp)
            pusher.pushInfo(len(bikes_dict), len(scannedPoint), sorter.bikeCountDataset)

            shader.update_dataset(bikes_dict, scannedPoint)

            timeFolder = folderHelper.open_CurTime_folder()
            pic_folder = timeFolder + 'images/'
            basic_name = timeStamp + '.png'
            print(f'dumpDATA at data')
            dumpBike_data(bikes_dict, folderHelper.open_CurTime_folder())
            print('save img')
            try:
                shader.scanned_points(scannedPoint, timeStamp, SAVE_IMG_PATH=pic_folder + 'ScannedPoints-' + basic_name)
                shader.distributeHotMap(bikes_dict, timeStamp,
                                        SAVE_IMG_PATH=pic_folder + 'BikeDistributedHotMap-' + basic_name)
            except:
                warnings.warn(f'Unable to save img')
                pass

            print(f"try save at {pic_folder}")
            print('SLEEPING')
            if datetime.datetime.now().hour > 5:
                Countdown(120 + 60 * random.random())
            else:
                Countdown(1800)
        except KeyboardInterrupt:

            print(f'\n\nEND')
            break
