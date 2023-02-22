import copy
import json
import random
import time
import warnings
from datetime import datetime

import numpy as np
import requests

import folderHelper
import req_misc
from folderHelper import bikeData_log_file_name
from phoneBookManager import PhoneBook_Manager

"""
lng lat ,lng lat

lat
|
|
|_______lng
"""
BOUND_LOCATION = [120.691208, 27.913032, 120.709791, 27.931309]

NORTHERN_SCH = [120.701227, 27.922759, BOUND_LOCATION[2], BOUND_LOCATION[3]]
NORTHERN_SCH_GATE = [120.704141, 27.924129]
NORTHERN_SCH_GATE_AREA = [120.703043, NORTHERN_SCH[1], 120.705006, 27.924429]

SOUTHERN_SCH = [BOUND_LOCATION[0], BOUND_LOCATION[1], 120.701335, 27.920465]
SOUTHERN_SCH_GATE = [120.700536, 27.917799]
SOUTHERN_SCH_GATE_AREA = [120.699958, 27.916437, SOUTHERN_SCH[2], 27.918875]

DE_AREA = [120.705654, 27.916654, 120.708851, 27.919135]
DE_AREA_GATE = [120.70884, 27.918759]

C_AREA = [120.7056, DE_AREA[3], BOUND_LOCATION[2], NORTHERN_SCH[1]]
C_AREA_GATE = [120.706458, 27.921396]

MALL_AREA = [SOUTHERN_SCH[2], BOUND_LOCATION[1], BOUND_LOCATION[2], DE_AREA[1]]
MALL_AREA_GATE = [120.706158, 27.916794]
COLONY_AREA = [120.692472, 27.921593, 120.697504, 27.92548]  # a place where a lot of bikes are stored

INVESTIGATE_AREA = [NORTHERN_SCH, NORTHERN_SCH_GATE_AREA,
                    SOUTHERN_SCH, SOUTHERN_SCH_GATE_AREA,
                    DE_AREA, C_AREA,
                    COLONY_AREA, MALL_AREA]
AREA_PARK_LOC = [NORTHERN_SCH_GATE, SOUTHERN_SCH_GATE, DE_AREA_GATE, C_AREA_GATE, MALL_AREA_GATE]

IG_1 = [120.687941, 27.927006, 120.696267, 27.931557]
IG_2 = [120.686324, 27.922987, 120.691174, 27.928371]

IGNORE_AREA = [IG_1, IG_2]


