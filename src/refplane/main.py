# -*- coding: utf-8 -*-
#
# 平面特征定位实验主程序，用来输出定位结果
# 

import argparse
import json
import logging
import os
import sys
import time
import numpy as np
import cv2

import sys
sys.path.append(os.path.abspath('..'))

FLANN_INDEX_KDTREE = 1
FLANN_INDEX_LSH    = 6

# 度量执行一个功能消耗的时间
def metricmethod(func):
    def wrap(*args, **kwargs):
        t1 = time.clock()
        result = func(*args, **kwargs)
        t2 = time.clock()
        logging.info('%s: %s ms', func.__name__, (t2 - t1) * 1000)
        return result
    return wrap

def load_model_data(filename):
    if filename.endswith('.npz'):
        npzfile = np.load(filename)
    else:
        npzfile = np.load(filename + '.npz')
    keypoints = [cv2.KeyPoint(x, y, size, angle, response, int(octave), int(class_id))
                 for x, y, size, angle, response, octave, class_id in npzfile['keypoints']]
    return keypoints, npzfile['descriptors'], npzfile['points3d']

def load_keypoint_data(filename):
    if filename.endswith('.npz'):
        npzfile = np.load(filename)
    else:
        npzfile = np.load(filename + '.npz')
    keypoints = [cv2.KeyPoint(x, y, size, angle, response, int(octave), int(class_id))
                 for x, y, size, angle, response, octave, class_id in npzfile['keypoints']]
    return keypoints, npzfile['descriptors']

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

def match_features(config, kp1, desc1, kp2, desc2):
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
    
    # if config.query_first:
    #     config.filenames = 'images/tp/t1-9.jpg', 'images/star/s1-5.jpg'
    # else:
    #     config.filenames = 'images/star/s1-5.jpg', 'images/tp/t1-9.jpg'
    # config.show = True
    # explore_match(config, kp_pairs, status, H)

    if status is None:
        status = np.ones(len(kp_pairs), np.bool_)

    return mi, status

def query_image(config, refimage, kps, descs):
    keypoints, descriptors, points3d = load_model_data(refimage)
    if len(keypoints) == 0:
        logging.info("参考照片缺少三维关键点数据")
        return
    query_first = True
    config.query_first = query_first
    # query_first 测试照片为query，参考照片为train
    if query_first:
        matchresults = match_features(config, kps, descs, keypoints, descriptors)
    else:
        matchresults = match_features(config, keypoints, descriptors, kps, descs)
    if matchresults is None:
        return

    mi, status = matchresults
    n = np.count_nonzero(status)
    if n < config.reject:
        return

    if query_first:
        imagePoints = np.float64([kps[m.queryIdx].pt for m, flag in zip(mi, status) if flag])
        objPoints = np.float64([points3d[m.trainIdx] for m, flag in zip(mi, status) if flag])
        refPoints = np.float64([keypoints[m.trainIdx].pt for m, flag in zip(mi, status) if flag])
    else:
        imagePoints = np.float64([kps[m.trainIdx].pt for m, flag in zip(mi, status) if flag])
        objPoints = np.float64([points3d[m.queryIdx] for m, flag in zip(mi, status) if flag])
        refPoints = np.float64([keypoints[m.queryIdx] for m, flag in zip(mi, status) if flag])

    # for i in range(len(imagePoints)):
    #     print("%d: (%d, %d) -> (%8.2f %8.2f %8.2f)" % (i, imagePoints[i][0], imagePoints[i][1], objPoints[i][0], objPoints[i][1], objPoints[i][2]))

    fx, fy = [float(x) for x in config.focals.split(',')]
    w, h = [float(x) for x in config.size.split(',')]
    K = np.float64([[fx*w, 0, 0.5*(w-1)],
                    [0, fy*h, 0.5*(h-1)],
                    [0.0,0.0,      1.0]])
    dist_coef = np.zeros(4)
    flags = cv2.SOLVEPNP_P3P if config.solve == 'P3P' else \
            cv2.SOLVEPNP_AP3P if config.solve == 'AP3P' else \
            cv2.SOLVEPNP_EPNP if config.solve == 'EPNP' else \
            cv2.SOLVEPNP_ITERATIVE
    # ret, rvec, tvec = cv2.solvePnP(objPoints, imagePoints, K, dist_coef, flags=flags)
    ret, rvec, tvec, inliers = cv2.solvePnPRansac(objPoints, imagePoints, K, dist_coef, flags=flags)
    rmat = np.matrix(cv2.Rodrigues(rvec)[0])
    nv = rmat * np.float64([0, 0, 1]).reshape(3, 1)
    yaw = np.arctan2(nv[0], nv[2])
    return n, yaw, -tvec.ravel(), imagePoints, objPoints, refPoints

