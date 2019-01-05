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

__src_path__ = os.path.normpath("../src")

class HUAWEI_G520:
    width=1920
    height=2560
    sx=3.05
    sy=4.13
    fc=3.5

class IOS_6S:
    width=4032
    height=3024
    sx=4.8
    sy=3.6
    fc=4.2

class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.work_path = '__data__'
        os.mkdir(self.work_path)

        m = self.mod_config = test_support.import_module('config')
        m.base_data_path = self.work_path

        m = self.mod_manager = test_support.import_module('manager')


        camera = HUAWEI_G520
        fc, sx, sy, w, h = camera.fc, camera.sx, camera.sy, camera.width, camera.height
        self.Kh = np.float64([[fc*w/sx, 0, 0.5*(w-1)],
                              [0, fc*h/sy, 0.5*(h-1)],
                              [0.0,0.0,      1.0]])

        camera = IOS_6S
        fc, sx, sy, w, h = camera.fc, camera.sx, camera.sy, camera.width, camera.height
        self.Ki = np.float64([[fc*w/sx, 0, 0.5*(w-1)],
                              [0, fc*h/sy, 0.5*(h-1)],
                              [0.0,0.0,      1.0]])
        
        s = self.building = 'wuxin'
        shutil.copytree(os.path.join('data', s), os.path.join(self.work_path, s))
        
        self.wifi_list = [ "TP-LINK_A970D6", "TP-LINK_5G_A7AC", "TP-LINK_4D5A3C", "TP-LINK_UFO"]

    def tearDown(self):
        shutil.rmtree(self.work_path)

    def detect_feature(self):
        detector = cv2.ORB_create(800)
        fn = 'images/world_map_front.jpg'
        img = cv2.imread(fn, 0)
        return detector.detectAndCompute(img, None)