def check_in_polygon(point: list, polygon_node_list: list) -> bool:
    """

    :param point: [lng ,lat]
    :param polygon_node_list: a list that contains all the node of tht polygon
    :return: if the point is in polygon
    """
    pass


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
                      INSERT_TIMESTAMP: bool = False, TIMESTAMP: datetime = None, RETURN_DENSITY: bool = False,
                      BAD_CHECK=True, Hold_retry=False):
    """
    功能：获取某一经纬度周边500(?)米的所有单车信息
    1.传入经纬度和token值
    2.如果顺利，返回经纬度周围500米的所有单车信息，否则显示异常信息
    """
    assert (INSERT_TIMESTAMP is False and TIMESTAMP is None) or (
            INSERT_TIMESTAMP is True and TIMESTAMP is not None), "forget match INSERT_TIMESTAMP and TIMESTAMP?"

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
    for i in range(max_retries):  # max retries 3 times
        try:
            with requests.post(get_bike_url, headers=req_misc.a_random_header(), data=json.dumps(req_load),
                               timeout=8) as echo:
                bikeData_return = echo
                if bikeData_return.status_code == 200:
                    break
                else:
                    print('sleep a while')
                    time.sleep(random.random())  # wait_time
        except TimeoutError:

            if requests.get('https://www.baidu.com/').status_code != 200:
                print('bad request')
                warnings.warn('MAY HAVE CORRUPTION')
                raise ConnectionError
            else:
                print(f'HOlD 20 seconds')
                time.sleep(20)
                if Hold_retry:
                    with requests.post(get_bike_url, headers=req_misc.a_random_header(), data=json.dumps(req_load),
                                       timeout=7) as echo:
                        bikeData_return = echo
                        if bikeData_return.status_code != 200:
                            print('blockage error')
                            raise ConnectionError

    Bike_raw_data_dict = json.loads(bikeData_return.text)  # return type is dict

    bike_data_list = Bike_raw_data_dict['data']

    time_stamp_key = 'timeStamp'

    if Bike_raw_data_dict['data']:
        if BAD_CHECK:
            if int(Bike_raw_data_dict['data'][0].get('bikeNo')) < 9000000000:
                print(Bike_raw_data_dict['data'])
                # print(Bike_raw_data_dict['data'][0].get('bikeNo'))
                warnings.warn(f'MAY have data corruption {datetime.now()}')

        if INSERT_TIMESTAMP:  # insert timestamp into data
            timeStamp = TIMESTAMP.strftime('%Y-%m-%d %H:%M')  # timestamp for this lap
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

    def __init__(self, loc_list: list = BOUND_LOCATION, stepLen: float = 0.0011, ignore_loc_list: list = IGNORE_AREA):
        """
        default constructor op on the whole school area
        :param loc_list:
        """
        self.loc_list = loc_list
        self.stepLen = stepLen
        self.ignore_loc_list = ignore_loc_list
        print(f'loc_list: {self.loc_list} stepLen: {stepLen}')
        print(f'IGNORE_AREA: {self.ignore_loc_list}')
        pass

    def rectangle_slice(self, precision: int = 6, REVERSE=False, SHAFFULL=False) -> list:
        """
        attention: This function will not function properly when called with a line_liked tangle,demanding img improvements
        BOUND_LOCATION: defined in the other docs

        :param REVERSE:
        :param precision:
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
                tempNode[0] = round(lngRange[i], precision)  # x
                tempNode[1] = round(latRange[j], precision)  # y
                node_list.append(tempNode.copy())
        if REVERSE:
            node_list.reverse()
        if SHAFFULL:
            random.shuffle(node_list)
        return node_list

    def tree_slice(self, phonebook_path, using_method: int = 1, return_bike_info: bool = False,
                   log_on=True, search_all=True, hall_timestamp: datetime = datetime.now()):
        """
        in book out bike_info and points Scanned
        :type hall_timestamp: object
        :param search_all:
        :param log_on:
        :param phonebook_path:
        :param using_method:
        :param return_bike_info:
        :return:
        """

        if using_method == 1:
            """
            dict for de duplicate

            this method will detect util every bike has at least 2 detected

            """
            min_detectedCount = 2
            HALL_SCAN_INTERVAL = 1
            last_time = time.time()

            init_time = datetime.now()

            Book = PhoneBook_Manager(phonebook_path)

            bikeNo_dict = {}  # storing the lng and lat and detected times
            # data_formatting = ['lng', 'lat', 'detectedBikes']
            loc_precision = 6
            root_points = []
            init_points = self.rectangle_slice(precision=loc_precision, SHAFFULL=True)

            temp_list = []  # to store the point's serial which is not empty
            print(f'scan init points at {init_time}')
            for serial, init_point in enumerate(init_points):
                token = Book.loop_token()
                if time.time() - last_time < HALL_SCAN_INTERVAL:  # to control HALL scan frequency
                    time.sleep(HALL_SCAN_INTERVAL)

                point_viewed_bikes = getBikes_reformed(init_point, token, INSERT_TIMESTAMP=True,
                                                       TIMESTAMP=hall_timestamp)  # requests
                bikesCount = len(point_viewed_bikes)

                print(f'[{serial + 1}/{len(init_points)}] [{bikesCount}] scanned '
                      f'{init_points[serial]}'
                      f'TimeConsumed: {datetime.now() - init_time} '
                      f'AllDetectedBikeCount: {len(bikeNo_dict)} |useToken: {token}')

                if bikesCount > 0:  # for point that is surrounded by multiple bikes

                    a_random_bike: dict = self.bike_selector(point_viewed_bikes,
                                                             selectMode=2)  # random get a bike from the requests result
                    location = [round(float(a_random_bike['lng']), loc_precision),
                                round(float(a_random_bike['lat']), loc_precision)]

                    if log_on:
                        print(f'chose bike that sits {location}')
                    if check_point_in_tangle(location, self.loc_list) and location not in root_points:
                        # preventing same location and external location
                        root_points.append(location)  # primitive layer

                    self.merge_dedup(bikeNo_dict, point_viewed_bikes)
                    temp_list.append(init_points[serial])
                else:

                    continue

            init_points = temp_list

            expand_list = []
            for point in self.coverage_check(bikeNo_dict, boundCount=min_detectedCount):  # get low coverage location
                if check_point_in_tangle(point, self.loc_list):
                    expand_list.append(point)

            root_points.extend(expand_list)  # second expand
            root_points = self.del_ignore_points(root_points)

            init_points.extend(root_points)  # combine two list
            init_points = self.del_ignore_points(init_points)

            print(f'scan second layer')

            if search_all:
                virtual_bound = True
                search_stack = []
                last_stack = []
                search_stack = root_points  # init search_stack with root_points

                random.shuffle(search_stack)

                stack_push_counter = 0
                min_increment = 12

                while len(search_stack) > 0:  # means there may be un scanned points

                    stack_push_counter += 1  # push
                    scanned_points = []
                    for i, point in enumerate(search_stack):  # deal with the stack

                        if point not in self.coverage_check(bikeNo_dict, boundCount=min_detectedCount):
                            # meaning that the bike on spot is now detected more or equal than min_detectedCount

                            print(f'batch|{stack_push_counter}| [{i}/{len(search_stack)}] {point} SKIP')
                            continue
                        else:
                            scanned_points.append(point)

                        token = Book.loop_token()

                        if time.time() - last_time < HALL_SCAN_INTERVAL:  # to control HALL scan frequency
                            time.sleep(HALL_SCAN_INTERVAL)

                        point_viewed_bikes = getBikes_reformed(point, token, INSERT_TIMESTAMP=True,
                                                               TIMESTAMP=hall_timestamp)
                        self.merge_dedup(bikeNo_dict, point_viewed_bikes)  # merge them add up the detectedCount

                        if virtual_bound:
                            self.inRange_prune(bikeNo_dict)  # del external bikes

                        print(
                            f'batch|{stack_push_counter}| [{i}/{len(search_stack)}] {point} [{len(point_viewed_bikes)}] '
                            f'TimeConsumed: {datetime.now() - init_time} '
                            f'AllDetectedBikeCount: {len(bikeNo_dict)} |useToken: {token} ')

                    self.bike_count_details(bikeNo_dict, statistics_list_len=30)

                    if search_stack is last_stack or abs(len(last_stack) - len(search_stack)) < min_increment:
                        # meaning no new bike was found or
                        break
                    last_stack = search_stack
                    search_stack = self.coverage_check(bikeNo_dict, boundCount=min_detectedCount)

                    init_points.extend(scanned_points)
                    time.sleep(3)

            consumedTime = datetime.now() - init_time
            print(f'Extracted point list length: {len(init_points)}')
            print(f'Extracted bike number: {len(bikeNo_dict)}')
            print(f'Consumed time: {consumedTime}')
            print(f'Scan [{(len(init_points) / consumedTime.seconds):.2f}] pt/s')

            if return_bike_info:
                return init_points, bikeNo_dict
            return init_points

        if using_method == 2:
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
                # timeStamp don't drive
                bike_info[3] += 1
            else:
                bikeNo_dict[bike['bikeNo']] = [bike['lng'], bike['lat'], bike['timeStamp'], 1]  # create if it not

    @staticmethod
    def coverage_check(bikeNo_dict, boundCount=2, precision=6) -> list:
        """

        :param precision:
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
                location = [round(float(bike_scan_data[0]), precision),
                            round(float(bike_scan_data[1]), precision)]  # convert str float

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

    @staticmethod
    def bike_selector(raw_bike_dicts: list, selectMode: int = 1) -> dict:
        """

        :param raw_bike_dicts:
        :param selectMode:
        :return:
        """
        selectedBike = {}
        if selectMode == 1:
            """
            select the a random bike
            """
            randomBikeSerial = random.randint(0, len(raw_bike_dicts) - 1)  # select a random bike
            return raw_bike_dicts[randomBikeSerial]
        elif selectMode == 2:

            """
            select bike that the longest distance between the selected
            """

            max_distance = 0.0
            serial = None
            for i, bike in enumerate(raw_bike_dicts):
                if float(bike.get('distance')) > max_distance:
                    max_distance = bike.get('distance')
                    serial = i
            if serial:
                return raw_bike_dicts[serial]
            else:
                warnings.warn('empty serial')
                return {}

    def inRange_prune(self, bikeNo_dict: dict) -> None:
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

    def del_ignore_points(self, points) -> list:
        temp_list = []

        for point in points:
            store = True

            for ignore_loc in self.ignore_loc_list:
                if check_point_in_tangle(point, ignore_loc):
                    store = False

            if store:
                temp_list.append(point)

        return temp_list


