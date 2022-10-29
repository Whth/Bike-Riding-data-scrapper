import os
import time

ASSET_ROOT_FOLDER = 'RecoveredBikeData/'

bikeData_file_name = "allBikes.txt"
bikeData_log_file_name = "bikes_variant.log"
phoneNumber_file_name = 'local_phone.txt'
phoneNumber_file_pdir = 'main/'
phoneNumber_file_path = phoneNumber_file_pdir + phoneNumber_file_name

"""
noticing that the phone number given token does not get expired immediately

so below are the new phone numbers format 
XD
"""
DEFAULT_VALUE = -1.0


def get_all_lines_count(filenameAdd) -> int:
    """
    Get the number of lines in a file
    """
    with open(filenameAdd, 'r') as f:
        lines = f.readlines()
    return len(lines)


def get_lines_with_content_Count(filenameAdd) -> int:
    """

    :param filenameAdd:
    :return:
    """
    length = 0
    with open(filenameAdd, 'r') as f:
        lines = f.readlines()

        for line in lines:
            if line != '\n':
                length += 1
    return length


def cheek_local_phone_format(raiseExceptions=False) -> int:
    """
    check text format
    1.create one if None
    2.return BAD LINE serial
    True normal/new blank

    """

    print(f'cheek {phoneNumber_file_name} file existence')
    if os.path.exists(f"{phoneNumber_file_name}"):

        with open(phoneNumber_file_path, "r") as f:
            totalLinesCount = get_lines_with_content_Count(phoneNumber_file_path)
            lineCounter = 0
            while lineCounter < totalLinesCount:  # operate on lines with content
                line = f.readline()
                print(f'cheek line: {lineCounter}', end='')
                if len(line.split(' ')) == len(normal_format_order):  # equal len means fine formatting
                    lineCounter += 1
                    print('\tok!')
                else:
                    print('####bad line###')  # bad line no tolerance
                    if raiseExceptions:
                        raise Exception

                    return lineCounter
            print(f'[{lineCounter}] lines with content in total, No obvious error')
        return -1
    else:
        # creating a new phone number file
        with open(phoneNumber_file_path, "a") as f:
            f.close()
        return 0


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