class ManagerTestCases(BaseTestCase):

    def no_test_write_yaml(self):
        fm = self.mod_manager.write_yaml
        kps, descs = self.detect_feature()
        points = np.float64([[0.1, 0, 0, 0.2], [0.2, 0, -1, 0.3]])
        fm('data/test.yaml', kps, descs, points)

    def test_save_and_load_keypoint_data(self):
        filename = os.path.join('data', self.building, 'r0', 'test.npz')
        fm = self.mod_manager.save_keypoint_data
        kps, descs = self.detect_feature()
        points = np.float64([[0.1, 0, 0, 0.2], [0.2, 0, -1, 0.3]])
        fm(filename, kps, descs, points)

        fm = self.mod_manager.load_keypoint_data
        kps2, descs2, points2 = fm(self.building, 0, 'test.npz')

        self.assertEqual(kps[0].pt, kps2[0].pt)
        self.assertListEqual(list(descs[0]), list(descs2[0]))
        self.assertListEqual(list(points[0]), list(points2[0]))


    def test_get_region_images(self):
        fm = self.mod_manager.get_region_images
        images = fm(self.building, 0)

    def test_get_region_list(self):
        fm = self.mod_manager.get_region_list
        regions = fm(self.building)

    def test_get_region_path(self):
        fm = self.mod_manager.get_region_path
        self.assertEqual(fm(self.building, 1),
                         os.path.normpath(self.work_path + '/' + self.building + '/r1'))

    def test_find_region_by_position(self):
        fm =self.mod_manager.find_region_by_position
        regions = self.mod_manager.get_region_list(self.building)

        p = [3.2, 5.8, 0]
        r = fm(regions, p)
        self.assertEqual(r, 0)

        p = [15.2, 5.8, 0]
        r = fm(regions, p)
        self.assertEqual(r, 1)

        p = [15.2, 15.8, 0]
        r = fm(regions, p)
        self.assertIsNone(r)

    def test_merge_image_into_region(self):
        fm = self.mod_manager.merge_image_into_region
        kps, descs, points = self.mod_manager.load_keypoint_data(self.building, 0, 'img-20170805-123029')

        position = 0.5, 3.2, 0
        azimuth = 10
        camera = 3528, 3528, 2506, 1920
        name = fm(self.building, position, azimuth, camera, kps, descs, points)

    def test_stereo_rectify_and_triangulate_points(self):
        fm = self.mod_manager.stereo_rectify

        size = IOS_6S.height, IOS_6S.width
        distCoeffs = np.zeros(4)
        t = np.float64([0.2, 0, 0])
        r = np.float64([0, 0.05, 0])
        P1, P2, Q = fm(self.Ki, distCoeffs, self.Ki, distCoeffs, size, r, t)

        fm = self.mod_manager.triangulate_points
        pts1 = np.float64([0, 0])
        pts2 = np.float64([0, 0])
        pt3d = fm(P1, P2, pts1, pts2)

    def test_add_image(self):
        fm = self.mod_manager.add_image

        building = self.building
        position = 2.3, 3.6, 0
        azimuth = 10
        focal = 3528, 3528
        mask = None
        distance = 2.5
        filename = 'images/world_map_front.jpg'
        asift = False

        name = fm(building, position, azimuth, focal, mask, distance, filename, asift)

    def test_add_image_with_mask(self):
        fm = self.mod_manager.add_image

        building = self.building
        position = 2.3, 3.6, 1.3
        azimuth = 0
        focal = self.Kh[0][0], self.Kh[1][1]
        mask = 20, 300, 1875, 1765
        distance = 2.5
        filename = 'images/world_map_front.jpg'
        asift = False

        name = fm(building, position, azimuth, focal, mask, distance, filename, asift)
        
        # path = os.path.join(self.work_path, 'wuxin', 'r0')
        # shutil.copy(os.path.join(path, 'images.json'), 'data')
        # shutil.copy(os.path.join(path, name + '.npz'), 'data')

    def no_test_add_image_with_asift(self):
        fm = self.mod_manager.add_image

        building = self.building
        position = 2.3, 3.6, 0
        azimuth = 10
        focal = 3528, 3528
        mask = None
        distance = 2.5
        filename = 'images/world_map_front.jpg'
        asift = True

        name = fm(building, position, azimuth, focal, mask, distance, filename, asift)

    def no_test_add_stereo_images(self):
        fm = self.mod_manager.add_stereo_images

        building = self.building
        position = 2.3, 3.6, 0
        azimuth = 0
        focal = 3528, 3528
        rotate = 0.33
        offset = np.float64([-1.2, 0, -1.2])
        filename1 = 'images/world_map_front.jpg'
        filename2 = 'images/world_map_right.jpg'
        asift = False

        name = fm(building, position, azimuth, focal, rotate, offset, filename1, filename2)

    def test_get_wifi_list(self):
        fm = self.mod_manager.get_wifi_list
        building = self.building
        wifis = fm(building)
        self.assertListEqual(wifis, self.wifi_list)

    def test_append_wifi_bssid(self):
        fm = self.mod_manager.append_wifi_bssid
        building = self.building
        bssid = 'abcdef'
        fm(building, bssid)

        wifis = self.mod_manager.get_wifi_list(building)
        self.assertListEqual(wifis, self.wifi_list +[bssid])

    def test_merge_wifi_data(self):
        fm = self.mod_manager.merge_wifi_data
        building = self.building
        bssid = 'TP-LINK_A970D6'
        data = [-50, 2.3, 3.1, 0], [-60, 12.5, 5.2, 0]
        fm(building, bssid, data)

        bssid = 'NewBssid'
        data = [-50, 2.3, 3.1, 0], [-60, 12.5, 5.2, 0]
        fm(building, bssid, data)

    def test_build_finger_from_rssi(self):
        fm = self.mod_manager.build_finger_from_rssi
        building = self.building
        filename = 'data/TP-LINK_A970D6.txt'
        data = np.loadtxt(filename)
        finger = fm(building, data)
        self.assertListEqual(list(finger), [-50., -80.])

    def test_add_wifi_finger(self):
        fm = self.mod_manager.add_wifi_finger
        building = self.building
        filename = 'data/TP-LINK_A970D6.txt'
        rssid = 'TP-LINK_A970D6'
        fm(building, rssid, filename)

if __name__ == '__main__':
    sys.path.insert(0, __src_path__)

    loader = unittest.TestLoader()
    # loader.testMethodPrefix = 'test_add_image_with_mask'
    suite = loader.loadTestsFromTestCase(ManagerTestCases)
    unittest.TextTestRunner(verbosity=2).run(suite)
