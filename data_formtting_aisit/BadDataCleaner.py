"""
Bad data cleaners
"""

import os
import time

import folderHelper


def fix_bad_allBikes(filename: str, infoON=True) -> bool:
    """
    sep good and bad data put em into different files
    :param filename:
    :return:
    """
    success_status = False
    # bad_data_list = []
    bad_data_counter = 0
    fineData_list = []
    bad_data_fileName = 'badData.txt'
    fine_data_fileName = 'allBikes.txt'

    if not os.path.exists(filename):
        raise  # target not foundError

    startTime = time.time()

    with open(filename, mode='r') as origin_file:
        raw_lines = origin_file.readlines()

    if len(raw_lines) == 0:
        success_status = False
        return success_status

    badFileAdd = os.path.dirname(filename) + '\\' + bad_data_fileName
    # badFileAdd[-1] = bad_data_fileName
    # badFileAdd = '/'.join(badFileAdd)

    with open(badFileAdd, mode='a') as bad_datafile:
        for line in raw_lines:
            if not check_is_good_bike(line):
                bad_data_counter += 1
                bad_datafile.write(line)
                continue
            fineData_list.append(line)

    with open(filename, mode='w') as origin_file:
        for line in fineData_list:
            origin_file.write(line)
    success_status = True
    """
    disPlay sec
    """
    if infoON:
        print('#############################')
        print(f'the target file length is: {len(raw_lines)}')
        print('fix operation Done')
        print(badFileAdd)
        print(f'using time: {(time.time() - startTime):.4f}s')
        print(f'Total goodBike_data count: {len(fineData_list)}')
        print(f'Total badBike_data count: {bad_data_counter}')
        print('#############################\n')
    return success_status


# <editor-fold desc="clean">
def iter_counter(number: int, start: int = 0, end: int = 15) -> int:
    NumberSum = 0
    curCount = 0
    number /= pow(10, start)
    while curCount < end and number > 0:
        NumberSum += number % 10
        number /= 10
        curCount += 1

    return NumberSum


# </editor-fold>


def check_BikeNo_chainSame(number: str, start: int = 0, end: int = None) -> bool:
    """

    :param number:
    :param start:
    :param end:
    :return:
    """

    # print(number)
    if number == '':
        print('blank number may have data corrupted')
        raise
    if end < start:
        raise

    counter = 0
    if len(number) < 2:
        return False

    head = number[start]

    for chars in number:
        counter += 1

        if counter > start and chars != head:
            return False
        if counter == end:
            return True
    return True


def check_is_good_bike(test_data: str) -> bool:
    """
    input data is a string contains timestamps| BikeNo| lat| lag

    Here only judge by the BikeNo
    :param test_data:
    :return:
    """
    BIkeNo = test_data.split('\t')[1]
    # print(f'the Number is {BIkeNo}')
    return not check_BikeNo_chainSame(BIkeNo, 2, 7)


def tree_folder_to_list(root: str = '.', filter_ON=False) -> list:
    """
    tree to list ,specifically find the
    :param filter_ON:
    :param root:
    :return:
    """
    fine_data_fileName = 'allBikes.txt'

    resultList = []
    folder_remain = [root]

    while len(folder_remain):

        for text_file in os.scandir(folder_remain.pop()):
            if os.path.isfile(text_file):
                if not filter_ON or filter_ON and text_file.name == fine_data_fileName:
                    resultList.append(text_file)  # put in an iter

                else:
                    pass
            else:
                folder_remain.append(text_file)
    print(f'{len(resultList)} files found\n'
          f'--------------------------------')
    for f in resultList:
        a = os.path.splitext(f)
        if a == '.log_scanData':
            del f
    return resultList


# print(tree_folder_to_list('L:\pycharm projects\master\main\RecoveredBikeData'))
# bad_data = '2022-10-06 23:33	22000001096	27.921054	120.691456\n'
#
# print(check_is_good_bike(bad_data))
# bad_data_txt = 'L:/pycharm projects/master/main/RecoveredBikeData/2022-10/02/allBikes.txt'
# fix_bad_allBikes(bad_data_txt)
def normal_data_clean() -> None:
    print('\n\nCLEANSE TIME')
    for file in tree_folder_to_list(folderHelper.ASSET_ROOT_FOLDER, filter_ON=True):
        fix_bad_allBikes(file.path, infoON=False)
    print('\n\nCLEANSE DONE')
    return


if __name__ == '__main__':
    normal_data_clean()
