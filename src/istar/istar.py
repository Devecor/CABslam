# -*- coding: utf-8 -*-
#

import argparse
import json
import logging
import os
import sys

import numpy as np
import cv2

from config import vigor_index, base_data_path, StarException
from wifi.finger import find_region_by_finger
from calibration.recover import query_image
from manager import get_region_images, load_keypoint_data, load_vigor_index

def load_refplane(filename):
    npzfile = np.load(filename if filename.endswith('.npz') else (filename + '.npz'))
    # TODO: XXXX 可能影响性能，因为关键点很多，数量级在万以上
    keypoints = [cv.KeyPoint(x, y, size, angle, response, int(octave), int(class_id))
                 for x, y, size, angle, response, octave, class_id in npzfile['keypoints']]
    return dict(camera=npzfile['camera'],
                pose=npzfile['pose'],
                keypoints=keypoints,
                descriptors=npzfile['descriptors'],
            )

def locate_image_in_region(config, image):
    '''在区域内使用照片精准定位

    region    备选区域列表

    image     图片信息数据

    focal     当前相机的内参 fx, fy

    location  参考位置，根据其他方法得到的参考位置，当wifi指纹无法定位的
              时候可以作为参考位置来确定区域

    返回相机的位置和水平方位角，以正北方向为0度，偏东方向为正，范围为
    (-pi/2, pi/2)。

    建筑物坐标系以正东为 X 轴，正北为 Y 轴，向上为 Z 轴。
    '''
    building = config.building
    region = config.region
    focal = float(config.focal)

    # 相机内部参数
    h, w = image.shape[:2]
    fx, fy = [ focal / float(x) for x in config.size.split(',') ]
    cx, cy = (w - 1) / 2, (h - 1) / 2
    k = np.float64([[fx*w,  0, cx],
                         [0,  fy*h, cy],
                         [0,     0, 1]])

    pose = None
    regionImages = get_region_images(building, region)
    refplanes = []
    for refimage in regionImages:
        logging.info('Use refimage: %s', refimage)
        refplane = load_refplane(refimage)
        pose = query_image(config, refplane, image, k)
        logging.info('Query result: %s', pose)
        refplanes.append(refplane)
        if pose:
            break

    if pose is None and not config.mode == 'dig':
        logging.info('Try dig mode to query pose')
        config.mode = 'dig'
        for refplane in refplanes:
            pose = query_image(config, refplane, image, k)
            logging.info('Query result: %s', pose)
            if pose:
                break

    return pose

def istar_find_region(building, wifi, location=None):
    '''根据wifi指纹定位区域

    building  当前所在的建筑物，例如物信楼，校园

    finger    wifi 指纹列表，[ (BSSID, RSSI), ...]

    '''

    if not os.path.exists(wifi):
        logging.error('Wifi指纹数据 %s 不存在', wifi)
        return

    with open(wifi, 'r') as f:
        finger = json.load(f)

    # 根据Wifi指纹定位区域
    return find_region_by_finger(building, finger)

def init_vigor_index(building):
    vigor_index = load_vigor_index(building)

def main():
    parser = argparse.ArgumentParser(description='iStar定位照片的命令行工具')
    parser.add_argument('images', metavar='FILENAME', nargs='+', help='图片文件名称')
    parser.add_argument('--building', default='north-west-university/building-1', help='拍摄照片所在的建筑物')
    parser.add_argument('--region', help='拍摄照片所在的区域')
    parser.add_argument('--focal', default='3.5', help='焦距（mm）')
    parser.add_argument('--size', default='3.6,4.8', help='底片大小（w,h）')

    parser.add_argument('--base-path', help='建筑物参考数据存储路径')

    parser.add_argument('--mode', default='normal', help='定位模式，支持正常定位和充分定位两种')
    parser.add_argument('--show', action='store_true', help='在窗口中显示包含关键点的图片')
    parser.add_argument('--save', action='store_true', help='保存定位结果')
    args = parser.parse_args()

    for image in args.images:
        if not os.path.exists(image):
            logging.error('图像文件 %s 不存在', image)
            return

    # init_vigor_index(args.building)

    if args.region is None:
        # wifi locate first
        region = 'floor_1/r0'

    try:
        results = []
        for filename in args.images:
            image = cv2.imread(filename, 0)
            pose = locate_image_in_region(args, image)
            if pose is None:
                results.append('%s' % os.path.basename(filename))
                logging.error('定位失败')
            else:
                value = ' %s %s %s' % (pose[0], pose[1][0],pose[1][2])
                logging.info('定位结果： %s', value)
                results.append(os.path.basename(filename) + value)
        if args.save:
            with open('result.txt', 'w') as f:
                f.write('\n'.join(results))
    except StarException as e:
        logging.error(e)

if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s %(message)s',
        level=logging.INFO,
    )
    main()
