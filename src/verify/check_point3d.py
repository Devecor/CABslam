# -*- coding: utf-8 -*-
#

'''
显示参考图片的关键点和三维坐标信息

鼠标滚轮可以垂直移动图片，按下Ctrl键的同时使用滚轮可以水平移动图片
鼠标左键，会在图片左上角打印出对应的三维空间坐标
'''

# Python 2/3 compatibility
from __future__ import print_function

import argparse
import math

import numpy as np
import cv2

import sys
sys.path.append('..')
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

def calculate_points3d(K, R, t, pts1, pts2):
    '''根据针孔相机模型两张图片对应的像素坐标计算对应的空间三维坐标
    >>> t = np.float32([-4, 0, 0])
    >>> K = np.float32([[2380, 0, 1223], \
                        [0, 2380, 1631], \
                        [0, 0, 1]])
    >>> pts1 = np.float32([[1226., 1237.], \
                           [1097., 375.]])
    >>> pts2 = np.float32([[1188.,1234.8], \
                           [1058.40002441, 373.20001221]])
    >>> pt3d = [[   0.31874507,  -41.58947622,  250.5377471 ], \
                [ -13.05410563, -130.24889215,  246.64372768]]
    >>> calculate_points3d(K, None, t, pts1, pts2)
    [array([   0.3214155 ,  -41.45054333,  249.68944372]), array([ -13.02433003, -129.96615533,  246.09709895])]
    '''
    fx, fy = K[0][0], K[1][1]
    cx, cy = K[0][2], K[1][2]
    cp = np.array([K[0][2], K[1][2]])
    dx, dy, dz = t.ravel()

    n = pts1.shape[0]

    b1 = np.zeros(2 * n).reshape(-1, 2)
    b2 = ( pts2 - cp ) * dz - np.array([fx * dx, fy * dy])
    b = np.hstack((b1, b2))

    a0 = np.array([[fx, 0], [0, fy]] * n)
    a1 = np.hstack((a0, (-pts1 + np.array([cx, cy])).reshape(-1, 1))).reshape(-1, 2, 3)
    a2 = np.hstack((a0, (-pts2 + np.array([cx, cy])).reshape(-1, 1))).reshape(-1, 2, 3)
    a = np.stack((a1, a2), axis=1).reshape(-1, 4, 3)
    return [np.linalg.lstsq(a[i], b[i])[0] for i in range(n)]

def handle_stereo_images(config):
    focal = [float(s) for s in config.focal.split(',')]
    rotate = config.yaw * math.pi / 180
    offset = [float(s) for s in config.offset.split(',')]
    filename1, filename2 = config.images
    feature, count = config.feature, config.nFeatures
    asift = config.asift
    homography = config.homography
    imgLeft, imgRight = cv2.imread(filename1, 0), cv2.imread(filename2, 0)
    h, w = imgLeft.shape[:2]
    # R, _jacob = cv2.Rodrigues(rotation_matrix(rotate, axis='y').A)
    R = rotation_matrix(rotate, axis='y').A
    T = np.float64(offset)
    distCoeffs = np.zeros(4)
    fx, fy = focal
    cx, cy = (w-1)/2, (h-1)/2
    K = np.float64([[w*fx, 0,    cx],
                    [0,    h*fy, cy],
                    [0,    0,    1]])

    pts1, pts2, keypoints, descriptors = match_images(imgLeft, imgRight,
                                                      feature + '-flann', asift=asift, n=count,
                                                      homography=homography)
    # if len(keypoints) < kp_stereo_match_threshold:
    #     raise RuntimeError('双目照片匹配的关键点个数 %d 少于 %d' % (len(keypoints), kp_stereo_match_threshold))

    if config.myself:
        points3d = calculate_points3d(K, R, T, pts1, pts2)
    else:
        if config.correct:
            E, mask = cv2.findEssentialMat(pts1, pts2, K)
            retval, R, t, mask = cv2.recoverPose(E, pts1, pts2, K)

            nv = np.matrix(R) * np.float64([0, 0, 1]).reshape(3, 1)
            yaw = np.arctan2(nv[0], nv[2])
            print("自动校正得到的相机水平偏转角度为 %8.2f" % (yaw[0] / math.pi * 180))

            nv = np.matrix(R) * np.float64([0, 1, 0]).reshape(3, 1)
            pitch = np.arctan2(nv[2], nv[1])
            print("自动校正得到的相机仰角为 %8.2f" % (pitch[0] / math.pi * 180))

            nv = np.matrix(R) * np.float64([1, 0, 0]).reshape(3, 1)
            roll = np.arctan2(nv[1], nv[0])
            print("自动校正得到的相机旋转角度为 %8.2f" % (roll[0] / math.pi * 180))

        distCoeffs = np.zeros(4)
        P1, P2, Q = stereo_rectify(K, distCoeffs, K, distCoeffs, (h, w), R, T)
        # print (h, w)
        # print ('R:', R)
        # print ('T:', T)
        # print ('K:', K)
        # print ('P1:', P1)
        # print ('P2:', P2)
        points3d = triangulate_points(P1, P2, pts1.T, pts2.T)
    return keypoints, points3d

def main(params=None):
    parser = argparse.ArgumentParser(description='查看图片关键点三维坐标')
    parser.add_argument('images', metavar='FILENAME', nargs=2, help='双目图片文件名称')
    parser.add_argument('--show', action='store_true', help='在窗口中显示包含关键点的图片')
    parser.add_argument('--save', action='store_true', help='保存包含关键点的图片')
    parser.add_argument('--myself', action='store_true', help='使用自己的算法计算')
    parser.add_argument('--output', metavar="path", help='输出文件的路径')
    parser.add_argument('--mask', metavar="x0,y0,x1,y1", help='选择区域（x0, y0, x1, y1)')
    parser.add_argument('--asift', action='store_true', help='使用asift算法')
    parser.add_argument('--correct', action='store_true', help='是否自动校正角度偏差')
    parser.add_argument('--homography', action='store_true', help='使用 Homography 进行过滤')
    parser.add_argument('--tilt', metavar="n", type=int, default=3, help='设置 asift 的 tilt 参数')
    parser.add_argument('--feature', choices=['orb', 'sift', 'surf'], default='orb', help='特征名称')
    parser.add_argument('--nFeatures', metavar='n', type=int, default=2000, help='特征数目')
    parser.add_argument('--offset', metavar="dx,dy,dz", help='两张照片拍摄地点的相对位移（dx,dy,dz)')
    parser.add_argument('--yaw', metavar="n", type=int, default=0, help='两张照片的相对偏转角度（度数）')
    parser.add_argument('--focal', metavar="fx,fy", help='相机内参（fx,fy)')
    args = parser.parse_args(params)

    kps, pt3s = handle_stereo_images(args)

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
    # 单元测试
    # python -m doctest -v check_point3d.py

    # HUAWEI SLA00 FOCAL: 0.9722,0.7292
    # HUAWEI G80 FOCAL: 1.15,0.85
    # IPHONE 6S  FOCAL: 1.167,0.875
    # params = ['--offset', ' -120,0,0', '--yaw', '0', '--focal', '0.9722,0.7292',
    #           'stereo/map-left.jpg', 'stereo/map-right-120.jpg']
    main()
