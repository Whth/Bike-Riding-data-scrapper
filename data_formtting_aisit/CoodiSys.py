import copy
import datetime
import json
import random
import time
import warnings

import numpy as np
import requests
from matplotlib import pyplot as plt

import req_misc
from phoneBookManager import PhoneBook_Manager

"""
lng lat ,lng lat
"""
BOUND_LOCATION = [120.691208, 27.913032, 120.709791, 27.931309]

NORTHERN_SCH = [120.701227, 27.922759, BOUND_LOCATION[2], BOUND_LOCATION[3]]
SOUTHERN_SCH = [BOUND_LOCATION[0], BOUND_LOCATION[1], 120.701335, 27.920465]

DE_AREA = [120.706223, 27.91666, 120.708851, 27.919135]

C_AREA = [120.701227, 27.922759, BOUND_LOCATION[2], NORTHERN_SCH[1]]
MALL = [SOUTHERN_SCH[2], BOUND_LOCATION[1], BOUND_LOCATION[2], DE_AREA[1]]


def check_point_in_tangle(point: list, tangle: list) -> bool:
    """

    :param point:
    :param tangle:
    :return:
    """
    temp = [float(point[0]), float(point[1])]
    point = temp
    inRange = False
    if tangle[0] < point[0] < tangle[2] and tangle[1] < point[1] < tangle[3]:  # x lock y lock
        inRange = True

    return inRange


def getBikes_reformed(point_coordinates: list, token: str, USE_NEW_VERSION=False,
                      INSERT_TIMESTAMP: bool = False, RETURN_DENSITY: bool = False, BAD_CHECK=True, Hold_retry=False):
    """
    功能：获取某一经纬度周边500(?)米的所有单车信息
    1.传入经纬度和token值
    2.如果顺利，返回经纬度周围500米的所有单车信息，否则显示异常信息
    retry on time SOUTHERN_SCH error
    """

    req_load = {"version": "4.2.3", "from": "h5", "systemCode": 63, "platform": 1,
                "action": "user.ride.nearBikes",
                "lng": point_coordinates[0], "lat": point_coordinates[1],
                "currentLng": point_coordinates[0], "currentLat": point_coordinates[1],
                "cityCode": "0577", "adCode": "330304", "token": token
                }

    req_load_new = {
        "version": "6.17.0", "from": "h5", "systemCode": 63, "platform": 1,
        "action": "user.ride.nearBikes",
        "lng": point_coordinates[0], "lat": point_coordinates[1],
        "currentLng": point_coordinates[0], "currentLat": point_coordinates[1],
        "adCode": "330304", "cityCode": "0577", "token": token,
        "ticket": "MTY3MjQxMjQ3Mg==.su9UiPSWh6VGUPHMqk8tpmD3wpgVr8eB464cPOT/J9o="
    }
    # well the tiket is by the account
    if USE_NEW_VERSION:
        req_load = req_load_new

    get_bike_url = 'https://api.ttbike.com.cn/api?user.ride.nearBikes'

    bikeData_return = None
    max_retries = 3

    try:
        for i in range(max_retries):  # max retries 3 times

            with requests.post(get_bike_url, headers=req_misc.a_random_header(), data=json.dumps(req_load),
                               timeout=7) as echo:
                bikeData_return = echo
            if bikeData_return:
                break
            else:
                print('sleep a while.pr')
                time.sleep(random.random())  # wait_time
    except:
        if requests.get('https://www.baidu.com/') != 200:
            print('bad request')
            raise Exception
        print(f'HOlD 20 seconds')
        time.sleep(20)
        if Hold_retry:
            return getBikes_reformed(point_coordinates=point_coordinates, token=token,
                                     INSERT_TIMESTAMP=INSERT_TIMESTAMP, USE_NEW_VERSION=USE_NEW_VERSION,
                                     RETURN_DENSITY=RETURN_DENSITY, BAD_CHECK=BAD_CHECK)

        return []

    Bike_raw_data_dict = json.loads(bikeData_return.text)  # return type is dict

    """

    passCode = 0
    expiredCode = 133
    """
    bike_data_list = Bike_raw_data_dict['data']

    time_stamp_key = 'timeStamp'

    if Bike_raw_data_dict['data']:
        if BAD_CHECK:
            if int(Bike_raw_data_dict['data'][0].get('bikeNo')) < 9000000000:
                print(Bike_raw_data_dict['data'])
                # print(Bike_raw_data_dict['data'][0].get('bikeNo'))

                warnings.warn(f'MAY have data corruption {datetime.datetime.now()}')
        if INSERT_TIMESTAMP:  # insert timestamp into data
            timeStamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')  # timestamp for this lap
            for bike_dict in bike_data_list:
                bike_dict[time_stamp_key] = timeStamp  # inserting
        if RETURN_DENSITY:
            distance_list = []

            for bike in bike_data_list:
                distance_list.append(float(bike.get('distance')))  # extract distance

            return bike_data_list, np.mean(distance_list)  # return average distance

        return bike_data_list  # a list

    else:
        # print(bikeData_return.text)
        warnings.warn(f'## EMPTY ECHO ## : {token}')
        return []


