# -*- coding: utf-8 -*-
#

'''
创建参考图片的关键点特征库。

'''

# Python 2/3 compatibility


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

def stereo_rectify(cameraMatrix1, distCoeffs1, cameraMatrix2, distCoeffs2, imageSize, R, T):
    R1, R2, P1, P2, Q, validPixROI1, validPixROI2 = cv2.stereoRectify(
        cameraMatrix1, distCoeffs1, cameraMatrix2, distCoeffs2, imageSize, R, T
        )
    return P1, P2, Q

def triangulate_points(projMatr1, projMatr2, projPoints1, projPoints2):
    points4D = cv2.triangulatePoints(projMatr1, projMatr2, projPoints1, projPoints2)
    return cv2.convertPointsFromHomogeneous(points4D.T);

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
    kp_pairs = list(zip(mkp1, mkp2))
    return mi, p1, p2, list(kp_pairs)

def calibrate_match_points(T, pts1, pts2):
    dx, dy, dz = T.ravel()

    if dz != 0:
        logging.info("警告：存在深度偏移，计算结果可能有误差")
        return

    if dx != 0 and dy != 0:
        logging.info("水平和垂直方向都有偏移，没有进行像素校准")
        return

    if dx == 0:
        logging.info("只有垂直方向偏移，进行水平像素校准")
        # pts2[:, 0] = pts1[:, 0]
        dt = np.mean(pts2 - pts1, axis=0)
        pts2[:, 0] -= dt[0]

    elif dy == 0:
        logging.info("只有水平方向偏移，进行垂直像素校准")
        # pts2[:, 1] = pts1[:, 1]
        dt = np.mean(pts2 - pts1, axis=0)
        pts2[:, 1] -= dt[1]

def calculate_points3d(K, T, pts1, pts2):
    '''根据针孔相机模型和两张图片对应的像素坐标计算对应的空间三维坐标，参考
    系以第一张照片拍摄位置为原点的相机坐标系，即相机正前为 Z, 向下为 Y
    轴，向右为 X 轴

    K 是相机内参，假设两张图片使用相同的相机拍摄

    t 为第二张图片的偏移位置，例如 第二张图片拍摄地点在第一张图片的右侧
    5cm，向前 10cm, 那么 t = (-5, 0, -10)

    pts1, pts2 是两张图片的匹配的像素坐标

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
    >>> calculate_points3d(K, t, pts1, pts2)
    [array([   0.3214155 ,  -41.45054333,  249.68944372]), array([ -13.02433003, -129.96615533,  246.09709895])]

    '''
    fx, fy = K[0][0], K[1][1]
    cx, cy = K[0][2], K[1][2]
    cp = np.array([K[0][2], K[1][2]])
    dx, dy, dz = T.ravel()

    n = pts1.shape[0]

    b1 = np.zeros(2 * n).reshape(-1, 2)
    b2 = ( pts2 - cp ) * dz - np.array([fx * dx, fy * dy])
    b = np.hstack((b1, b2))

    a0 = np.array([[fx, 0], [0, fy]] * n)
    a1 = np.hstack((a0, (-pts1 + np.array([cx, cy])).reshape(-1, 1))).reshape(-1, 2, 3)
    a2 = np.hstack((a0, (-pts2 + np.array([cx, cy])).reshape(-1, 1))).reshape(-1, 2, 3)
    a = np.stack((a1, a2), axis=1).reshape(-1, 4, 3)
    return [np.linalg.lstsq(a[i], b[i])[0] for i in range(n)]

def calculate_points3d_by_y(K, T, pts1, pts2):
    fx, fy = K[0][0], K[1][1]
    cx, cy = K[0][2], K[1][2]
    cp = np.array([K[0][2], K[1][2]])
    dx, dy, dz = T.ravel()

    n = pts1.shape[0]

    b1 = np.zeros(2 * n).reshape(-1, 2)
    b2 = ( pts2 - cp ) * dz - np.array([fx * dx, fy * dy])
    b = np.hstack((b1, b2))

    a0 = np.array([[fx, 0], [0, fy]] * n)
    a1 = np.hstack((a0, (-pts1 + np.array([cx, cy])).reshape(-1, 1))).reshape(-1, 2, 3)
    a2 = np.hstack((a0, (-pts2 + np.array([cx, cy])).reshape(-1, 1))).reshape(-1, 2, 3)
    a = np.stack((a1, a2), axis=1).reshape(-1, 4, 3)
    # 删除第三个等式
    a = np.delete(a, 2, axis=1)
    b = np.delete(b, 2, axis=1)
    return [np.linalg.lstsq(a[i], b[i])[0] for i in range(n)]

