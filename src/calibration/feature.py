# -*- coding: utf-8 -*-
#

# Python 2/3 compatibility
from __future__ import print_function

import logging

import numpy as np
import cv2

import itertools as it
from multiprocessing.pool import ThreadPool

from config import StarException, kp_feature_count, kp_query_match_threshold

FLANN_INDEX_KDTREE = 1  # bug: flann enums are missing
FLANN_INDEX_LSH    = 6

def anorm2(a):
    return (a*a).sum(-1)

def anorm(a):
    return np.sqrt( anorm2(a) )

def get_size(img):
    h, w = img.shape[:2]
    return w, h

def init_feature(name, n=None):
    chunks = name.split('-')
    if chunks[0] == 'sift':
        detector = cv2.xfeatures2d.SIFT_create()
        norm = cv2.NORM_L2
    elif chunks[0] == 'surf':
        detector = cv2.xfeatures2d.SURF_create(800 if n is None else n)
        norm = cv2.NORM_L2
    elif chunks[0] == 'orb':
        detector = cv2.ORB_create(800 if n is None else n)
        norm = cv2.NORM_HAMMING
    elif chunks[0] == 'akaze':
        detector = cv2.AKAZE_create()
        norm = cv2.NORM_HAMMING
    elif chunks[0] == 'brisk':
        detector = cv2.BRISK_create()
        norm = cv2.NORM_HAMMING
    else:
        return None, None
    if 'flann' in chunks:
        if norm == cv2.NORM_L2:
            flann_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
        else:
            flann_params= dict(algorithm = FLANN_INDEX_LSH,
                               table_number = 6, # 12
                               key_size = 12,     # 20
                               multi_probe_level = 1) #2
        matcher = cv2.FlannBasedMatcher(flann_params, {})  # bug : need to pass empty dict (#1329)
    else:
        matcher = cv2.BFMatcher(norm)
    return detector, matcher

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

def match_images(img1, img2, feature_name, asift=False, n=None, homography=False):
    detector, matcher = init_feature(feature_name, n=n)
    if detector is None:
        raise Exception('未知的特征匹配算法 %s' % feature_name)

    kp1, desc1 = asift_detect_compute(detector, img1, None) if asift \
        else detector.detectAndCompute(img1, None)
    kp2, desc2 = asift_detect_compute(detector, img2, None) if asift \
        else detector.detectAndCompute(img2, None)

    raw_matches = matcher.knnMatch(desc1, trainDescriptors = desc2, k = 2) #2
    mi, p1, p2, kp_pairs = filter_matches(kp1, kp2, raw_matches)

    if not homography:
        # keypoints = [kpp[0] for kpp in kp_pairs]
        # descriptors = [desc1[m.queryIdx] for m in mi]
        # return p1, p2, keypoints, descriptors
        H, status = cv2.findFundamentalMat(p1, p2)
    else:
        H, status = cv2.findHomography(p1, p2, cv2.RANSAC, 5.0)
    # F, status = cv2.findFundamentalMat(p1, p2)
    # H, status = cv2.findHomography(p1, p2, 0)
    keypoints = [kpp[0] for kpp, flag in zip(kp_pairs, status) if flag]
    descriptors = [desc1[m.queryIdx] for m, flag in zip(mi, status) if flag]
    
    pt1 = np.float64([p for p, flag in zip(p1, status) if flag])
    pt2 = np.float64([p for p, flag in zip(p2, status) if flag])
    return pt1, pt2, keypoints, descriptors

