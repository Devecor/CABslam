# -*- coding: utf-8 -*-
#

import argparse
import json
import logging
import os
import sys

import numpy as np
import cv2

from check_match import explore_match, load_keypoint_data

FLANN_INDEX_KDTREE = 1
FLANN_INDEX_LSH    = 6

def camera_matrix(config):
    img = cv2.imread(config.filenames[1], 0)
    h, w = img.shape[:2]
    if config.focals:
        fx, fy = [float(s) for s in config.focals.split(',')]
    else:
        fx, fy = 0, 0
    return np.float64([[fx*w, 0, 0.5*(w-1)],
                       [0, fy*h, 0.5*(h-1)],
                       [0.0,0.0,      1.0]])

def filter_matches(kp1, kp2, matches, ratio = 0.75):
    mkp1, mkp2 = [], []
    mi = []
    for m in matches:
        if len(m) == 2 and m[0].distance < m[1].distance * ratio:
            m = m[0]
            mkp1.append( kp1[m.queryIdx] )
            mkp2.append( kp2[m.trainIdx] )
            mi.append(m)
    p1 = np.float32([kp.pt for kp in mkp1])
    p2 = np.float32([kp.pt for kp in mkp2])
    kp_pairs = zip(mkp1, mkp2)
    return mi, p1, p2, list(kp_pairs)

def recover_pose(config, kp1, desc1, kp2, desc2):
    flann_params= dict(algorithm = FLANN_INDEX_LSH,
                       table_number = 6, # 12
                       key_size = 12,     # 20
                       multi_probe_level = 1) #2
    matcher = cv2.FlannBasedMatcher(flann_params, {})  # bug : need to pass empty dict (#1329)

    raw_matches = matcher.knnMatch(desc1, trainDescriptors = desc2, k = 2) #2
    logging.info('原始匹配数目： %s', len(raw_matches))

    mi, p1, p2, kp_pairs = filter_matches(kp1, kp2, raw_matches)
    # p1 = cv2.KeyPoint_convert(kp_pairs[0])
    # p1 = cv2.KeyPoint_convert(kp_pairs[1])

    if len(p1) < 4:
        logging.info('过滤之后匹配数目（ %s ）小于4个，无法定位', len(p1))
        return

    logging.info('过滤之后匹配数目： %s', len(kp_pairs))

    # H, status = cv2.findHomography(p1, p2, cv2.RANSAC, 5.0)
    # F, status = cv2.findFundamentalMat(p1, p2)
    # H, status = cv2.findHomography(p1, p2, 0)
    H, status = None, None
    if config.homography:
        logging.info("使用 finHomography 过滤匹配结果")
        H, status = cv2.findHomography(p1, p2, cv2.RANSAC, 3.0)
    elif config.fundamental:
        logging.info("使用 findFundamentalMat 过滤匹配结果")
        H, status = cv2.findFundamentalMat(p1, p2)

    if config.show:
        explore_match(config, kp_pairs, status, H)

    if status is None:
        status = np.ones(len(kp_pairs), np.bool_)
    
    pts1 = np.float64([kpp[0].pt for kpp, flag in zip(kp_pairs, status) if flag])
    pts2 = np.float64([kpp[1].pt for kpp, flag in zip(kp_pairs, status) if flag])

    n = len(np.unique(pts2, axis=0))
    if n < 9:
        logging.info('最终匹配数目（ %s ）小于9个，无法定位', n)
        return
        
    K = camera_matrix(config)
    E, mask = cv2.findEssentialMat(pts1, pts2, K)
    retval, R, t, mask = cv2.recoverPose(E, pts1, pts2, K)

    nv = np.matrix(R) * np.float64([0, 0, 1]).reshape(3, 1)
    yaw = np.arctan2(nv[0], nv[2])
    return yaw, t

def main(params=None):
    parser = argparse.ArgumentParser(description='根据参考图片，定位查询图片的角度（recoverPose)')
    parser.add_argument('filenames', metavar='FILENAME', nargs=2, help='参考图片，查询图片')
    parser.add_argument('--ref', required=True, help='存放参考图片关键点的文件')
    parser.add_argument('--query', required=True, help='存放查询图片关键点的文件')
    parser.add_argument('--homography', action='store_true', help='是否使用 homography 过滤匹配结果')
    parser.add_argument('--fundamental', action='store_true', help='是否使用 fundamental 过滤匹配结果')
    parser.add_argument('--essential', action='store_true', help='是否使用 essential 过滤匹配结果')
    parser.add_argument('--show', action='store_true', help='在窗口中显示匹配结果')
    parser.add_argument('--save', action='store_true', help='是否保存匹配和计算结果')
    parser.add_argument('--output', help='输出文件的路径')
    parser.add_argument('--focals', help='相机内参（fx,fy)')
    args = parser.parse_args(params)

    logging.info("参考图片: %s", args.filenames[0])
    logging.info("查询图片: %s", args.filenames[1])

    for filename in args.ref, args.query:
        if not os.path.exists(filename):
            logging.warning('关键点数据还没有生成，请首先使用 check_feature 生成关键点文件: %s', filename)
            return

    kp1, des1 = load_keypoint_data(args.query)
    kp2, des2 = load_keypoint_data(args.ref)
    yaw, t = recover_pose(args, kp1, des1, kp2, des2)
    # 这是相对参考相机拍摄角度的偏转，顺时针为正值
    logging.info("相对参考相机的拍摄角度： %s", yaw * 180 / np.pi)
    logging.info("偏移方向： %s", t.ravel())
    logging.info("相对参考相机 X 轴偏移角度： %s", np.arctan2(t[2], t[0]) * 180 / np.pi)
    return yaw.A.ravel()[0], t

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    main()
