# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 14:54:23 2019

@author: wuhaoyu
"""

import math
def bdToGaoDe(lon,lat):
    """
    百度坐标转高德坐标
    :param lon:
    :param lat:
    :return:
    """
    PI = 3.14159265358979324 * 3000.0 / 180.0
    x = lon - 0.0065
    y = lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * PI)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * PI)
    lon = z * math.cos(theta)
    lat = z * math.sin(theta)
    return lon,lat