def _match_features(matcher, kp1, desc1, kp2, desc2):
    if desc1 is None or desc2 is None:
        return None, None, None
    raw_matches = matcher.knnMatch(desc1, trainDescriptors = desc2, k = 2) #2
    # Filter raw matches
    ratio = 0.75
    mkp1, mkp2 = [], []
    for m in raw_matches:
        if len(m) == 2 and m[0].distance < m[1].distance * ratio:
            m = m[0]
            mkp1.append( kp1[m.queryIdx] )
            mkp2.append( kp2[m.trainIdx] )
    p1 = np.float64([kp.pt for kp in mkp1])
    p2 = np.float64([kp.pt for kp in mkp2])

    if len(p1[:4]) < 4:
        return None, None, None
    H, status = cv2.findHomography(p1, p2, cv2.RANSAC, 5.0)
    # do not draw outliers (there will be a lot of them)
    pts1 = np.float64([kpp for kpp, flag in zip(p1, status) if flag])
    pts2 = np.float64([kpp for kpp, flag in zip(p2, status) if flag])
    if len(pts2[:1]) == 0:
        return None, None, None
    return status, pts1, pts2

def simple_match_features(config, detector, matcher, kp1, desc1, image):
    kp2, desc2 = detector.detectAndCompute(image, None)
    return _match_features(matcher, kp1, desc1, kp2, desc2)

def dig_match_features(config, detector, matcher, kp1, desc1, image):
    mask = np.zeros(image.shape, image.dtype)
    # mask = np.array(img.shape, dtype=np.uint8)
    mask.fill(255)

    count = 1
    alpha = 0.382
    kp_threshold = kp_feature_count * 0.618
    max_dig_count = 3
    match_threshold = kp_query_match_threshold

    logging.info('使用挖掘算法匹配参考照片...')
    while True:
        kp2, desc2 = detector.detectAndCompute(image, mask)
        status, pt1, pt2 = _match_features(matcher, kp1, desc1, kp2, desc2)
        if status is None:
            logging.info('%d: 匹配参考照片的特征点数目: %s', count, 0)
        else:
            n = len(np.unique(pt2, axis=0))
            logging.info('%d: 匹配参考照片的特征点数目: %s', count, n)
            if n > match_threshold:
                logging.info('挖掘算法匹配成功')
                return pt1, pt2            
        if (count > max_dig_count or len(kp2) < kp_threshold):
            logging.info('挖掘算法匹配失败')
            break
        count += 1
        for kp in kp2:
            x, y = [int(i) for i in kp.pt]
            r = int(kp.size * alpha)
            mask[(y-r):(y+r), (x-r):(x+r)] = 0

def match_features(config, kp1, desc1, image):
    detector, matcher = init_feature('orb-flann', kp_feature_count)
    if detector is None:
        raise StarException('未知的特征匹配算法 %s' % feature_name)
    if config.mode == 'dig':
        return dig_match_features(config, detector, matcher, kp1, desc1, image)

    status, pt1, pt2 = simple_match_features(config, detector, matcher, kp1, desc1, image)
    n = 0 if status is None else len(np.unique(pt2, axis=0))
    if n < kp_query_match_threshold:
        logging.info('匹配参考照片特征点点数目 %s 少于阀值 %s', n, kp_query_match_threshold)
        # return dig_match_features(config, detector, matcher, kp1, desc1, image)
    else:
        logging.info('匹配参考照片的特征点数目: %s', n)
        return pt1, pt2

