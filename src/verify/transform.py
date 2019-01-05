# -*- coding: utf-8 -*-
#

'''
转换数据文件的格式，支持 .npz 和 .yml 之间的相互转换

'''

# Python 2/3 compatibility
from __future__ import print_function

import argparse
import logging
import math
import os
import sys

import numpy as np
import cv2

FLANN_INDEX_KDTREE = 1
FLANN_INDEX_LSH    = 6

def load_keypoint_data(filename):
    npzfile = np.load(filename)
    keypoints = [cv2.KeyPoint(x, y, size, angle, response, int(octave), int(class_id))
                 for x, y, size, angle, response, octave, class_id in npzfile['keypoints']]
    return keypoints, npzfile['descriptors']

def save_model_data(filename, keypoints, descriptors, points3d, focals, pose):
    '''写入 npz 格式的数据到 path 指定的文件中。'''
    kpdata =  np.array([(kp.pt[0], kp.pt[1], kp.size, kp.angle, kp.response, kp.octave, kp.class_id)
                        for kp in keypoints])
    np.savez(filename, keypoints=kpdata, descriptors=descriptors, points3d=points3d, focals=focals, pose=pose)
    return filename

def write_yaml(path, focals, pose, keypoints, descriptors, points3d):
    '''写入 yaml 格式的数据 path 指定的文件中。

    在我的Xp上运行只能写入单个的值，写 np.array 的数据直接崩溃，原因暂
    时不明，所以现在暂时不用这种格式，而是直接用 np 的存储格式。

    暂时在 ubuntu 下面跑这个应用，这上面没有问题。
    '''
    fs = cv2.FileStorage(path, cv2.FILE_STORAGE_WRITE)
    fs.open(path, cv2.FILE_STORAGE_WRITE)
    fs.write('focals', focals)
    fs.write('pose', pose)
    fs.write('points2d', np.float64([(kp[0], kp[1]) for kp in keypoints]))
    fs.write('descriptors', descriptors)
    fs.write('points3d', points3d)
    fs.release()

def read_yaml(path):
    '''读取 yaml 格式的数据，返回 keypoints, descriptors, points3d。'''
    fs = cv2.FileStorage(path, cv2.FILE_STORAGE_READ)
    keypoints = fs.getNode('keypoints')
    descriptors = fs.getNode('descriptors')
    points3d = fs.getNode('points3d')
    fs.release()
    return keypoints, descriptors, points3d

def main(params=None):
    parser = argparse.ArgumentParser(description='转换文件格式')
    parser.add_argument('files', metavar='FILE', nargs='+', help='需要转换的文件')
    parser.add_argument('--output', metavar="path", help='输出文件的路径')
    args = parser.parse_args(params)
    
    for filename in args.files:
        if not os.path.exists(filename):
            logging.info('输入文件 %s 不存在', filename)
            continue
        logging.info('装载文件 %s', filename)
        npzfile = np.load(filename)
        dest = os.path.join(args.output, os.path.splitext(os.path.basename(filename))[0] + '.yml')
        logging.info('写入文件 %s', dest)
        write_yaml(dest, npzfile['focals'], npzfile['pose'], npzfile['keypoints'], npzfile['descriptors'], npzfile['points3d'])
    
if __name__ == '__main__':
    logging.basicConfig(format='%(message)s', level=logging.INFO)
    main()
