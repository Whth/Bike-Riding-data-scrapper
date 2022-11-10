import os

from wxpusher import WxPusher

from folderHelper import open_CurTime_folder, bikeData_log_file_name


class WxPusher_comp(WxPusher):
    def __init__(self):
        self.TOKEN = ''
        self.UIDS = ['UID_zKFzOuemC8WJkw1vqSIHebgtBO9Q'
            ,
                     ]
        self.TOPIC_IDS = [
            '7619',
        ]

    def pushInfo(self, info: list):

        self.send_message(f'NormalFormatDBikes: {info[0]}\n'
                          f'DuplicatedBikes: {info[1]}\n'
                          f'ALL AREA TotalDetected: {info[0] + info[1]}\n',
                          uids=self.UIDS,
                          topic_ids=self.TOPIC_IDS,
                          token='AT_7gneRS02ois8YkgVWeCS0Q9iEV3Lq4Xl')

    @staticmethod
    def log_scanData(data: list):
        log_dir = open_CurTime_folder() + bikeData_log_file_name

        log_content = {
            'totalDetectedBikes': data[0],
            'timestamp': data[1]
        }

        if not os.path.exists(log_dir):  # check if the log_scanData file exists
            with open(log_dir, mode='w'):
                pass
        with open(log_dir, mode='a') as log:
            for content_ele in log_content.keys():
                log.write(f'{log_content[content_ele]}\t')
            log.write('\n')