class FakeDataConstructor(object):

    def __init__(self):
        self.fakeDataList = []


class TangleScrapper(object):

    def __init__(self, loc_list: list = BOUND_LOCATION, stepLen: float = 0.0011):
        """
        default constructor op on the whole school area
        :param loc_list:
        """
        self.loc_list = loc_list
        self.stepLen = stepLen

        pass

    def rectangle_slice(self, disPlayPic: bool = False) -> list:
        """
        attention: This function will not function properly when called with a line_liked tangle,demanding img improvements
        BOUND_LOCATION: defined in the other docs
        :param disPlayPic:
        :param step:
        :return: node_list containing point within the rectangle defined by two conner

        lat
        |
        |
        |_______lng
        """
        MIN_INTERVal = 0.0011
        if self.stepLen < MIN_INTERVal:
            warnings.warn(f'interval for step is too low')  # preventing over pulling

        node_list = []
        Node = [0, 0]

        latRange = np.arange(self.loc_list[1], self.loc_list[3], self.stepLen)
        lngRange = np.arange(self.loc_list[0], self.loc_list[2], self.stepLen)

        total_nodes_counter = len(lngRange) * len(latRange)
        print(f'the monitoring area contains {total_nodes_counter}')
        for i in range(len(lngRange)):
            for j in range(len(latRange)):
                tempNode = copy.deepcopy(Node)
                tempNode[0] = lngRange[i]  # x
                tempNode[1] = latRange[j]  # y
                node_list.append(tempNode.copy())
        if disPlayPic:
            data_display_multiplier = 1

            plt.figure(figsize=(len(lngRange) / 1.2, len(latRange) / 1.2), dpi=130)

            plt.axis('equal')

            for node in node_list:
                plt.scatter(node[0], node[1], s=5)
                plt.scatter(node[0], node[1], alpha=0.5, s=2000)

            plt.grid()

            """
            labeling
            """
            plt.suptitle(f"({len(lngRange)}X{len(latRange)}) {len(node_list)} Points", fontsize=16, color='blue')
            plt.title(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
            plt.xlabel(f'Longitude deg', loc='left')
            plt.ylabel(f'Latitude deg', loc='top')

            plt.show()
        return node_list

    def tree_slice(self, phoneBook_path, usingMethod=1, return_bike_info: bool = False,
                   logON=True, virtual_bound=True, SEARCH_ALL=True):
        """
        in book out bike_info and points Scand
        :param SEARCH_ALL:
        :param virtual_bound:
        :param logON:
        :param phoneBook_path:
        :param usingMethod:
        :param return_bike_info:
        :return:
        """

        if usingMethod == 1:
            """
            dict for de duplicate

            this method will detect util every bike has at least 2 detected

            """

            init_time = datetime.datetime.now()

            Book = PhoneBook_Manager(phoneBook_path)

            bikeNo_dict = {}  # storing the lng and lat and detected times
            # data_formatting = ['lng', 'lat', 'detectedBikes']

            root_points = []
            init_points = self.rectangle_slice()

            temp_list = []  # to store the point's serial which is not empty
            print(f'scan init points at {init_time}')
            for serial, init_point in enumerate(init_points):

                point_viewed_bikes = getBikes_reformed(init_point, Book.loop_token(), INSERT_TIMESTAMP=True)  # requests
                bikesCount = len(point_viewed_bikes)

                print(f'[{serial + 1}/{len(init_points)}] [{bikesCount}] bikes scanned '
                      f'TimeConsumed: {datetime.datetime.now() - init_time} '
                      f'AllDetectedBikeCount: {len(bikeNo_dict)}')

                if bikesCount > 0:  # for point that is surrounded by multiple bikes
                    randomBikeSerial = random.randint(0, bikesCount - 1)  # select a random bike

                    a_random_bike: dict = point_viewed_bikes[
                        randomBikeSerial]  # random get a bike from the requests result
                    location = [float(a_random_bike['lng']), float(a_random_bike['lat'])]
                    if logON:
                        print(f'chose [{randomBikeSerial}] {location}')
                    if location not in root_points:  # preventing same location
                        root_points.append(location)  # primitive layer

                    self.merge_dedup(bikeNo_dict, point_viewed_bikes)
                    temp_list.append(init_points[serial])
                else:

                    continue

            init_points = temp_list

            expand_list = self.coverage_check(bikeNo_dict)
            root_points.extend(expand_list)  # second expand
            init_points.extend(root_points)  # combine two list

            print(f'scan second layer')

            if SEARCH_ALL:
                search_stack = []
                last_stack = 0
                search_stack = root_points  # init search_stack with root_points
                min_detectedCount = 2

                stack_push_counter = 0
                min_increment = 5

                while len(search_stack) > 0:  # means there may be un scanned points

                    last_stack = search_stack
                    stack_push_counter += 1  # push
                    for i, point in enumerate(search_stack):
                        token = Book.loop_token()
                        point_viewed_bikes = getBikes_reformed(point, token, INSERT_TIMESTAMP=True)

                        print(
                            f'batch|{stack_push_counter}| [{i}/{len(search_stack)}] {point} [{len(point_viewed_bikes)}] '
                            f'AllDetectedBikeCount: {len(bikeNo_dict)} |useToken: {token} ')
                        self.merge_dedup(bikeNo_dict, point_viewed_bikes)  # merge them add up the detectedCount
                        if virtual_bound:
                            self.inRange_pruner(bikeNo_dict)  # del external bikes

                    self.bike_count_details(bikeNo_dict)

                    search_stack = []
                    search_stack = self.coverage_check(bikeNo_dict, boundCount=min_detectedCount)

                    if search_stack is last_stack:
                        # meaning no bike was found

                        break
                    else:
                        random.shuffle(search_stack)

                    if abs(len(last_stack) - len(search_stack)) < min_increment:
                        break
                    init_points.extend(search_stack)
                    time.sleep(3)

            self.bike_count_details(bikeNo_dict)

            print(f'Extracted list length: {len(init_points)}')
            print(f'Extracted bike number: {len(bikeNo_dict)}')

            if return_bike_info:
                return init_points, bikeNo_dict
            return init_points

        if usingMethod == 2:
            pass

    @staticmethod
    def merge_dedup(bikeNo_dict, point_viewed_bikes) -> None:
        """

        :param bikeNo_dict:
        :param point_viewed_bikes:
        :return:
        """
        for bike in point_viewed_bikes:  # record the bike detectedCount

            if bikeNo_dict.get(bike['bikeNo']):
                bike_info = bikeNo_dict[bike['bikeNo']]
                bike_info[0], bike_info[1] = bike['lng'], bike['lat']
                # timeStamp don't move
                bike_info[3] += 1
            else:
                bikeNo_dict[bike['bikeNo']] = [bike['lng'], bike['lat'], bike['timeStamp'], 1]  # create if it not

    @staticmethod
    def coverage_check(bikeNo_dict, boundCount=2) -> list:
        """

        :param boundCount:
        :param bikeNo_dict:
        :return: a location list contains bike loc whose detectedCount is less than boundCount
        """
        loc_list = []
        bikeNo_list = list(bikeNo_dict.keys())  # list of bikeNo int type
        for bikeNo in bikeNo_list:  # append to bike loc whose detectedCount is less than 2
            bike_scan_data: list = bikeNo_dict[bikeNo]  # contains Bike counter
            if bike_scan_data[-1] >= boundCount:
                # detected more than once ,covered,next
                continue
            else:
                location = [float(bike_scan_data[0]), float(bike_scan_data[1])]  # convert str float

                loc_list.append(location)  # the point loc out

        return loc_list

    @staticmethod
    def bike_count_details(bikeNo_dict, infoON=True, statistics_list_len=60) -> list:
        """

        :param statistics_list_len:
        :param infoON:
        :param bikeNo_dict:
        :return: a list
        """

        allCounter = [0] * statistics_list_len  # each number with its serial is bikesCount and detectedCount
        # each counter [count ,the count of the bike that has been detected {count} times]
        for i, bikeNo in enumerate(list(bikeNo_dict.keys())):
            if bikeNo_dict.get(bikeNo)[-1] > statistics_list_len - 1:
                allCounter[0] += 1  # for bike whose detectedCount is more than the statistics_list_len
                continue

            allCounter[bikeNo_dict.get(bikeNo)[-1]] += 1  # for normal_data

        if infoON:
            print('--------------------------------')
            for i, bikeCount in enumerate(allCounter):
                if i:
                    print(f'detected {i} times: {bikeCount}')
                else:
                    print(f'detected more than {statistics_list_len - 1} times: {bikeCount}')
            print('--------------------------------')
        return allCounter

    def inRange_pruner(self, bikeNo_dict: dict) -> None:
        """

        :param bikeNo_dict:
        :return:
        """
        counter = 0
        for bikeNo in list(bikeNo_dict.keys()):
            location = [bikeNo_dict.get(bikeNo)[0], bikeNo_dict.get(bikeNo)[1]]

            if check_point_in_tangle(location, self.loc_list):
                continue
            else:
                counter += 1
                del bikeNo_dict[bikeNo]

        print(f'totally delete {counter} external bikes')


if __name__ == '__main__':
    pass
TEST_POINT = (120.695064, 27.916269)  # our main teaching building
