import os
import time

ASSET_ROOT_FOLDER = 'RecoveredBikeData/'

bikeData_file_name = "allBikes.txt"
bikeData_log_file_name = "bikes_variant.log_scanData"
phoneNumber_file_name = 'local_phone.txt'
phoneNumber_file_pdir = 'main/'
phoneNumber_file_path = phoneNumber_file_pdir + phoneNumber_file_name

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
    if rootFolder == '':
        rootFolder = os.path.abspath('.')  # current directory
    time_str = time.strftime('%Y-%m %d', time.localtime())
    firstFolder = time_str.split()[0]
    secondFolder = time_str.split()[1]
    created_folder = f'{rootFolder}/{firstFolder}/{secondFolder}/'
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
        raise


if __name__ == '__main__':
    if cheek_local_phone_format() > 0:
        sync_phone_txt(phoneNumber_file_path)