class DataSorter(object):

    def __init__(self, bikeNo_dict: dict, timeStamp: str, ):
        """

        :param bikeNo_dict:
        :param timeStamp:
        """
        self.bikeCountDataset = {}
        self.C_AREA_dict = {}
        self.DE_AREA_dict = {}
        self.SOUTHERN_SCH_dict = {}
        self.SOUTHERN_SCH_GATE_dict = {}

        self.NORTHERN_SCH_dict = {}
        self.NORTHERN_SCH_GATE_dict = {}

        self.MALL_AREA_dict = {}
        self.COLONY_AREA_dict = {}

        self.WANDERING_bike_sum: int = 0

        self.HALL_bike_sum: int = len(bikeNo_dict)
        self.bikeNo_dict: dict = bikeNo_dict
        self.timeStamp: str = timeStamp

        self.ALL_AREA_RESORT()

    @staticmethod
    def location_of_dict(bikeNo_dict_value: list) -> list:
        """

        :param bikeNo_dict_value:
        :return: lng ,lat  should all be str
        """
        location = [bikeNo_dict_value[0], bikeNo_dict_value[1]]
        return location

    def AREA_resort(self, AREA):
        """
        :AREA: target location
        :return: bikeNo_dict that contains bike in DE_AREA
        """
        temp = {}
        for bikeNo in self.bikeNo_dict.keys():
            loc = self.location_of_dict(bikeNo_dict_value=self.bikeNo_dict.get(bikeNo))
            if check_point_in_tangle(loc, AREA):
                temp[bikeNo] = self.bikeNo_dict.get(bikeNo)  # add the point to the sum dict

        return temp

    def ALL_AREA_RESORT(self, infoON=True, SAVE=True):
        print(f'ALL_AREA_RESORT')
        print(f'----------------------------------------------------------------')
        self.SOUTHERN_SCH_dict = self.AREA_resort(SOUTHERN_SCH)
        self.SOUTHERN_SCH_GATE_dict = self.AREA_resort(SOUTHERN_SCH_GATE_AREA)
        self.NORTHERN_SCH_dict = self.AREA_resort(NORTHERN_SCH)
        self.NORTHERN_SCH_GATE_dict = self.AREA_resort(NORTHERN_SCH_GATE_AREA)
        self.DE_AREA_dict = self.AREA_resort(DE_AREA)
        self.C_AREA_dict = self.AREA_resort(C_AREA)
        self.MALL_AREA_dict = self.AREA_resort(MALL_AREA)
        self.COLONY_AREA_dict = self.AREA_resort(COLONY_AREA)

        self.WANDERING_bike_sum = self.HALL_bike_sum - len(self.C_AREA_dict) - len(self.DE_AREA_dict) - len(
            self.SOUTHERN_SCH_dict) - len(self.NORTHERN_SCH_dict) - len(self.MALL_AREA_dict) - len(
            self.COLONY_AREA_dict)

        self.bikeCountDataset = {'HALL_bike_sum': self.HALL_bike_sum,
                                 'WANDERING_bike_sum': self.WANDERING_bike_sum,
                                 'SOUTHERN_SCH': len(self.SOUTHERN_SCH_dict),
                                 'SOUTHERN_SCH_GATE_AREA': len(self.SOUTHERN_SCH_GATE_dict),
                                 'NORTHERN_SCH': len(self.NORTHERN_SCH_dict),
                                 'NORTHERN_SCH_GATE_AREA': len(self.NORTHERN_SCH_GATE_dict),
                                 'DE_AREA': len(self.DE_AREA_dict),
                                 'C_AREA': len(self.C_AREA_dict),
                                 'MALL_AREA': len(self.MALL_AREA_dict),
                                 'COLONY_AREA': len(self.COLONY_AREA_dict),
                                 'timeStamp': self.timeStamp}

        if infoON:
            for key in self.bikeCountDataset.keys():
                print(f'{key}: {self.bikeCountDataset.get(key)}')
        if SAVE:
            with open(folderHelper.open_CurTime_folder() + bikeData_log_file_name, mode='a') as f:
                f.write(f'{json.dumps(self.bikeCountDataset)}\n')


if __name__ == '__main__':
    pass
TEST_POINT = (120.695064, 27.916269)  # our main teaching building
