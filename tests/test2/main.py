# -*- coding: utf-8 -*-
#
import os
import pickle
import shutil
import sys
import tempfile

if sys.version_info[0] == 2:
    from test import test_support as test_support
else:
    import test.support as test_support
import unittest

import numpy as np
import cv2

FLANN_INDEX_KDTREE = 1  # bug: flann enums are missing
FLANN_INDEX_LSH    = 6

__src_path__ = os.path.normpath("../../src")

class IOS_6S:
    width=4032
    height=3024
    sx=4.8
    sy=3.6
    fc=4.2

def clock():
    return cv2.getTickCount() / cv2.getTickFrequency()

def duration(t):
    return float((clock()-t)*1000)

def save_keypoint_data(filename, keypoints, descriptors):
    kpdata =  np.array([(kp.pt[0], kp.pt[1], kp.size, kp.angle, kp.response, kp.octave, kp.class_id)
                        for kp in keypoints])
    np.savez(filename, keypoints=kpdata, descriptors=descriptors)

def load_keypoint_data(filename):
    npzfile = np.load(filename if filename.endswith('.npz') else (filename + '.npz'))
    keypoints = [cv2.KeyPoint(x, y, size, angle, response, int(octave), int(class_id))
                 for x, y, size, angle, response, octave, class_id in npzfile['keypoints']]
    return keypoints, npzfile['descriptors']

class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.work_path = tempfile.mkdtemp()

        m = self.mod_solvePnp = test_support.import_module('calibration.solvePnp')
        self.m_unproject_image_points = m.unproject_image_points
        self.m_solve_pnp = m.solve_pnp

        m = test_support.import_module('calibration.feature')
        self.m_asift_detect_compute = m.asift_detect_compute
        self.m_filter_matches = m.filter_matches

        camera = IOS_6S
        fc, sx, sy, w, h = camera.fc, camera.sx, camera.sy, camera.width, camera.height
        self.Ki = np.float64([[fc*w/sx, 0, 0.5*(w-1)],
                              [0, fc*h/sy, 0.5*(h-1)],
                              [0.0,0.0,      1.0]])

    def tearDown(self):
        shutil.rmtree(self.work_path)

    def explore_match(self, img1, img2, kp_pairs, status):
        h1, w1 = img1.shape[:2]
        h2, w2 = img2.shape[:2]
        vis = np.zeros((max(h1, h2), w1+w2), np.uint8)
        vis[:h1, :w1] = img1
        vis[:h2, w1:w1+w2] = img2
        vis = cv2.cvtColor(vis, cv2.COLOR_GRAY2BGR)

        p1, p2 = [], []  # python 2 / python 3 change of zip unpacking
        for kpp in kp_pairs:
            p1.append(np.int32(kpp[0].pt))
            p2.append(np.int32(np.array(kpp[1].pt) + [w1, 0]))

        green = (0, 255, 0)
        red = (0, 0, 255)
        white = (255, 255, 255)
        kp_color = (51, 103, 236)
        for (x1, y1), (x2, y2), inlier in zip(p1, p2, status):
            if inlier:
                col = green
                cv2.circle(vis, (x1, y1), 2, col, -1)
                cv2.circle(vis, (x2, y2), 2, col, -1)
            else:
                col = red
                r = 2
                thickness = 3
                cv2.line(vis, (x1-r, y1-r), (x1+r, y1+r), col, thickness)
                cv2.line(vis, (x1-r, y1+r), (x1+r, y1-r), col, thickness)
                cv2.line(vis, (x2-r, y2-r), (x2+r, y2+r), col, thickness)
                cv2.line(vis, (x2-r, y2+r), (x2+r, y2-r), col, thickness)
        for (x1, y1), (x2, y2), inlier in zip(p1, p2, status):
            if inlier:
                cv2.line(vis, (x1, y1), (x2, y2), green)
        return vis

    def filter_matches(self, kp1, kp2, matches, ratio = 0.75):
        mkp1, mkp2 = [], []
        for m in matches:
            if len(m) == 2 and m[0].distance < m[1].distance * ratio:
                m = m[0]
                mkp1.append( kp1[m.queryIdx] )
                mkp2.append( kp2[m.trainIdx] )
        p1 = np.float32([kp.pt for kp in mkp1])
        p2 = np.float32([kp.pt for kp in mkp2])
        kp_pairs = zip(mkp1, mkp2)
        return p1, p2, list(kp_pairs)

    def match(self, matcher, kp1, desc1, kp2, desc2):
        raw_matches = matcher.knnMatch(desc1, trainDescriptors = desc2, k = 2) #2
        p1, p2, kp_pairs = self.filter_matches(kp1, kp2, raw_matches)

        if len(p1) >= 4:
            H, status = cv2.findHomography(p1, p2, cv2.RANSAC, 5.0)
            # do not draw outliers (there will be a lot of them)
            kp_pairs = [kpp for kpp, flag in zip(kp_pairs, status) if flag]
            return H, status, kp_pairs

    def correction_match(self, matcher, kp1, desc1, kp2, desc2):
        raw_matches = matcher.knnMatch(desc1, trainDescriptors = desc2, k = 2) #2
        mi, p1, p2, kp_pairs = self.m_filter_matches(kp1, kp2, raw_matches)

        if len(p1) >= 4:
            H, status = cv2.findHomography(p1, p2, cv2.RANSAC, 5.0)
            # do not draw outliers (there will be a lot of them)
            kp_pairs = [kpp for kpp, flag in zip(kp_pairs, status) if flag]
            mp = [dma.queryIdx for dma, flag in zip(mi, status) if flag]
            return mp, status, kp_pairs

    def save(self, filename, img1, img2, kp_pairs, status):
        vis = self.explore_match(img1, img2, kp_pairs, status)
        cv2.imwrite(filename, vis)

