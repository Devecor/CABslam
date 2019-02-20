# -*- coding: utf-8 -*-
#

'''
显示参考图片的关键点和三维坐标信息

命令行参数

  view.py [-p | --print] [-s | --start=i] [-n | --count=1] --image imgfile filename

使用方法

* 打印图片关键点和对应的空间坐标

  view.py -p img-20170519.npz

  打印所有关键点和对应的空间坐标

  view.py -p -s=100 img-20170519.npz

  打印第100个关键点以后的所有关键点和对应的空间坐标


  view.py -p -s=100 -n=20 img-20170519.npz

  打印第100个关键点以后的20个关键点和对应的空间坐标

* 显示包含关键点图形

  view.py --image images/IMG_3509.JPG data/r0/img-20170519.npz

  显示图片中的所有关键点
  鼠标滚轮可以垂直移动图片，按下Ctrl键的同时使用滚轮可以水平移动图片
  鼠标左键点击关键点，会在图片左上角打印出对应的三维空间坐标
'''

# Python 2/3 compatibility
from __future__ import print_function

import argparse
import math

import numpy as np
import cv2

from manager import stereo_rectify, triangulate_points
from calibration.feature import match_images
from calibration.recover import rotation_matrix

kp_stereo_match_threshold = 100

def anorm2(a):
    return (a*a).sum(-1)

def anorm(a):
    return np.sqrt( anorm2(a) )

def draw_str(dst, target, s):
    x, y = target
    # cv2.putText(dst, s, (x+1, y+1), cv2.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 0), thickness = 2, lineType=cv2.LINE_AA)
    # cv2.putText(dst, s, (x, y), cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255), lineType=cv2.LINE_AA)
    cv2.putText(dst, s, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255))

def load_keypoint_data(filename):
    npzfile = np.load(filename)
    keypoints = [cv2.KeyPoint(x, y, size, angle, response, int(octave), int(class_id))
                 for x, y, size, angle, response, octave, class_id in npzfile['keypoints']]
    return keypoints, npzfile['descriptors'], npzfile['points3d']

def explore_keypoint(win, img, kps, points):
    h, w = img.shape[:2]
    w1, h1 = 1200, 600
    maxOffset = max(0, w - w1), max(0, h - h1)
    offset = [0, 0]    
    green = (0, 255, 0)
    red = (0, 0, 255)
    white = (255, 255, 255)
    kp_color = (51, 103, 236)
    vis0 = cv2.drawKeypoints(img, kps, None, flags=0, color=green)
    cv2.imshow(win, vis0)

    pts = []
    for kp in kps:
        pts.append(np.int32(kp.pt))

    delta = 120 << 16;
    speed = 30
    cur_vis = np.zeros((h1, w1), np.uint8)
    def onmouse(event, x, y, flags, offset):
        x0, y0 = offset
        redraw = False
        if event & cv2.EVENT_MOUSEWHEEL:
            dt = -int((flags - (flags & 0xffff)) / delta)            
            if flags & cv2.EVENT_FLAG_CTRLKEY:
                dx = x0 + dt * speed
                x0 = max(0, min(maxOffset[0], dx))
            else:
                dy = y0 + dt * speed
                y0 = max(0, min(maxOffset[1], dy))
            offset[:] = [x0, y0]
            redraw = True
        cur_vis = vis0[y0:, x0:].copy()
        if flags & cv2.EVENT_FLAG_LBUTTON:
            r = 2.6
            m = anorm(np.array(pts) - (x + x0, y + y0)) < r
            idxs = np.where(m)[0]
            tx, ty = 0, 50            
            for i in idxs:                
                draw_str(cur_vis, (tx, ty), '%5d: %s' % (i, points[i].ravel()))
                ty += 50
            redraw = True
        if redraw:
            cv2.imshow(win, cur_vis)
    cv2.setMouseCallback(win, onmouse, offset)

def handle_stereo_images(focal, rotate, offset, filename1, filename2, feature, count):
    imgLeft, imgRight = cv2.imread(filename1, 0), cv2.imread(filename2, 0)
    h, w = imgLeft.shape[:2]
    R = rotation_matrix(rotate, axis='y').A
    T = np.float64(offset)
    distCoeffs = np.zeros(4)
    fx, fy = focal
    cx, cy = (w-1)/2, (h-1)/2
    K = np.float64([[h*fx, 0,    cx],
                    [0,    w*fy, cy],
                    [0,    0,    1]])
    P1, P2, Q = stereo_rectify(K, distCoeffs, K, distCoeffs, (h, w), R, T)

    pts1, pts2, keypoints, descriptors = match_images(imgLeft, imgRight, feature, count)
    if len(keypoints) < kp_stereo_match_threshold:
        raise StarException('双目照片匹配的关键点个数少于 %i' % kp_stereo_match_threshold)

    points3d = triangulate_points(P1, P2, pts1.T, pts2.T)
    return keypoints, points3d

