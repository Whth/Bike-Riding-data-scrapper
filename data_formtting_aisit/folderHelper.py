import copy
import os
import time

ROOT = 'L:/pycharm projects/Bike_Scrapper/'
ASSET_ROOT_FOLDER = ROOT + 'RecoveredBikeData/'

bikeData_file_name = "allBikes.csv"
bikeData_log_file_name = "bikes_variant.log"

phoneNumber_file_name = 'phoneBook.json'
phoneNumber_file_pdir = 'main/'
phoneNumber_file_path: str = ROOT + phoneNumber_file_pdir + phoneNumber_file_name

background_img_folder = ASSET_ROOT_FOLDER + 'img/'

directView_folder_name = 'directView'
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


def fix_format(filename: str):
    new_f = []
    with open(filename, mode='r') as f:
        for line in f.readlines():
            new_f.append(copy.deepcopy(line.replace('\t\n', '\n')))
        print(f'readlines: {len(new_f)}')
    with open(filename, mode='w') as f:
        f.writelines(new_f)


def concatenate_txt_files(filenames, output_path):
    """
    put all data together
    :param filenames:
    :return:
    """

    with open(output_path, 'w') as outfile:
        for fname in filenames:
            with open(fname) as infile:
                outfile.write(infile.read())


def merge_logs(startDays: int, endDays: int, except_list: list) -> str:
    """
    only work on data in Nov
    tail not included
    :param startDays:
    :param endDays:
    :return:
    """
    assert endDays > startDays >= 13

    log_list = []
    year_month_folder = r'2022-11'
    baseDir = rf"{ASSET_ROOT_FOLDER}\{year_month_folder}"
    for i in range(startDays, endDays):
        if i in except_list:
            continue
        log_list.append(rf'{baseDir}\{i}\{bikeData_log_file_name}')

    if len(except_list):
        output_path = rf'{baseDir}\{startDays}-{endDays}merged_logs{len(except_list)}ignored.txt'
    else:
        output_path = rf'{baseDir}\{startDays}-{endDays}merged_logs.txt'
    concatenate_txt_files(log_list, output_path)
    return output_path


def merged_log_to_csv(log_path: str):
    """

    :param log_path:
    :param out_put_csv_path:
    :return:
    """
    import json
    """
    {"HALL_bike_sum": 1780,
    "WANDERING_bike_sum": 460, 
    "SOUTHERN_SCH": 520, 
    "NORTHERN_SCH": 358,
    "DE_AREA": 226,
    "C_AREA": 105,
    "MALL_AREA": 111,
    "timeStamp": "2022-11-13-11-38"}
    """
    with open(log_path, 'r') as f:
        lines = f.readlines()
    assert len(lines) > 0
    keys = json.loads(lines[0]).keys()

    merged_dict = {key: [] for key in keys}

    for i, line in enumerate(lines):
        log_data_dict = json.loads(line)
        for key in keys:
            merged_dict.get(key).append(log_data_dict.get(key))
    import pandas

    df = pandas.DataFrame.from_dict(merged_dict)
    out_put_csv_path = log_path.replace('.txt', '.csv')
    df.to_csv(out_put_csv_path, sep=',', index=False)
    print('done')


if __name__ == '__main__':
    ex_list = []
    merged_log_to_csv(merge_logs(15, 19, ex_list))
    merged_log_to_csv(r'L:\pycharm projects\Bike_Scrapper\RecoveredBikeData\2022-11\19_test.txt')
