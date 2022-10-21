import os

from Funcdev import DEFAULT_COOLDOWN

ROOT_FOLDER = 'RecoveredBikeData/'

phoneNumber_file_name = 'local_phone.txt'
phoneNumber_file_pdir = 'main/'
phoneNumber_file_path = phoneNumber_file_pdir + phoneNumber_file_name

"""
noticing that the phone number given token does not get expired immediately

so below are the new phone numbers format 
XD
"""
DEFAULT_VALUE = -1.0

normal_format_dict = {'PhoneNumber': DEFAULT_VALUE, 'last_phone_used_time': DEFAULT_VALUE,
                      'expired_code': DEFAULT_VALUE, 'LoginToken': '', 'last_LoginToken_used_time': DEFAULT_VALUE,
                      'CoolDown_time': DEFAULT_VALUE}

normal_format_order = ['PhoneNumber', 'last_phone_used_time',
                       'LoginToken', 'expired_code', 'last_LoginToken_used_time', 'CoolDown_time']


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


def cheek_local_phone_format() -> int:
    """
    check text format
    1.create one if None
    2.return BAD LINE serial
    -1 normal
    0 new blank
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
                    raise Exception

            print(f'[{lineCounter}] lines with content in total, No obvious error')
        return -1
    else:
        # creating a new phone number file
        with open(phoneNumber_file_path, "a") as f:
            f.close()
        return 0


def sync_phone_txt(add=phoneNumber_file_path):
    """
    hard reset {phoneNumber_file_name}
    record phone number and then create a new {phoneNumber_file_name} with other data reset to -1
    """
    with open(add, "r") as f:  # record all the phone numbers
        lineCounter = 0
        phone_number_list = []
        line = f.readline()
        while line != '':
            line = line.split()
            lineCounter += 1

            print(f'current OverWriting line {lineCounter} : {line}')

            phone_number_list.append(line[0])  # phone number list assemble
            line = f.readline()  # next line

    with open(add, "w") as f:  # draw the records to the text and sync other data
        for phoneNumber in phone_number_list:
            f.write(phoneNumber)
            for ele in range(len(normal_format_order) - 2):
                f.write(f' {DEFAULT_VALUE}')
            f.write(f' {DEFAULT_COOLDOWN}\n')  # default cooldown time