class VerifyTestCases(BaseTestCase):

    def test_robust(self):
        afeatures = 500, 1000, 2000
        nfeatures = 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000

        refimage = 'robust/00.jpg'
        images = 'robust/11.png', 'robust/22.png', 'robust/33.png', 'robust/44.png'

        results = []
        image_results = []

        flann_params= dict(algorithm = FLANN_INDEX_LSH,
                           table_number = 6, # 12
                           key_size = 12,     # 20
                           multi_probe_level = 1) #2
        matcher = cv2.FlannBasedMatcher(flann_params, {})  # bug : need to pass empty dict (#1329)
        img1 = cv2.imread(refimage, 0)

        results.append('```')
        title2 = '%8s %8s %8s %8s ' % ('查询参数', '原图取样', '查询时间', '关键点数')
        title1 = '{:8} {:_^26} '.format(' ', '原图')

        for image in images:
            name = os.path.basename(image)
            name = name[:name.find('.')]
            title2 += '{0:8} {1:8} {2:8} {3:8}{4:4} '.format('查询时间', '关键点数', '匹配时间', '匹配数目', ' ')
            title1 += ' {0:_^38} '.format(name)
        results.append(title1)
        results.append(title2)

        for n in nfeatures:
            detector2 = cv2.ORB_create(n)

            for k in afeatures:
                filename = 'results/robust/image_00_asift_%d.npz' % k
                if os.path.exists(filename):
                    start = clock()
                    kp1, desc1 = load_keypoint_data(filename)
                    t1 = duration(start)
                else:
                    detector1 = cv2.ORB_create(k)
                    start = clock()
                    kp1, desc1 = self.m_asift_detect_compute(detector1, img1)
                    t1 = duration(start)
                    save_keypoint_data(filename, kp1, desc1)
                result = '{0:<8d} {1:^8d} {2:^8.1f} {3:^8d} '.format(n, k, t1, len(kp1))
                for image in images:
                    img2 = cv2.imread(image, 0)
                    start = clock()
                    kp2, desc2 = detector2.detectAndCompute(img2, None)
                    t2 = duration(start)
                    start = clock()
                    try:
                        H, status, kp_pairs = self.match(matcher, kp1, desc1, kp2, desc2)
                    except TypeError:
                        H, status, kp_pairs = None, None, None
                    t3 = duration(start)

                    name = os.path.basename(image)
                    name = name[:name.find('.')]
                    if status is None:
                        mn = '< 4'
                    else:
                        # inliers/matched
                        mn = '%d / %d ' % (np.sum(status), len(status))
                        filename = 'results/robust/orb-{0}-asift-{1}-{2}.jpg'.format(n, k, name)
                        image_results.append('* [R{0}-A{1}-{2}]({3})'.format(n, k, name, filename))
                        self.save(filename, img1, img2, kp_pairs, status)
                    result += '{0:^8.1f} {1:^8d} {2:^8.1f} {3:12} '.format(t2, len(kp2), t3, mn)
                results.append(result)
        results.append('```\n')
        results.append('### 图片匹配结果\n')
        results.append('\n'.join(image_results))
        results.append('')
        with open('results/robust/result.txt', 'w') as f:
            f.write('\n'.join(results))

    def test_accuracy(self):
        results = []
        image_results = []
        np.set_printoptions(precision=2, suppress=True)

        afeatures = 500,
        nfeatures = 2000, 5000, 8000

        refimage = 'accuracy/1.JPG'
        images = ['accuracy/{0}.JPG'.format(i) for i in range(2, 7)]

        dt = 200
        positions = np.int32([[0, 0, -100],
                              [115, 0, 0],
                              [200, 0, 0],
                              [-115, 0, 0],
                              [-200, 0, 0]])
        angles = np.int32([0, -30, -45, 30, 45])

        flann_params= dict(algorithm = FLANN_INDEX_LSH,
                           table_number = 6, # 12
                           key_size = 12,     # 20
                           multi_probe_level = 1) #2
        matcher = cv2.FlannBasedMatcher(flann_params, {})  # bug : need to pass empty dict (#1329)
        img1 = cv2.imread(refimage, 0)

        k = afeatures[0]
        filename = 'results/accuracy/image_1_asift_%d.npz' % k
        if os.path.exists(filename):
            start = clock()
            kp1, desc1 = load_keypoint_data(filename)
            t1 = duration(start)
        else:
            detector1 = cv2.ORB_create(k)
            start = clock()
            kp1, desc1 = self.m_asift_detect_compute(detector1, img1)
            t1 = duration(start)
            save_keypoint_data(filename, kp1, desc1)

        K = self.Ki
        points = np.float64([kp.pt for kp in kp1])
        refPoints = self.m_unproject_image_points(points, K, dt)

        results.append('[原图](accuracy/1.jpg)关键点数目 %d' % len(kp1))
        results.append('')
        count = 0

        for n in nfeatures:
            count += 1
            results.append('### 结果 %d\n' % count)
            results.append('查询照片最多关键点数目: %d\n' % n)
            results.append('```')
            results.append('查询图片 查询时间 匹配时间 匹配数目   角度/期望/误差         位置/期望/误差')
            detector2 = cv2.ORB_create(n)
            count2 = 0
            for image in images:
                name = os.path.basename(image)
                name = name[:name.find('.')]

                img2 = cv2.imread(image, 0)
                assert(img2 is not None)
                start = clock()
                kp2, desc2 = detector2.detectAndCompute(img2, None)
                t2 = duration(start)                
                try:
                    start = clock()
                    mp, status, kp_pairs = self.correction_match(matcher, kp1, desc1, kp2, desc2)
                except TypeError:
                    mp, status, kp_pairs = None, None, None
                t3 = duration(start)
                if status is None:
                    result = '%-8s %-8.1f %-8.1f %s' % (name, t2, t3, '没有足够匹配点 < 4')
                else:
                    mn = '%d/%d ' % (np.sum(status), len(status))
                    filename = 'results/accuracy/orb-{0}-asift-{1}-{2}.jpg'.format(n, k, name)
                    image_results.append('* [L{0}-A{1}-{2}]({3})'.format(n, k, name, filename))
                    self.save(filename, img1, img2, kp_pairs, status)

                    imagePoints = np.float64([kpp[1].pt for kpp in kp_pairs])
                    yaw, vt = self.m_solve_pnp(refPoints[mp], imagePoints, K)
                    a1 = float(yaw * 180 / np.pi)
                    ra = '%4.0f / %i / %i' % (a1, angles[count2], angles[count2] - a1)
                    rv = '%s / %s / %s' % (vt.ravel(), positions[count2], (vt - positions[count2]).ravel())
                    result = '%-8s %-8.1f %-8.1f %-10s %-20s %s' % (name, t2, t3, mn, ra, rv)
                results.append(result)                
                count2 += 1
            results.append('```\n')
        # results.append('### 图片匹配结果\n')
        # results.append('\n'.join(image_results))
        # results.append('')
        with open('results/accuracy/result.txt', 'w') as f:
            f.write('\n'.join(results))
        print '\n'.join(results)

    def test_accuracy_coffee(self):
        results = []
        image_results = []
        np.set_printoptions(precision=2, suppress=True)

        afeatures = 500,
        nfeatures = 2000, 5000, 8000

        refimage = 'accuracy/coffee_front.jpg'
        images = ['accuracy/coffee_side.jpg']

        dt = 250
        positions = np.int32([[-216, 0, 125]])
        angles = np.int32([60])

        flann_params= dict(algorithm = FLANN_INDEX_LSH,
                           table_number = 6, # 12
                           key_size = 12,     # 20
                           multi_probe_level = 1) #2
        matcher = cv2.FlannBasedMatcher(flann_params, {})  # bug : need to pass empty dict (#1329)
        img1 = cv2.imread(refimage, 0)

        k = afeatures[0]
        filename = 'results/accuracy/coffee_asift_%d.npz' % k
        if os.path.exists(filename):
            start = clock()
            kp1, desc1 = load_keypoint_data(filename)
            t1 = duration(start)
        else:
            detector1 = cv2.ORB_create(k)
            start = clock()
            kp1, desc1 = self.m_asift_detect_compute(detector1, img1)
            t1 = duration(start)
            save_keypoint_data(filename, kp1, desc1)

        K = self.Ki
        points = np.float64([kp.pt for kp in kp1])
        refPoints = self.m_unproject_image_points(points, K, dt)

        results.append('[coffee_front.jpg](accuracy/coffee_front.jpg)关键点数目 %d' % len(kp1))
        results.append('')
        count = 0

        for n in nfeatures:
            count += 1
            results.append('### 结果 %d\n' % count)
            results.append('查询照片最多关键点数目: %d\n' % n)
            results.append('```')
            results.append('查询图片 查询时间 匹配时间 匹配数目   角度/期望/误差         位置/期望/误差')
            detector2 = cv2.ORB_create(n)
            count2 = 0
            for image in images:
                name = os.path.basename(image)
                name = name[:name.find('.')]

                img2 = cv2.imread(image, 0)
                assert(img2 is not None)
                start = clock()
                kp2, desc2 = detector2.detectAndCompute(img2, None)
                t2 = duration(start)                
                try:
                    start = clock()
                    mp, status, kp_pairs = self.correction_match(matcher, kp1, desc1, kp2, desc2)
                except TypeError:
                    mp, status, kp_pairs = None, None, None
                t3 = duration(start)
                if status is None:
                    result = '%-8s %-8.1f %-8.1f %s' % (name, t2, t3, '没有足够匹配点 < 4')
                else:
                    mn = '%d/%d ' % (np.sum(status), len(status))
                    filename = 'results/accuracy/coffee-{0}-asift-{1}-{2}.jpg'.format(n, k, name)
                    image_results.append('* [L{0}-A{1}-{2}]({3})'.format(n, k, name, filename))
                    self.save(filename, img1, img2, kp_pairs, status)

                    imagePoints = np.float64([kpp[1].pt for kpp in kp_pairs])
                    yaw, vt = self.m_solve_pnp(refPoints[mp], imagePoints, K)
                    a1 = float(yaw * 180 / np.pi)
                    ra = '%4.0f / %i / %i' % (a1, angles[count2], angles[count2] - a1)
                    rv = '%s / %s / %s' % (vt.ravel(), positions[count2], (vt - positions[count2]).ravel())
                    result = '%-8s %-8.1f %-8.1f %-10s %-20s %s' % (name, t2, t3, mn, ra, rv)
                results.append(result)                
                count2 += 1
            results.append('```\n')
        # results.append('### 图片匹配结果\n')
        # results.append('\n'.join(image_results))
        # results.append('')
        with open('results/accuracy/coffee-result.txt', 'w') as f:
            f.write('\n'.join(results))
        print '\n'.join(results)

if __name__ == '__main__':
    sys.path.insert(0, __src_path__)

    loader = unittest.TestLoader()
    loader.testMethodPrefix = 'test_accuracy_coffee'
    suite = loader.loadTestsFromTestCase(VerifyTestCases)
    unittest.TextTestRunner(verbosity=2).run(suite)