def affine_skew(tilt, phi, img, mask=None):
    '''
    affine_skew(tilt, phi, img, mask=None) -> skew_img, skew_mask, Ai

    Ai - is an affine transform matrix from skew_img to img
    '''
    h, w = img.shape[:2]
    if mask is None:
        mask = np.zeros((h, w), np.uint8)
        mask[:] = 255
    A = np.float32([[1, 0, 0], [0, 1, 0]])
    if phi != 0.0:
        phi = np.deg2rad(phi)
        s, c = np.sin(phi), np.cos(phi)
        A = np.float32([[c,-s], [ s, c]])
        corners = [[0, 0], [w, 0], [w, h], [0, h]]
        tcorners = np.int32( np.dot(corners, A.T) )
        x, y, w, h = cv2.boundingRect(tcorners.reshape(1,-1,2))
        A = np.hstack([A, [[-x], [-y]]])
        img = cv2.warpAffine(img, A, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    if tilt != 1.0:
        s = 0.8*np.sqrt(tilt*tilt-1)
        img = cv2.GaussianBlur(img, (0, 0), sigmaX=s, sigmaY=0.01)
        img = cv2.resize(img, (0, 0), fx=1.0/tilt, fy=1.0, interpolation=cv2.INTER_NEAREST)
        A[0] /= tilt
    if phi != 0.0 or tilt != 1.0:
        h, w = img.shape[:2]
        mask = cv2.warpAffine(mask, A, (w, h), flags=cv2.INTER_NEAREST)
    Ai = cv2.invertAffineTransform(A)
    return img, mask, Ai


def affine_detect(detector, img, mask=None, pool=None):
    '''
    affine_detect(detector, img, mask=None, pool=None) -> keypoints, descrs

    Apply a set of affine transormations to the image, detect keypoints and
    reproject them into initial image coordinates.
    See http://www.ipol.im/pub/algo/my_affine_sift/ for the details.

    ThreadPool object may be passed to speedup the computation.
    '''
    tilt = 3
    params = [(1.0, 0.0)]
    for t in 2**(0.5*np.arange(1, tilt)):
        for phi in np.arange(0, 180, 72.0 / t):
            params.append((t, phi))

    def f(p):
        t, phi = p
        timg, tmask, Ai = affine_skew(t, phi, img, mask)
        keypoints, descrs = detector.detectAndCompute(timg, tmask)
        for kp in keypoints:
            x, y = kp.pt
            kp.pt = tuple( np.dot(Ai, (x, y, 1)) )
        if descrs is None:
            descrs = []
        return keypoints, descrs

    keypoints, descrs = [], []
    if pool is None:
        ires = it.imap(f, params)
    else:
        ires = pool.imap(f, params)

    for i, (k, d) in enumerate(ires):
        # logging.debug('affine sampling: %d / %d' % (i+1, len(params)))
        keypoints.extend(k)
        descrs.extend(d)

    return keypoints, np.array(descrs)

def asift_detect_compute(detector, img, mask=None):
    pool=ThreadPool(processes = cv2.getNumberOfCPUs())
    return affine_detect(detector, img, mask=mask, pool=pool)

def find_homography(fn1, fn2):
    feature_name = 'orb-flann'

    img1 = cv2.imread(fn1, 0)
    img2 = cv2.imread(fn2, 0)
    detector, matcher = init_feature(feature_name)

    if img1 is None:
        print('Failed to load fn1:', fn1)
        return

    if img2 is None:
        print('Failed to load fn2:', fn2)
        return

    if detector is None:
        print('unknown feature:', feature_name)
        return

    print('using', feature_name)

    kp1, desc1 = detector.detectAndCompute(img1, None)
    kp2, desc2 = detector.detectAndCompute(img2, None)
    print('img1 - %d features, img2 - %d features' % (len(kp1), len(kp2)))

    print('matching...')
    raw_matches = matcher.knnMatch(desc1, trainDescriptors = desc2, k = 2) #2
    mi, p1, p2, kp_pairs = filter_matches(kp1, kp2, raw_matches)

    if len(p1) >= 4:
        H, status = cv2.findHomography(p1, p2, cv2.RANSAC, 5.0)
        print('%d / %d  inliers/matched' % (np.sum(status), len(status)))

        # do not draw outliers (there will be a lot of them)
        kp_pairs = [kpp for kpp, flag in zip(kp_pairs, status) if flag]

    else:
        H, status, kp_pairs = None, None, None
        print('%d matches found, not enough for homography estimation' % len(p1))

    return H, kp_pairs


if __name__ == '__main__':
    import sys, getopt
    opts, args = getopt.getopt(sys.argv[1:], '', [''])
    try:
        fn1, fn2 = args
    except:
        fn1 = '../data/box.png'
        fn2 = '../data/box_in_scene.png'

    H, kp_paris = find_homography(fn1, fn2)
    print ('Got H:', H)