def main(params=None):
    parser = argparse.ArgumentParser(description='根据平面特征参考图片，定位查询图片的位置和朝向')
    parser.add_argument('refplane', metavar='PLANE', nargs=1, help='平面特征参考图片')
    parser.add_argument('images', metavar='IMAGE', nargs='+', help='多张测试图片')
    parser.add_argument('--homography', action='store_true', help='是否使用 homography 过滤匹配结果')
    parser.add_argument('--fundamental', action='store_true', help='是否使用 fundamental 过滤匹配结果')
    parser.add_argument('--reject', type=int, default=16, help='匹配失败阀值，小于该值认为是失败')
    parser.add_argument('--accept', type=int, default=100, help='匹配成功阀值，大于该值认为匹配成功')
    parser.add_argument('--output', default="output", help='输出文件的路径')
    parser.add_argument('--focals', default="0.9722,0.7292", help='相机内参（fx,fy)')
    parser.add_argument('--solve', default="P3P", choices=('ITERATIVE', 'P3P', 'AP3P', 'EPNP'), help='选择定位算法，默认是 P3P')
    parser.add_argument('--debug', action='store_true', help='输出定位结果json文件')
    parser.add_argument('--mask', metavar="x0,y0,x1,y1", help='选择平面所在的区域（x0, y0, x1, y1)')
    parser.add_argument('--nFeatures', metavar='n', type=int, default=2000, help='参考照片的特征数目')
    parser.add_argument('--tFeatures', metavar='tn', type=int, default=2000, help='测试照片的特征数目')
    parser.add_argument('--asift', choices=(1, 2, 3, 4, 5), type=int, help='使用asift算法的tilt值')
    parser.add_argument('--save', action='store_true', help='是否保存定位结果')
    args = parser.parse_args(params)

    refimg = args.refplane[0]
    for img in args.images:
        logging.info("查询图片: %s", args.images[0])

        kp1, des1 = load_keypoint_data(args.qryimage[0])
        total, yaw, pos = 0, None, None
        index = None
        refImg = None
    imagePoints, points3d, refPoints = [], [], []
    for i in range(len(args.refimages)):
        logging.info('使用第 %s 张照片进行匹配', i + 1)
        pose = query_image(args, args.refimages[i], kp1, des1)
        if pose is not None:
            logging.info('第 %s 张照片匹配成功', i + 1)
            if pose[0] > total:
                total, yaw, pos, imagePoints, points3d, refPoints = pose
                index = i
                refImg = os.path.basename(args.refimages[i])
                # 大于 100 个直接使用该定位结果
                if total > args.accept:
                    break
    t2 = time.clock()
    t = (t2 - t1) * 1000
    name = os.path.basename(args.qryimage[0]).rsplit('-', 1)[0]
    filename = os.path.join(args.output, name + '-pose.txt')
    if pos is None:
        logging.info('%s 定位失败，耗时： %s', name, t)
        if args.save:
            logging.info("定位结果写入文件: %s", filename)
            with open(filename, "w") as f:
                f.write('%-8s %-8.2f %-8s\n' % (name, t, 'NaN'))
        return

    a = yaw.A.ravel()[0] * 180 / np.pi
    # 这是相对参考相机拍摄角度的偏转，顺时针为正值
    refname = os.path.splitext(os.path.basename(args.refimages[index]))[0]
    logging.info("使用参考照片 %s 的定位结果，消耗时间: %s 毫秒，匹配关键点: %d", refname, t, total)
    logging.info("相对参考相机的拍摄角度： %s", a)
    logging.info("相对参考相机的偏移： %s", pos.ravel())
    if args.debug:
        if args.debug:
            sw, sh = args.size.rsplit(',')
            points3d = points3d + pos
            image = {'url': name, 'size': [int(sw), int(sh)], 'points': imagePoints.tolist()}
            refimage = {"url": refImg, "size": [int(sw), int(sh)], 'points': refPoints.tolist()}
            if os.path.exists('./debug') == False:
                os.makedirs('./debug')
            with open ('./debug/' + name + '-' + refImg + '.json', 'w') as f:
                json.dump({"image": image, "points3d": points3d.tolist(), "refimage": refimage}, f, indent = 2)
    if args.save:
        logging.info("定位结果写入文件: %s", filename)
        with open(filename, "w") as f:
            f.write('%-8s %-8.2f %-6s %-6.2f %8.2f %8.2f %4d\n' % (name, t, refname, a, pos[0], pos[2], total))

    return yaw, pos

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    main()
