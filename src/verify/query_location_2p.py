# -*- coding: utf-8 -*-
#

import argparse
import json
import logging
import os
import sys

import numpy as np
import cv2

from check_3p_locate import calculate_location
from check_recover_pose import main as recover_pose

def query_location(config):
    query = os.path.join(config.query, os.path.basename(config.qImage[0]).rsplit('.', 1)[0] + '-orb.npz')
    x, y = [float(_x) for _x in config.refpos.split(',')]

    for i in range(len(config.tImage)):
        train = os.path.join(config.train, os.path.basename(config.tImage[i]).rsplit('.', 1)[0] + '-orb.npz')
        argv = ['--focals', config.focals, '--ref', train, '--query', query]
        if config.homography:
            argv.append('--homography')
        if config.fundamental:
            argv.append('--fundamental')
        argv.extend([config.tImage[i], config.qImage[0]])
        try:
            yaw1, t1 = recover_pose(argv)
        except Exception:
            continue
        a1 = np.arctan2(t1[2], t1[0])[0]

        train = os.path.join(config.train, os.path.basename(config.tImage[i]).rsplit('.', 1)[0] + 'a-orb.npz')
        argv = ['--focals', config.focals, '--ref', train, '--query', query]
        if config.homography:
            argv.append('--homography')
        if config.fundamental:
            argv.append('--fundamental')
        argv.extend([config.tImage[i], config.qImage[0]])
        try:
            yaw2, t2 = recover_pose(argv)
        except Exception:
            continue
        a2 = np.arctan2(t2[2], t2[0])[0]

        p = calculate_location(x, y, a1, a2)
        return i+1, tuple(p)

def main(params=None):
    parser = argparse.ArgumentParser(description='根据参考照片和辅助照片，定位查询图片的位置')
    parser.add_argument('qImage', metavar='QUERY', nargs=1, help='查询图片名称')
    parser.add_argument('tImage', metavar='TRAIN', nargs='+', help='多个参考图片名称')
    parser.add_argument('--train', required=True, help='存放参考图片关键点的路径')
    parser.add_argument('--query', required=True, help='存放查询图片关键点的路径')
    parser.add_argument('--refpos', required=True, help='辅助照片的位移: x,y')
    parser.add_argument('--focals', required=True, help='相机内参（fx,fy)')
    parser.add_argument('--homography', action='store_true', help='是否使用 homography 过滤匹配结果')
    parser.add_argument('--fundamental', action='store_true', help='是否使用 fundamental 过滤匹配结果')
    parser.add_argument('--show', action='store_true', help='在窗口中显示匹配结果')
    parser.add_argument('--save', action='store_true', help='是否保存匹配和计算结果')
    parser.add_argument('--output', help='输出文件的路径')
    parser.add_argument('--size', default="2448,3264", help='查询照片大小（w,h)')
    args = parser.parse_args(params)

    result = query_location(args)
    if result is None:
        logging.info('定位失败')
    else:
        i, p = result
        logging.info('使用第 %d 张照片定位成功，相机位置： %s', i, tuple(p))

    if args.save:
        tp = os.path.basename(args.qImage[0]).rsplit('.', 1)[0]        
        output = args.output
        logging.info("定位结果写入到文件: %s", output)
        with open(output, "a") as f:
            # 测试点 参考点 n x y
            if result is None:
                f.write("%s NaN\n" % tp)
            else:
                rp = os.path.basename(args.tImage[i-1]).rsplit('.', 1)[0]
                f.write("%-8s %-8s %8.2f %8.2f\n" % (tp, rp, p[0], p[1]))

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    main()
