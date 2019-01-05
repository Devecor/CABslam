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

__src_path__ = os.path.normpath("../src/calibration")

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
        self.work_path = tempfile.mkdtemp()

        m = self.mod_matchFeature = test_support.import_module('matchFeature')
        self.m_find_homography = m.find_homography
        self.m_find_asift_homography = m.find_asift_homography

        m = self.mod_solvePnp = test_support.import_module('solvePnp')
        self.m_unproject_image_points = m.unproject_image_points
        self.m_solve_pnp = m.solve_pnp

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
        
    def tearDown(self):
        shutil.rmtree(self.work_path)


class SolvePnpTestCases(BaseTestCase):

    def test_solve_pnp_map_left(self):
        fm = self.m_solve_pnp
        fn1, fn2 = 'images/world_map_front.jpg', 'images/world_map_left.jpg'
        H, kp_pairs = self.m_find_homography(fn1, fn2)

        t = 230
        tvec = np.float64([0, -130, -230])
        K = self.Kh

        e_tvec = np.float64([-120, -130, -350])
        e_azimuth = -0.33

        points = np.float64([kpp[0].pt for kpp in kp_pairs])
        refPoints = self.m_unproject_image_points(points, K, t)

        imagePoints = np.float64([kpp[1].pt for kpp in kp_pairs])
        yaw, vt = self.mod_solvePnp.solve_pnp(refPoints, imagePoints, K)
        a_tvec = tvec - vt.ravel()
        print 'Solve pnp say map left: ', yaw, vt.ravel()
        print 'Expected: ', e_azimuth, e_tvec
        print 'Actual:', yaw, a_tvec
        print 'Deviation: ', yaw - e_azimuth, a_tvec - e_tvec

    def test_solve_pnp_map_right(self):
        fm = self.m_solve_pnp
        fn1, fn2 = 'images/world_map_front.jpg', 'images/world_map_right.jpg'
        H, kp_pairs = self.m_find_homography(fn1, fn2)

        t = 230
        tvec = np.float64([0, -130, -230])
        K = self.Kh

        e_tvec = np.float64([120, -130, -350])
        e_azimuth = 0.33

        points = np.float64([kpp[0].pt for kpp in kp_pairs])
        refPoints = self.m_unproject_image_points(points, K, t)

        imagePoints = np.float64([kpp[1].pt for kpp in kp_pairs])
        yaw, vt = self.mod_solvePnp.solve_pnp(refPoints, imagePoints, K)
        a_tvec = tvec - vt.ravel()
        print 'Solve pnp say map right: ', yaw, vt.ravel()
        print 'Expected: ', e_azimuth, e_tvec
        print 'Actual:', yaw, a_tvec
        print 'Deviation: ', yaw - e_azimuth, a_tvec - e_tvec

    def test_solve_pnp_coffee(self):
        fm = self.m_solve_pnp
        fn1, fn2 = 'images/coffee_front.jpg', 'images/coffee_side.jpg'
        hdata = 'images/coffee_match.data'
        if os.path.exists(hdata):
            with open(hdata, 'rb') as f:
                H, kp_data = pickle.load(f)
        else:
            H, kp_pairs = self.m_find_asift_homography(fn1, fn2)
            kp_data = np.array([(kpp[0].pt, kpp[1].pt) for kpp in kp_pairs])
            with open(hdata, 'wb') as f:
                pickle.dump((H, kp_data), f)

        # scale = 0.25
        # H, kp_pairs = self.m_find_asift_homography(fn1, fn2, scale=scale)
        # kp_data = np.array([(kpp[0].pt, kpp[1].pt) for kpp in kp_pairs])        
        scale = 1.0

        t = 250
        tvec = np.float64([0, -120, -250])
        K = self.Ki * scale

        e_tvec = np.float64([176, -120, -176])
        e_azimuth = 1.03

        points = np.float64([kpp[0] for kpp in kp_data])
        refPoints = self.m_unproject_image_points(points, K, t)

        imagePoints = np.float64([kpp[1] for kpp in kp_data])
        yaw, vt = self.mod_solvePnp.solve_pnp(refPoints, imagePoints, K)
        a_tvec = tvec - vt.ravel()
        print 'Solve pnp say coffee: ', yaw, vt.ravel()
        print 'Expected: ', e_azimuth, e_tvec
        print 'Actual:', yaw, a_tvec
        print 'Deviation: ', yaw - e_azimuth, a_tvec - e_tvec

    def test_solve_pnp_recover_coffee_1_2(self):
        fm = self.m_solve_pnp
        fn1, fn2 = 'recover/images/1-1.jpg', 'recover/images/1-2.jpg'
        hdata = 'images/recover_coffee_1_2.data'
        if os.path.exists(hdata):
            with open(hdata, 'rb') as f:
                H, kp_data = pickle.load(f)
        else:
            H, kp_pairs = self.m_find_asift_homography(fn1, fn2)
            kp_data = np.array([(kpp[0].pt, kpp[1].pt) for kpp in kp_pairs])
            with open(hdata, 'wb') as f:
                pickle.dump((H, kp_data), f)

        # scale = 0.25
        # H, kp_pairs = self.m_find_asift_homography(fn1, fn2, scale=scale)
        # kp_data = np.array([(kpp[0].pt, kpp[1].pt) for kpp in kp_pairs])        
        scale = 1.0

        t = 500
        tvec = np.float64([0, -120, -500])
        K = self.Ki * scale

        e_tvec = np.float64([240, -120, -500])
        e_azimuth = 0.4475

        points = np.float64([kpp[0] for kpp in kp_data])
        refPoints = self.m_unproject_image_points(points, K, t)

        imagePoints = np.float64([kpp[1] for kpp in kp_data])
        yaw, vt = self.mod_solvePnp.solve_pnp(refPoints, imagePoints, K)
        a_tvec = tvec - vt.ravel()
        print 'Solve pnp say recover 1-2: ', yaw, vt.ravel()
        print 'Expected: ', e_azimuth, e_tvec
        print 'Actual:', yaw, a_tvec
        print 'Deviation: ', yaw - e_azimuth, a_tvec - e_tvec

    def test_solve_pnp_recover_coffee_1_3(self):
        fm = self.m_solve_pnp
        fn1, fn2 = 'recover/images/1-1.jpg', 'recover/images/1-3.jpg'
        hdata = 'images/recover_coffee_1_3.data'
        if os.path.exists(hdata):
            with open(hdata, 'rb') as f:
                H, kp_data = pickle.load(f)
        else:
            H, kp_pairs = self.m_find_asift_homography(fn1, fn2)
            kp_data = np.array([(kpp[0].pt, kpp[1].pt) for kpp in kp_pairs])
            with open(hdata, 'wb') as f:
                pickle.dump((H, kp_data), f)

        # scale = 0.25
        # H, kp_pairs = self.m_find_asift_homography(fn1, fn2, scale=scale)
        # kp_data = np.array([(kpp[0].pt, kpp[1].pt) for kpp in kp_pairs])        
        scale = 1.0

        t = 500
        tvec = np.float64([0, -120, -500])
        K = self.Ki * scale

        e_tvec = np.float64([120, -120, -500])
        e_azimuth = 0.2355

        points = np.float64([kpp[0] for kpp in kp_data])
        refPoints = self.m_unproject_image_points(points, K, t)

        imagePoints = np.float64([kpp[1] for kpp in kp_data])
        yaw, vt = self.mod_solvePnp.solve_pnp(refPoints, imagePoints, K)
        a_tvec = tvec - vt.ravel()
        print 'Solve pnp say recover 1-3: ', yaw, vt.ravel()
        print 'Expected: ', e_azimuth, e_tvec
        print 'Actual:', yaw, a_tvec
        print 'Deviation: ', yaw - e_azimuth, a_tvec - e_tvec


if __name__ == '__main__':
    sys.path.insert(0, __src_path__)

    loader = unittest.TestLoader()
    # loader.testMethodPrefix = 'test_solve_pnp_recover'
    suite = loader.loadTestsFromTestCase(SolvePnpTestCases)
    unittest.TextTestRunner(verbosity=2).run(suite)
