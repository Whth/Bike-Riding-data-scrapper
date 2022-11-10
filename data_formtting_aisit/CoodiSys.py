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

SOUTHERN_SCH = [120.697855, 27.919326, 120.707664, 27.926667]
BOUND_LOCATION = [120.691208, 27.913032, 120.709791, 27.931309]
NORTHERN_SCH = [120.704529, 27.924249, 120.718147, 27.931749]
D_AREA = [120.706223, 27.91666, 120.708851, 27.919135]
D_PARK = [120.70648, 27.918711, 120.708036, 27.919072]
E_AREA = [120.714814, 27.922776, 120.716799, 27.924619]
A_AREA = [120.700832, 27.925936, 120.703653, 27.927596]
B_AREA = [120.70381, 27.929415, 120.708912, 27.932558]


def check_point_in_tangle(point: list, tangle: list) -> bool:
    """

    :param point:
    :param tangle:
    :return:
    """
    inRange = False
    if tangle[0] < point[0] < tangle[2]:  # x lock
        if tangle[1] < point[1] < tangle[3]:  # y lock
            inRange = True

    return inRange


def getBikes_reformed(point_coordinates: list, token: str, USE_NEW_VERSION=False,
                      INSERT_TIMESTAMP: bool = False, RETURN_DENSITY: bool = False, BAD_CHECK=True):
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
                time.sleep(random.random())  # wait_time
    except TimeoutError:
        print(f'HOlD 20 seconds')
        time.sleep(20)
        return []

    Bike_raw_data_dict = json.loads(bikeData_return.text)  # return type is dict

    """

    passCode = 0
    expiredCode = 133
    """
    bike_data_list = Bike_raw_data_dict['data']

    time_stamp_key = 'timeStamp'
    if INSERT_TIMESTAMP:  # insert timestamp into data
        timeStamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')  # timestamp for this lap
        for bike_dict in bike_data_list:
            bike_dict[time_stamp_key] = timeStamp  # inserting

    if Bike_raw_data_dict['data']:
        if BAD_CHECK:
            if int(Bike_raw_data_dict['data'][0].get('bikeNo')) < 9000000000:
                print(Bike_raw_data_dict['data'])
                print(Bike_raw_data_dict['data'][0].get('bikeNo'))
                warnings.warn(f'MAY have data corruption {datetime.datetime.now()}')
                keyboad = req_misc.input_with_timeout('enter y to continue|ay to all continue|sl to silent')
                allPass = False
                if keyboad == 'ay':
                    allPass = True
                if keyboad == 'y' or keyboad == 'Y':
                    raise ValueError
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

    def tree_slice(self, a_phoneBook: object = None, phoneBook_path=None, usingMethod=1, return_bike_info: bool = False,
                   logON=True):
        """
        in book out bike_info and points Scand
        :param logON:
        :param a_phoneBook:
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

            if a_phoneBook and not phoneBook_path:
                Book = a_phoneBook
            elif not a_phoneBook and not phoneBook_path:
                raise Exception
            init_time = datetime.datetime.now()

            Book = PhoneBook_Manager(phoneBook_path)
            timeStamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
            bikeNo_dict = {}  # storing the lng and lat and detected times
            # data_formatting = ['lng', 'lat', 'detectedBikes']

            root_points = []
            init_points = self.rectangle_slice()

            emptyPointSerials = []  # to store the point's serial which is empty
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
                else:
                    # delete the empty point
                    emptyPointSerials.append(serial)
                    continue

            for emptyPointSerial in emptyPointSerials:  # delete the empty point
                del init_points[emptyPointSerial]

            expand_list = self.coverage_check(bikeNo_dict)
            root_points.extend(expand_list)  # second expand
            init_points.extend(root_points)  # combine two list

            print(f'scan second layer')

            SEARCH_ALL = True
            if SEARCH_ALL:
                search_stack = []
                search_stack = root_points  # init search_stack with root_points
                min_detectedCount = 1
                stack_push_counter = 0
                while len(search_stack) > 0:  # means there may be un scanned points
                    random.shuffle(search_stack)
                    stack_push_counter += 1  # push
                    for i, point in enumerate(search_stack):
                        token = Book.loop_token()
                        point_viewed_bikes = getBikes_reformed(point, token, INSERT_TIMESTAMP=True)

                        print(
                            f'batch|{stack_push_counter}| [{i}/{len(search_stack)}] {point} [{len(point_viewed_bikes)}] '
                            f'AllDetectedBikeCount: {len(bikeNo_dict)} |useToken: {token} ')
                        self.merge_dedup(bikeNo_dict, point_viewed_bikes)  # merge them add up the detectedCount
                    search_stack = []
                    self.bike_count_details(bikeNo_dict)
                    for bikeNo in bikeNo_dict.keys():
                        if bikeNo_dict.get(bikeNo)[-1] == min_detectedCount:
                            location = [bikeNo_dict.get(bikeNo)[0], bikeNo_dict.get(bikeNo)[1]]  # lng lat
                            search_stack.append(location)
            else:
                for i, point in enumerate(root_points):
                    point_viewed_bikes = getBikes_reformed(point, Book.loop_token(), INSERT_TIMESTAMP=True)

                    print(
                        f'root_points [{i}/{len(root_points)}] {point} [{len(point_viewed_bikes)}] '
                        f'AllDetectedBikeCount: {len(bikeNo_dict)}')
                    self.merge_dedup(bikeNo_dict, point_viewed_bikes)  # merge them add up the detectedCount

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
        :return: a location list contains bike loc whose detectedCount is less than 2
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
    def bike_count_details(bikeNo_dict, infoON=True, statistics_list_len=20) -> list:
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


if __name__ == '__main__':
    pass
TEST_POINT = (120.695064, 27.916269)  # our main teaching building
