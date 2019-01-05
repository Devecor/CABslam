# -*- coding: utf-8 -*-
#

import argparse
import json
import logging
import os
import sys

import numpy as np
import cv2

from check_feature import create_detector, explore_features
from check_match import match_features, load_keypoint_data

def dig_feature(config):
    detector = create_detector(config)
    filename = config.files[1]

    train = os.path.join(config.path, os.path.basename(config.files[0]).rsplit('.', 1)[0] + '-asift.orb')
    kp2, des2 = load_keypoint_data(train)

    logging.info('挖掘当前图片: %s', filename)
    img = cv2.imread(filename, 0)
    mask = np.zeros(img.shape, img.dtype)
    # mask = np.array(img.shape, dtype=np.uint8)
    mask.fill(255)
    count = 0
    alpha = 0.76
    baseoutput = config.output
    name = os.path.splitext(os.path.basename(filename))[0]
    delta = cv2.getTickFrequency()
    while True:
        if config.save:            
            config.output = os.path.join(baseoutput, name, str(count))
            if not os.path.exists(config.output):
                os.makedirs(config.output)

        t = cv2.getTickCount()
        kp1, des1 = detector.detectAndCompute(img, mask)
        logging.info('Detect feature: %s', (cv2.getTickCount() - t) / delta )

        t = cv2.getTickCount()
        # mask[np.int32(cv2.KeyPoint_convert(kps))] = 0
        for kp in kp1:
            x, y = [int(n) for n in kp.pt]
            r = int(kp.size / 2 * alpha)
            mask[(y-r):(y+r), (x-r):(x+r)] = 0
        logging.info('Fill mask time: %s', (cv2.getTickCount() - t) / delta )

        explore_features(config, filename, img, kp1, des1)
        if len(kp1) < 300:
            break
        cv2.waitKey(1000)

        t = cv2.getTickCount()
        match_features(config, kp2, des2, kp1, des1)
        logging.info('Match features time: %s', (cv2.getTickCount() - t) / delta )
        
def main():
    parser = argparse.ArgumentParser(description='挖掘图片特征和关键点')
    parser.add_argument('files', metavar='FILENAME', nargs=2, help='图片文件名称')
    parser.add_argument('--show', action='store_true', help='在窗口中显示包含关键点的图片')
    parser.add_argument('--save', action='store_true', help='保存包含关键点的图片')
    parser.add_argument('--output', help='输出文件的路径')
    parser.add_argument('--asift', action='store_true', help='使用asift算法')
    parser.add_argument('--feature', choices=['orb', 'sift', 'surf'], default='orb', help='特征名称')
    parser.add_argument('--nFeatures', metavar='n', type=int, default=800, help='特征数目')
    parser.add_argument('--path', default="features", required=True, help='关键点文件的路径')
    parser.add_argument('--suffix', default='orb', help='关键点文件的后缀名称')
    parser.add_argument('--kdtree', action='store_true', help='使用 FLANN_INDEX_KDTREE 进行匹配')
    parser.add_argument('--pose', help='参考平面和相机距离，水平方位角和相机位置（d,a,x,y,z)')
    parser.add_argument('--camera', help='相机内参（fx,fy)')
    args = parser.parse_args()

    dig_feature(args)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    main()
