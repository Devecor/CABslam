# -*- coding: utf-8 -*-
#

import getopt
import json
import logging
import os
import numpy as np

from config import base_data_path, wifi_data_filename
from manager import get_region_list, find_region_by_position, get_wifi_list

def filter_region(regions, wifiData, n=1):
    '''过滤掉没有 wifi 信号的区域。因为传入进入的各个Wifi都有强度不一的
    信号，如果该区域没有对应的 wifi 信号，那么一定不是可选区域。
    '''
    result = []
    for i in regions:
        try:
            list(wifiData[:, i]).index(0)
        except ValueError:
            result.append(i)
            if not len(result) < n:
                break
    return result

def find_region_by_finger(building, wifiFinger):
    '''根据wifi指纹查找区域编号，最多返回三个可能值。

    building     当前建筑物，字符串。
    wifiFinger   [(BSSID, RSSI),...] 的列表
    '''
    indexes = []
    fingerData = []
    wifiBssids = get_wifi_list(building)
    for bssid, rssi in wifiFinger:
        try:
            index = wifiBssids.index(bssid)
        except ValueError:
            logging.warning('Wifi %s 没有在数据库中', bssid)
        else:
            indexes.append(index)
            fingerData.append(rssi)

    filename = os.path.join(base_data_path, building, wifi_data_filename)
    wifiData = np.load(filename)[np.array(indexes)]
    fingerData = np.array(fingerData).reshape(-1, 1)

    regions = np.argsort(np.linalg.norm(wifiData - fingerData, axis=0))
    return filter_region(regions, wifiData)
