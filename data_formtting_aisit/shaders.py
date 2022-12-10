import datetime
import json
import os

import matplotlib.pyplot as plt

from folderHelper import bikeData_log_file_name


class DataRenderer(object):
    """
    simply render the log file data
    """

    def __init__(self, dataRoot: str):
        self.dataRoot = dataRoot
        self.var_log_path = f'{dataRoot}\{bikeData_log_file_name}'

        self.all_data_log = []
        self.load_log()
        print(f'{self.var_log_path}')

        if len(self.all_data_log):
            # get the data set name
            self.dataKeys = self.all_data_log[0].keys()

    def var_line_map(self, varName: str, SAVE_IMG_FOLDER: str == ''):
        data_list = []
        timeStamp_list = []

        for log in self.all_data_log:
            data_list.append(log.get(varName))
            timeStamp = datetime.datetime.strptime(log.get('timeStamp'), "%Y-%m-%d-%H-%M")
            timeStamp_list.append(timeStamp.hour)
        # print(f'{data_list}|{timeStamp_list}')
        plt.figure(dpi=200),
        plt.suptitle(varName, fontsize='large')
        plt.xlabel('Time (/hr)', loc='right'), plt.ylabel('bikeCount (/count)', loc='top')
        plt.tick_params(axis='x', size=15)
        plt.bar(timeStamp_list, data_list)

        plt.tight_layout(pad=2)
        if SAVE_IMG_FOLDER:
            file_path = fr'{SAVE_IMG_FOLDER}\{varName}.png'

            print(f'save at {file_path}')
            plt.savefig(file_path)
        plt.show()
        pass

    @staticmethod
    def data_pie(data_dict: dict):
        """
        draw pie
        :param data_dict:
        :return:
        """
        AllBikeCount = data_dict.get('HALL_bike_sum')
        ignore_GATE = True
        labels = list(data_dict.keys())[2:-1]  # 定义标签
        if ignore_GATE:
            temp = []
            for label in labels:
                if 'GATE' not in label and label != 'COLONY_AREA':
                    temp.append(label)
            labels = temp

        sets = []  # a list to store the AREA bike COUNT data
        for label in labels:
            sets.append(data_dict.get(label))

        explode = [0] * (len(labels))  # 突出显示，这里仅仅突出显示第二块（即'Hogs'）
        explode[0] += 0.05

        plt.figure(dpi=200)
        plt.pie(sets, explode=explode, labels=labels, autopct='%1.1f%%', startangle=90)

        plt.legend(loc=1, prop={'size': 6})

        plt.title('BikeDistributed PIE', weight="bold")
        plt.axis('equal')  # 显示为圆（避免比例压缩为椭圆）
        plt.tight_layout()
        plt.show()

    def load_log(self):
        load_counter = 0
        if os.path.exists(self.var_log_path):
            with open(self.var_log_path, mode='r') as log:
                for line in log.readlines():
                    if line != '' and line != '\n':
                        load_counter += 1
                        self.all_data_log.append(json.loads(line))

            print(f'Load {load_counter} logs')
        else:
            raise FileNotFoundError

    def all_map(self, SAVE_IMG_FOLDER: str = ''):
        if os.path.exists(SAVE_IMG_FOLDER):
            pass
        else:
            os.makedirs(SAVE_IMG_FOLDER)
        for key in self.dataKeys:
            if key == 'timeStamp':
                continue
            self.var_line_map(key, SAVE_IMG_FOLDER)

    def all_pie(self):
        for log in self.all_data_log:
            self.data_pie(log)


if __name__ == '__main__':
    from folderHelper import directView_folder_name

    for daySerial in range(13, 20):
        deal_path = rf'L:\pycharm projects\Bike_Scrapper\RecoveredBikeData\2022-11\{daySerial}'
        render = DataRenderer(deal_path)
        render.all_map(SAVE_IMG_FOLDER=rf'{deal_path}\{directView_folder_name}')
