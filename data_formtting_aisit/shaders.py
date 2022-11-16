import datetime
import json
import os

import matplotlib.pyplot as plt

from folderHelper import bikeData_log_file_name


class DataRenderer(object):

    def __init__(self, dataRoot: str):
        self.dataRoot = dataRoot
        self.var_log_path = f'{dataRoot}\{bikeData_log_file_name}'

        self.all_data_log = []
        self.load_log()
        print(f'{self.var_log_path}')

        if len(self.all_data_log):
            self.dataKeys = self.all_data_log[0].keys()

    def var_line_map(self, varName: str):
        data_list = []
        timeStamp_list = []

        for log in self.all_data_log:
            data_list.append(log.get(varName))
            timeStamp = datetime.datetime.strptime(log.get('timeStamp'), "%Y-%m-%d-%H-%M")
            timeStamp_list.append(timeStamp.hour)
        # print(f'{data_list}|{timeStamp_list}')
        plt.figure(dpi=200)
        plt.suptitle(varName, fontsize='large')
        plt.bar(timeStamp_list, data_list)
        plt.tight_layout()
        plt.show()
        pass

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

    def all_map(self):
        for key in self.dataKeys:
            if key == 'timeStamp':
                continue
            self.var_line_map(key)


if __name__ == '__main__':
    deal_path = 'L:\pycharm projects\Bike_Scrapper\RecoveredBikeData\\2022-11\\15'
    render = DataRenderer(deal_path)
    render.all_map()
    pass
