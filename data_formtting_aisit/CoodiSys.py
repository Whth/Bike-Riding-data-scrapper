import copy
import datetime
import json
import warnings

import numpy as np
import requests
from matplotlib import pyplot as plt

import req_misc

SOUTHERN_SCH = [120.697855, 27.919326, 120.707664, 27.926667]
BOUND_LOCATION = [120.691208, 27.913032, 120.709791, 27.931309]
NORTHERN_SCH = [120.704529, 27.924249, 120.718147, 27.931749]
D_AREA = [120.706223, 27.91666, 120.708851, 27.919135]
D_PARK = [120.70648, 27.918711, 120.708036, 27.919072]
E_AREA = [120.714814, 27.922776, 120.716799, 27.924619]
A_AREA = [120.700832, 27.925936, 120.703653, 27.927596]
B_AREA = [120.70381, 27.929415, 120.708912, 27.932558]


def getBikes_reformed(point_coordinates: list, token: str, USE_NEW_VERSION=False) -> list:
    """
    功能：获取某一经纬度周边500(?)米的所有单车信息
    1.传入经纬度和token值
    2.如果顺利，返回经纬度周围500米的所有单车信息，否则显示异常信息
    """

    get_bike_data = {"version": "4.2.3", "from": "h5", "systemCode": 63, "platform": 1,
                     "action": "user.ride.nearBikes",
                     "lng": point_coordinates[0], "lat": point_coordinates[1],
                     "currentLng": point_coordinates[0], "currentLat": point_coordinates[1],
                     "cityCode": "0577", "adCode": "330304", "token": token
                     }

    get_bike_data_new = {
        "version": "6.17.0", "from": "h5", "systemCode": 63, "platform": 1,
        "action": "user.ride.nearBikes",
        "lng": point_coordinates[0], "lat": point_coordinates[1],
        "currentLng": point_coordinates[0], "currentLat": point_coordinates[1],
        "adCode": "330304", "cityCode": "0577", "token": token,
        "ticket": "MTY3MjQxMjQ3Mg==.su9UiPSWh6VGUPHMqk8tpmD3wpgVr8eB464cPOT/J9o="
    }
    if USE_NEW_VERSION:
        get_bike_data = get_bike_data_new

    get_bike_url = 'https://api.ttbike.com.cn/api?user.ride.nearBikes'
    bikeData_return = requests.post(get_bike_url, headers=req_misc.a_random_header(), data=json.dumps(get_bike_data),
                                    timeout=5)
    print(f'Server Echoing status:{bikeData_return}')
    Bike_raw_data_dict = json.loads(bikeData_return.text)  # return type is dict

    """

    passCode = 0
    expiredCode = 133
    """

    if Bike_raw_data_dict['data']:
        return Bike_raw_data_dict['data']  # a list

    else:
        # print(bikeData_return.text)
        print(f'## BAD TOKEN ## : {token}')
        return [token]
class FakeDataConstructor(object):

    def __init__(self):
        self.fakeDataList = []



class TangleScrapper(object):

    def __init__(self, loc_list: list = BOUND_LOCATION):
        """
        default constructor op on the whole school area
        :param loc_list:
        """
        self.loc_list = loc_list,

        pass


    def rectangle_slice(self, step=0.0011,
                        disPlayPic: bool = False) -> list:
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
        if step < MIN_INTERVal:
            warnings.warn(f'interval for step is too low')

        node_list = []
        Node = [0, 0]

        latRange = np.arange(self.loc_list[1], self.loc_list[3], step)
        lngRange = np.arange(self.loc_list[0], self.loc_list[2], step)

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

    def tree_slice(self, usingMethod=1):
        """

        :return:
        """

        if usingMethod == 1:
            """
            dict for de duplicate
            """
            bikeNo_dict = {}  # storing the lng and lat and detected times
            data_formatting = []
            points_list = []

            init_points = self.rectangle_slice()

            root_points = []

            for init_point in init_points:
                point_view =
            return points_list


if __name__ == '__main__':
    pass
TEST_POINT = (120.695064, 27.916269)  # our main teaching building
