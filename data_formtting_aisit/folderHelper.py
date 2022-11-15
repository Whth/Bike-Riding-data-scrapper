import os
import time

ROOT = 'L:/pycharm projects/Bike_Scrapper/'
ASSET_ROOT_FOLDER = ROOT + 'RecoveredBikeData/'

bikeData_file_name = "allBikes.csv"
bikeData_log_file_name = "bikes_variant.log"

phoneNumber_file_name = 'phoneBook.json'
phoneNumber_file_pdir = 'main/'
phoneNumber_file_path = ROOT + phoneNumber_file_pdir + phoneNumber_file_name

background_img_folder = ASSET_ROOT_FOLDER + 'img/'
"""
noticing that the phone number given token does not get expired immediately

so below are the new phone numbers format 
XD
"""
DEFAULT_VALUE = -1.0


def open_CurTime_folder(rootFolder: str = ASSET_ROOT_FOLDER, CREATES_basic_datafile: bool = False):
    """
    :param CREATES_basic_datafile:
    :returns the dirName it creates
    :param rootFolder:
    :return: the dir that creates
    """

    time_str = time.strftime('%Y-%m %d', time.localtime())
    firstFolder, secondFolder = tuple(time_str.split())

    created_folder = f'{rootFolder}{firstFolder}/{secondFolder}/'
    if os.path.exists(created_folder + 'images/'):
        pass
    else:
        print('create images/')
        os.makedirs(created_folder + 'images/')
    if os.path.exists(created_folder):
        return created_folder
    else:
        os.makedirs(created_folder)

    if os.path.exists(created_folder):

        print(f'timeTreeFolder {created_folder} has been created')
        if CREATES_basic_datafile:
            with open(created_folder + bikeData_file_name, mode='w') as f:
                f.close()
            with open(created_folder + bikeData_log_file_name, mode='w') as f:
                f.close()
            print('basic_datafile created')
        return created_folder
    else:
        raise FileNotFoundError


if __name__ == '__main__':
    print(open_CurTime_folder())
    pass