def make_models(config, kp1, desc1, kp2, desc2):
    flann_params= dict(algorithm = FLANN_INDEX_LSH,
                       table_number = 6, # 12
                       key_size = 12,     # 20
                       multi_probe_level = 1) #2
    matcher = cv2.FlannBasedMatcher(flann_params, {})  # bug : need to pass empty dict (#1329)

    raw_matches = matcher.knnMatch(desc1, trainDescriptors = desc2, k = 2) #2
    logging.info('KFLANN 匹配数目： %s', len(raw_matches))

    mi, p1, p2, kp_pairs = filter_matches(kp1, kp2, raw_matches)
    logging.info('过滤之后匹配数目： %s', len(kp_pairs))
    # p1 = cv2.KeyPoint_convert(kp_pairs[0])
    # p1 = cv2.KeyPoint_convert(kp_pairs[1])

    H, status = None, None
    if len(p1) >= 4:
        if config.homography:
            H, status = cv2.findHomography(p1, p2, cv2.RANSAC, 3.0)
            logging.info('使用 Homograph 过滤之后匹配数目： %s', np.count_nonzero(status))
        elif config.fundamental:
            H, status = cv2.findFundamentalMat(p1, p2)
            logging.info('使用 Fundamental 过滤之后匹配数目： %s', np.count_nonzero(status))
    if status is None:
        status = np.ones(len(kp_pairs), np.bool_)

    pts1 = np.float64([kpp[0].pt for kpp, flag in zip(kp_pairs, status) if flag])
    pts2 = np.float64([kpp[1].pt for kpp, flag in zip(kp_pairs, status) if flag])

    w, h = [int(x) for x in config.size.split(',')]
    T = np.float64([float(x) for x in config.refpos.split(',')])
    fx, fy = [float(x) for x in config.focals.split(',')]
    cx, cy = (w-1)/2, (h-1)/2

    # change by devecor
    # previous:
    # K = np.float64([[w*fx, 0,    cx],
    #                 [0,    h*fy, cy],
    #                 [0,    0,    1]])
    if config.intrinsicMatrix == None:
        K = np.float64([[w*fx, 0,    cx],
                        [0,    h*fy, cy],
                        [0,    0,    1]])
    else:
        f_x, f_y, c_x, c_y = [float(i) for i in config.intrinsicMatrix.split(',')]
        K = np.float64([[f_x,  0,  c_x],
                        [0,   f_y, c_y],
                        [0,    0,   1]])
    # changes over ----by devecor

    if config.myself:
        # 校正匹配点
        #     如果是水平偏移，那么两张照片匹配点的垂直像素修改为相等
        #     如果是垂直平移，那么两张照片匹配点的水平像素修改为相等
        # calibrate_match_points(T, pts1, pts2)
        pt3s = calculate_points3d(K, T, pts1, pts2)
    else:
        E, mask = cv2.findEssentialMat(pts1, pts2, K)
        retval, R, t, mask = cv2.recoverPose(E, pts1, pts2, K)
        distCoeffs = np.zeros(4)
        P1, P2, Q = stereo_rectify(K, distCoeffs, K, distCoeffs, (h, w), R, T)
        pt3s = triangulate_points(P1, P2, pts1.T, pts2.T).reshape(-1, 3)

    if config.save:
        output = '' if config.output is None else config.output        
        oname = os.path.splitext(os.path.basename(config.image[0]))[0]
        filename = os.path.join(output, oname.rsplit('-', 1)[0])
        # 过滤三维坐标点中 z 值小于 0 的或者特别大的(>config.maximum）
        status3 = np.ones(len(pt3s))
        for i in range(len(pt3s)):
            if pt3s[i][2] < 0:
                status3[i] = 0
            elif pt3s[i][2] > config.maximum:
                status3[i] = 0
        kps = [kpp[0] for kpp, flag in zip(kp_pairs, status) if flag]
        des = [desc1[m.queryIdx] for m, flag in zip(mi, status) if flag]
        kps = [k for k, flag in zip(kps, status3) if flag]
        des = [d for d, flag in zip(des, status3) if flag]
        pts = [p for p, flag in zip(pt3s, status3) if flag]
        n = len(pts)
        logging.info("保存计算得到关键点（ 共 %s 个）的三维坐标到文件： %s", n, filename)
        pose = np.zeros(4) if config.pose is None else np.array([float(x) for x in config.pose.split(',')])
        save_model_data(filename, kps, des, pts, np.array([fx, fy]), pose)
        rname = os.path.splitext(os.path.basename(config.refimage[0]))[0]
        filename = os.path.join(output, "model-%s-%s.txt" % (oname, rname))
        with open(filename, "w") as f:
            f.write("%-16s %-16s %-10s\n" % (oname, rname, n))
        # for i in range(len(pts)):
        #     pt = kps[i].pt
        #     print("%d: (%d, %d) -> (%8.2f %8.2f %8.2f)" %( i, pt[0], pt[1], pts[i][0], pts[i][1], pts[i][2]))

    if config.show:
        logging.info("计算得到的三维坐标信息如下：")
        _u, index = np.unique(pts1, axis=0, return_index=True)
        j = 0
        for i in index:
            if pt3s[i][2] < 0:
                logging.info('%-4d %s, %s: %s', j, np.int32(pts1[i]), np.int32(pts2[i]), "无效结果")
            elif pt3s[i][2] > config.maximum:
                logging.info('%-4d %s, %s: %s(%8.2f)', j, np.int32(pts1[i]), np.int32(pts2[i]), "距离太远", pt3s[i][2])
            else:
                logging.info('%-4d %s, %s: %s', j, np.int32(pts1[i]), np.int32(pts2[i]), pt3s[i])
            j += 1

