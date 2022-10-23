from wxpusher import WxPusher
TOKEN = ''
UIDS = ['UID_zKFzOuemC8WJkw1vqSIHebgtBO9Q'
    ,
        ]
TOPIC_IDS = [
    '7619',
]
WxPusher.send_message(f'NormalFormatDBikes: {bike_count_detail[0]}\n'
                      f'DuplicatedBikes: {bike_count_detail[1]}\n'
                      f'ALL AREA TotalDetected: {bike_count_detail[0] + bike_count_detail[1]}\n'


                      f'timestamp: {timestamp}\n'
                      f'NextCheckTime: {nextTime.strftime("%Y-%m-%d %H:%M")}',
                      uids=UIDS,
                      topic_ids=TOPIC_IDS,
                      token='AT_7gneRS02ois8YkgVWeCS0Q9iEV3Lq4Xl')
