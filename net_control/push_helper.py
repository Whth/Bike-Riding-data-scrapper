import datetime
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

    def pushInfo(self, DetectedBikesCount, ScannedPointsCount, dataset=None):

        msg = f'DetectedBikesCount: {DetectedBikesCount}\nScannedPointsCount: {ScannedPointsCount}\n'
        if dataset:
            msg = msg + f'\n\n{dataset}'
        self.send_message(msg
                          ,
                          uids=self.UIDS,
                          topic_ids=self.TOPIC_IDS,
                          token='AT_7gneRS02ois8YkgVWeCS0Q9iEV3Lq4Xl')

    @staticmethod
    def log_scanData(bikeNo_dict: dict):
        """
        :return:
        """
        log_dir = open_CurTime_folder() + bikeData_log_file_name

        log_content = {
            'totalDetectedBikes': len(bikeNo_dict),
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%s')
        }

        if not os.path.exists(log_dir):  # check if the log_scanData file exists
            with open(log_dir, mode='w'):
                pass
        with open(log_dir, mode='a') as log:
            for content_ele in log_content.keys():
                log.write(f'{log_content[content_ele]}\t')
            log.write('\n')