def main(params=None):
    parser = argparse.ArgumentParser(description='生成图片的三维特征点文件')
    parser.add_argument('image', metavar='IMAGE', nargs=1, help='图片对应的特征文件')
    parser.add_argument('refimage', metavar='REFIMAGE', nargs=1, help='参考图片对应的特征文件')
    parser.add_argument('--pose', help='图片的位置坐标 x,y,z,a')
    parser.add_argument('--refpos', help='参考图片拍摄位置相对偏移量 dx,dy,dz')
    parser.add_argument('--size', required=True, help='图片大小 w,h')
    parser.add_argument('--show', action='store_true', help='打印获取到的关键点三维信息')
    parser.add_argument('--save', action='store_true', help='保存三维关键点数据')
    parser.add_argument('--myself', action='store_true', help='使用自己的算法计算三维坐标')
    parser.add_argument('--output', metavar="path", help='输出文件的路径')
    parser.add_argument('--homography', action='store_true', help='使用 Homography 进行过滤 ')
    parser.add_argument('--fundamental', action='store_true', help='使用 fundamental 过滤匹配结果')
    parser.add_argument('--focals', metavar="fx,fy", help='相机内参（fx,fy)')
    parser.add_argument('--maximum', metavar="D", type=int, default=3000, help='最远的三维关键点距离，单位是厘米')
    # add by devecor
    parser.add_argument('-K', '--intrinsicMatrix', metavar='fx,fy,cx,cy', default=None, help='内参矩阵 若指定了此参数 --focals将失效')
    # add end    ----devecor
    args = parser.parse_args(params)

    for filename in args.image + args.refimage:
        if not os.path.exists(filename):
            logging.info('输入文件 %s 不存在', filename)
            return

    kp1, des1 = load_keypoint_data(args.image[0])
    kp2, des2 = load_keypoint_data(args.refimage[0])
    make_models(args, kp1, des1, kp2, des2)

if __name__ == '__main__':
    # 单元测试
    # python -m doctest -v make_model.py

    logging.basicConfig(format='%(message)s', level=logging.INFO)
    # HUAWEI SLA00 FOCAL: 0.9722,0.7292      size: 2448,3264
    # HUAWEI G80 FOCAL: 1.15,0.85
    # IPHONE 6S  FOCAL: 1.167,0.875          size: 3024,4032
    main()
