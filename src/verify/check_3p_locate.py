# -*- coding: utf-8 -*-
#

import argparse
import json
import logging
import os
import sys

import numpy as np
import cv2

from check_recover_pose import main as recover_pose

def calculate_location(x, y, a1, a2):
    '''计算目标相机位置，假设参考相机和辅助相机拍摄角度一致，传入参数

    以参考相机的拍摄位置为原点，向前为 Y 轴，向右为 X 轴

    x, y 是辅助相机在参考相机坐标系中的位置

    a1 是目标相机在参考相机的方向，以 X 轴为 0，逆时针为正的角度
    a2 是目标相机在辅助相机的方向

    >>> calculate_location(10, 0, np.pi / 6, -np.pi  / 4)
    array([ 6.33974596,  3.66025404])

    >>> calculate_location(10, 0, np.pi / 2, - np.pi / 6)
    array([  3.53525080e-16,   5.77350269e+00])

    >>> calculate_location(10, 0, np.pi / 2, - np.pi / 3)
    array([  1.06057524e-15,   1.73205081e+01])

    '''
    pi = np.pi

    # 计算目标相机和两个参考相机直线的斜率
    # k = np.tan(np.array([np.pi / 2 - r1, np.pi / 2 - (r2 + a)]))
    k = np.tan(np.array([a1, a2]))

    # 解线性方程组
    #     k1 * x - y = k1 * x1 - y1
    #     k2 * x - y = k2 * x2 - y2
    a = np.stack((k, np.array([-1, -1])), axis=1)
    b = k * np.array([0, x]) - np.array([0, y])
    x = np.linalg.solve(a, b)
    return x

def main(params=None):
    parser = argparse.ArgumentParser(description='根据参考照片和辅助照片，定位查询图片的位置')
    parser.add_argument('tImage', metavar='TRAIN', nargs=1, help='参考图片')
    parser.add_argument('rImage', metavar='REF', nargs=1, help='辅助照片')
    parser.add_argument('qImage', metavar='QUERY', nargs=1, help='查询图片')
    parser.add_argument('--train', required=True, help='存放参考图片关键点的文件')
    parser.add_argument('--ref', required=True, help='存放辅助照片关键点的文件')
    parser.add_argument('--query', required=True, help='存放查询图片关键点的文件')
    parser.add_argument('--refpos', required=True, help='辅助照片的位置和角度: x,y')
    parser.add_argument('--focals', required=True, help='相机内参（fx,fy)')
    parser.add_argument('--homography', action='store_true', help='是否使用 homography 过滤匹配结果')
    parser.add_argument('--fundamental', action='store_true', help='是否使用 fundamental 过滤匹配结果')
    parser.add_argument('--show', action='store_true', help='在窗口中显示匹配结果')
    parser.add_argument('--save', action='store_true', help='是否保存匹配和计算结果')
    parser.add_argument('--output', help='输出文件的路径')
    parser.add_argument('--expected', help='期望结果: x,y,a')
    args = parser.parse_args(params)

    argv = ['--focals', args.focals, '--ref', args.train, '--query', args.query]
    if args.homography:
        argv.append('--homography')
    if args.fundamental:
        argv.append('--fundamental')
    argv.extend([args.tImage[0], args.qImage[0]])
    yaw1, t1 = recover_pose(argv)
    a1 = np.arctan2(t1[2], t1[0])[0]

    argv = ['--focals', args.focals, '--ref', args.ref, '--query', args.query]
    if args.homography:
        argv.append('--homography')
    if args.fundamental:
        argv.append('--fundamental')
    argv.extend([args.rImage[0], args.qImage[0]])
    yaw2, t2 = recover_pose(argv)
    a2 = np.arctan2(t2[2], t2[0])[0]

    x, y = [float(_x) for _x in args.refpos.split(',')]
    p = calculate_location(x, y, a1, a2)
    logging.info('相机位置： %s', tuple(p))
    if args.save:
        rp = os.path.splitext(os.path.basename(args.tImage[0]))[0]
        tp = os.path.splitext(os.path.basename(args.qImage[0]))[0]
        output = os.path.join(args.output, 'location-%s.txt' % tp)
        logging.info("定位结果写入到文件: %s", output)
        with open(output, "w") as f:
            # 测试点 参考点 x y a 期望结果
            # 坐标值都是在参考相机坐标系中，a 是相对参考相机的偏移弧度，顺时针为正
            f.write("%s %s %s %s %s %s %s" % (tp, rp, p[0], p[1], yaw1, args.expected))
    return p

if __name__ == '__main__':
    # 单元测试
    # python -m doctest -v check_3p_locate.py

    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    main()