def main(params=None):
    parser = argparse.ArgumentParser(description='查看图片关键点三维坐标')
    parser.add_argument('images', metavar='FILENAME', nargs=2, help='双目图片文件名称')
    parser.add_argument('--show', action='store_true', help='在窗口中显示包含关键点的图片')
    parser.add_argument('--save', action='store_true', help='保存包含关键点的图片')
    parser.add_argument('--output', metavar="path", help='输出文件的路径')
    parser.add_argument('--mask', metavar="x0,y0,x1,y1", help='选择区域（x0, y0, x1, y1)')
    parser.add_argument('--asift', action='store_true', help='使用asift算法')
    parser.add_argument('--tilt', metavar="n", type=int, default=3, help='设置 asift 的 tilt 参数')
    parser.add_argument('--feature', choices=['orb', 'sift', 'surf'], default='orb', help='特征名称')
    parser.add_argument('--nFeatures', metavar='n', type=int, default=2000, help='特征数目')
    parser.add_argument('--offset', metavar="dx,dy,dz", help='两张照片拍摄地点的相对位移（dx,dy,dz)')
    parser.add_argument('--yaw', metavar="n", type=int, default=0, help='两张照片的相对偏转角度（度数）')
    parser.add_argument('--focal', metavar="fx,fy", help='相机内参（fx,fy)')
    args = parser.parse_args(params)

    focal = [float(s) for s in args.focal.split(',')]
    yaw = args.yaw * math.pi / 180
    offset = [float(s) for s in args.offset.split(',')]

    kps, pt3s = handle_stereo_images(focal, yaw, offset, args.images[0], args.images[1], args.feature, args.nFeatures)

    img = cv2.imread(args.images[0], 0)    
    win = 'view3d'
    # cv2.namedWindow(win, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
    cv2.namedWindow(win)
    cv2.moveWindow(win, 0, 0)
    cv2.setWindowTitle(win, 'KeyPoint 3D Viewer')
    explore_keypoint(win, img, kps, pt3s)
    cv2.waitKey()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    # params = ['--offset', '120,0,-120', '--yaw', '25', '--focal', '1.15,0.85',
    #           '../tests/images/world_map_front.jpg', '../tests/images/world_map_right.jpg']
    # main(params)
    import sys, getopt, os
    opts, args = getopt.getopt(
        sys.argv[1:],
        'i:n:ps:',
        ['count=', 'image=', 'print', 'start='])
    opts = dict(opts)

    imgfile = opts.get('--image', opts.get('-i', ''))
    pflag = opts.get('--print', opts.get('-p', None))
    pstart = int(opts.get('--start', opts.get('-s', '0')))
    pcount = opts.get('--count', opts.get('-n', None))
    if pcount is not None:
        pcount = int(pcount)

    try:
        filename = args[0]
    except IndexError:
        print('请指定需要查看的关键点文件名称')
        print(__doc__)
        sys.exit(1)

    if not os.path.exists(filename):
        print('关键点文件 %s 不存在' % filename)
        sys.exit(1)

    img = cv2.imread(imgfile, 0)
    if img is None:
        print('读取文件失败:', imgfile)
        sys.exit(1)

    try:
        kps, descs, points = load_keypoint_data(filename)
    except Exception as e:
        print('非法的关键点文件: %s' % e)
        sys.exit(1)

    if pflag is None:
        win = 'view_keypoint'
        cv2.namedWindow(win)
        cv2.moveWindow(win, 0, 0)
        cv2.setWindowTitle(win, 'KeyPoint Viewer')
        explore_keypoint(win, img, kps, points)
        cv2.waitKey()
        cv2.destroyAllWindows()
    else:
        n = len(kps)
        if pcount is not None:
            n = min(n, pstart + pcount)
        for i in range(pstart, n):
            print ('%5d: %12s --> %s' % (i, np.int32(kps[i].pt), points[i].ravel()))
