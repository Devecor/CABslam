# -*- coding: utf-8 -*-
#
# ！！！ 这个文件不再使用，属于前期的探索性代码，已经完成使命。#
# ！！！保留于此，以作纪念。
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
    alpha=1.
    width=1920
    height=2560
    sx=3.05
    sy=4.13
    fc=3.5

class HUAWEI_CX7:
    alpha=1.
    width=3264
    height=2448
    sx=4.8
    sy=3.6
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

        m = test_support.import_module('matchFeature')
        self.m_find_homography = m.find_homography
        self.m_find_asift_homography = m.find_asift_homography

        self.mod_recoverPose = m = test_support.import_module('recoverPose')
        self.m_calculate_image_points = m.calculate_image_points
        self.m_find_pose = m.find_pose

        cameraHeight = 130
        camera = HUAWEI_G520
        fc, sx, sy, w, h, alpha = camera.fc, camera.sx, camera.sy, camera.width, camera.height, camera.alpha
        self.Kh = np.float64([[fc*w/sx, 0, 0.5*(w-1)],
                              [0, fc*h/sy, 0.5*(h-1)],
                              [0.0,0.0,      1.0]]) * alpha
        self.Th_front = np.float64([0, cameraHeight, 230])
        self.map_corners = np.float64([[-95, -233, 0], [56, -233, 0], [56, -123, 0], [-95, -123, 0]])

        self.Th_front2 = np.float64([60, cameraHeight, 230])
        self.map_corners2 = np.float64([[-150, -230, 0], [0, -230, 0], [0, -120, 0], [-150, -120, 0]])

        self.Th_left = np.float64([-120, cameraHeight, 350])
        a = -np.arctan2(120.0, 350) / alpha
        sa, ca = np.sin(a), np.cos(a)
        self.Rh_left_yaw = a
        self.Rh_left = np.float64([[ca,  0, sa],
                                   [0,   1, 0],
                                   [-sa, 0, ca]])
        self.Rhv_left, jacobian = cv2.Rodrigues(self.Rh_left)

        self.Th_right = np.float64([-120, cameraHeight, 350])
        a = np.arctan2(120, 350.0) / alpha
        sa, ca = np.sin(a), np.cos(a)
        self.Rh_right_yaw = a
        self.Rh_right = np.float64([[ca,  0, sa],
                                   [0,   1, 0],
                                   [-sa, 0, ca]])

        # 地图的左上角和右下角两个参考点
        self.h_points = np.float64([[-90, -230, 0], [90, -230, 0]])

        camera = IOS_6S
        fc, sx, sy, w, h = camera.fc, camera.sx, camera.sy, camera.width, camera.height
        self.Ki = np.float64([[fc*w/sx, 0, 0.5*(w-1)],
                              [0, fc*h/sy, 0.5*(h-1)],
                              [0.0,0.0,      1.0]])

        self.UnitRt = np.float64([[1, 0, 0],
                                  [0, 1, 0],
                                  [0, 0, 1]])
        self.UnitRv = np.float64([0, 0, 0])
        self.zeroDistCoeffs = np.zeros(4)

        PI = 3.1415926
        a = 1/18.0*PI
        sa, ca = np.sin(a), np.cos(a)
        self.Rt_yaw_10 = np.float64([[ca,  0, sa],
                                    [0,   1, 0],
                                    [-sa, 0, ca]])
        self.Rv_yaw_10, jacobian = cv2.Rodrigues(self.Rt_yaw_10)

        a = -1/18.0*PI
        sa, ca = np.sin(a), np.cos(a)
        self.Rt_yaw_n10 = np.float64([[ca,  0, sa],
                                    [0,   1, 0],
                                    [-sa, 0, ca]])
        self.Rv_yaw_n10, jacobian = cv2.Rodrigues(self.Rt_yaw_n10)

        a = PI / 4
        sa, ca = np.sin(a), np.cos(a)
        self.Rt_yaw_45 = np.float64([[ca,  0, sa],
                                    [0,   1, 0],
                                    [-sa, 0, ca]])
        self.Rv_yaw_45, jacobian = cv2.Rodrigues(self.Rt_yaw_45)

    def tearDown(self):
        shutil.rmtree(self.work_path)

    def projectPoints(self, cameraMatrix, rm, tvec, points):
        fx, fy, cx, cy = cameraMatrix[0][0], cameraMatrix[1][1], cameraMatrix[0][2], cameraMatrix[1][2]

        # refPoints = points - tvec
        # p1 = (rm * refPoints[0].reshape(3, 1)).A.reshape(-1)
        # p2 = (rm * refPoints[1].reshape(3, 1)).A.reshape(-1)

        # m1 = (cameraMatrix * p1.reshape(3, 1)).A.reshape(-1)
        # m2 = (cameraMatrix * p2.reshape(3, 1)).A.reshape(-1)

        # rotPoints = np.array([p1, p2])

        # m1 = p1[:2] / p1[2]
        # m2 = p2[:2] / p2[2]

        # m1 = np.float64([m1[0] * fx, m1[1] * fy]) + (cx, cy)
        # m2 = np.float64([m2[0] * fx, m2[1] * fy]) + (cx, cy)

        # imgPoints = np.array([m1, m2])

        refPoints = points - tvec
        if rm is not None:
            rotPoints = np.array([(rm * p.reshape(3, 1)).A.reshape(-1) for p in refPoints])
        else:
            rotPoints = refPoints
        tmpPoints = [p[:2] / p[2] for p in rotPoints]
        imagePoints = np.array([[p[0] * fx + cx, p[1] * fy + cy] for p in tmpPoints])
        return rotPoints, imagePoints

class RecoverPoseTestCases(BaseTestCase):

    def test_rotation_matrix(self):
        rt = np.matrix(self.Rt_yaw_10)
        rtn = np.matrix(self.Rt_yaw_n10)
        v = np.float64([0, 0, 1]).reshape(3, 1)

        ret = rt * v
        print 'Z axis rotate 10: ', ret.reshape(-1)

        ret = rtn * v
        print 'Z axis rotate -10: ', ret.reshape(-1)

    def test_offset_no_change(self):
        cameraMatrix = self.Kh
        fx, fy, cx, cy = self.Kh[0][0], self.Kh[1][1], self.Kh[0][2], self.Kh[1][2]
        a = -3.1415926 / 10 # z->x 旋转矩阵角度为负，顺时针
        sa, ca = np.sin(a), np.cos(a)
        rt_yaw_n45 = np.float64([[ca,  0, sa],
                                 [0,   1, 0],
                                 [-sa, 0, ca]])
        rm = np.matrix(rt_yaw_n45)

        sa, ca = np.sin(-a), np.cos(-a)
        rtn = np.float64([[ca,  0, sa],
                          [0,   1, 0],
                          [-sa, 0, ca]])
        rmn = np.matrix(rtn)

        tvec1 = np.float64([0, -120, -230])
        tvec2 = np.float64([-120, -120, -350])
        refPoints = np.float64([[-90, -230, 0], [60, -230, 0], [60, -100, 0], [-90, -100, 0],
                                [-30, -150, 0], [10, -60, 0], [-200, -230, 0], [-1200, -160, 0]])

        rotatePoints, imagePoints = self.projectPoints(cameraMatrix, None, tvec1, refPoints)
        print 'Image Points by my projectPoints no rotate:', imagePoints

        imagePoints, jacobian = cv2.projectPoints(refPoints, self.UnitRv, tvec1*-1, cameraMatrix, self.zeroDistCoeffs)
        print 'Image Points by cv2.projectPoints no rotate:', imagePoints

        rotatePoints, imagePoints = self.projectPoints(cameraMatrix, rm, tvec1, refPoints)
        print 'Pos:', tvec1
        print 'Points:', refPoints
        print 'Rotate Points:', rotatePoints
        print 'Image Points:', imagePoints

        # imagePoints, jacobian = cv2.projectPoints(refPoints, cv2.Rodrigues(rt_yaw_n45)[0], tvec1*-1, cameraMatrix, self.zeroDistCoeffs)
        # print 'Image Points by cv2.projectPoints:', imagePoints

        # a = -3.1415926 / 8 # z->x 旋转矩阵角度为负，顺时针
        # a += 0.05
        sa, ca = np.sin(a), np.cos(a)
        rt2 = np.float64([[ca,  0, sa],
                          [0,   1, 0],
                          [-sa, 0, ca]])
        rm2 = np.matrix(rt2)

        rotatePoints2, imagePoints2 = self.projectPoints(cameraMatrix, rm2, tvec2, refPoints)
        print 'Pos:', tvec2
        print 'Points:', refPoints
        print 'Rotate Points:', rotatePoints2
        print 'Image Points:', imagePoints2

        for i in range(rotatePoints.shape[0]):
            x0, y0, z0 = rotatePoints.reshape(-1, 3)[i]
            ma = imagePoints.reshape(-1, 2)[i]
            assert(not z0 == 0)
            print "Point ", i, refPoints[i]
            print "Rotate:", x0, y0, z0

            Ma = imagePoints2.reshape(-1, 2)[i]

            print "Ma, ma:", Ma, ma
            du, dv = (Ma - ma).reshape(-1, 2)[0]
            print "du, dv:", du, dv

            dz2 = z0 - y0 / ( dv / fy + y0 / z0 )
            dx2 = x0 - ( du / fx + x0 / z0 ) * ( z0 - dz2 )
            print
            angle = -a # z->x 为正， 大于 0，顺时针
            print "dx2, dz2:", dx2, dz2
            s1 = dx2 * np.tan(angle)
            s2 = dz2 - s1
            dz = s2 * np.cos(angle)
            dx = dx2 / np.cos(angle) + s2 * np.sin(angle)
            # dx = -np.sqrt(dz2*dz2 + dx2*dx2 - dz*dz)
            print "dx, dz:", dx, dz
            p = np.float64([dx2, 0, dz2]).reshape(3, 1)

            print "Rotate negative:", rm.T * p
            print
            print

    def test_rotate_no_change(self):
        cameraMatrix = self.Kh
        a = -3.1415926 / 6
        # a = -0.8
        b = 0
        c = 0
        sa, ca = np.sin(a), np.cos(a)
        rt_yaw_n45 = np.float64([[ca,  0, sa],
                                 [0,   1, 0],
                                 [-sa, 0, ca]])
        rt_roll_n45 = np.float64([[ca,  -sa, 0],
                                  [sa,   ca, 0],
                                  [ 0,    0, 1]])

        rm = np.matrix(rt_roll_n45) * np.matrix(rt_yaw_n45)
        # rm = self.mod_recoverPose.compose_rotation_matrix(yaw=a, pitch=b, roll=c)
        points = np.float64([[0, -10, 0], [0, -210, 0]])
        tvec = np.float64([0, -130, -230])

        # rotatePoints, imagePoints = self.projectPoints(cameraMatrix, None, tvec, points)
        # print 'Pos:', tvec
        # print 'Points:', points
        # print 'No rotate Image Points:', imagePoints
        # print 'du, dv', imagePoints[1] - imagePoints[0]
        # print 'length:', np.linalg.norm(imagePoints[0] - imagePoints[1])

        rotatePoints, imagePoints = self.projectPoints(cameraMatrix, rm, tvec, points)
        print 'Pos:', tvec
        print 'Points:', points
        print 'Rotate Points:', rotatePoints
        print 'Image Points:', imagePoints
        print 'du, dv', imagePoints[1] - imagePoints[0]
        print 'length:', np.linalg.norm(imagePoints[0] - imagePoints[1])

        tvec = np.float64([-30, -130, -200])
        rotatePoints, imagePoints = self.projectPoints(cameraMatrix, rm, tvec, points)
        print 'Pos:', tvec
        print 'Points:', points
        print 'Rotate Points:', rotatePoints
        print 'Image Points:', imagePoints
        print 'du, dv', imagePoints[1] - imagePoints[0]
        print 'length:', np.linalg.norm(imagePoints[0] - imagePoints[1])

        tvec = np.float64([30, -130, -260])
        rotatePoints, imagePoints = self.projectPoints(cameraMatrix, rm, tvec, points)
        print 'Pos:', tvec
        print 'Points:', points
        print 'Rotate Points:', rotatePoints
        print 'Image Points:', imagePoints
        print 'du, dv', imagePoints[1] - imagePoints[0]
        print 'length:', np.linalg.norm(imagePoints[0] - imagePoints[1])

        tvec = np.float64([80, -130, -310])
        rotatePoints, imagePoints = self.projectPoints(cameraMatrix, rm, tvec, points)
        print 'Pos:', tvec
        print 'Points:', points
        print 'Rotate Points:', rotatePoints
        print 'Image Points:', imagePoints
        print 'du, dv', imagePoints[1] - imagePoints[0]
        print 'length:', np.linalg.norm(imagePoints[0] - imagePoints[1])


    def test_keep_size(self):
        points = np.float64([[0, 0, 0], [0, 160, 0]])
        rm = np.matrix(self.Rt_yaw_45)
        p1 = (rm * ( points[0] - self.Th_front).reshape(3, 1)).A.reshape(-1)
        p2 = (rm * ( points[1] - self.Th_front).reshape(3, 1)).A.reshape(-1)
        print 'p1:', p1
        print 'p2:', p2

        imagePoints, jacobian = cv2.projectPoints(points - self.Th_front, self.Rv_yaw_45, self.Th_front, self.Kh, self.zeroDistCoeffs)
        imagePoints = imagePoints.reshape(-1, 2)
        print 'Th:', self.Th_front
        print 'Rotate yaw 45:', imagePoints
        print 'line du, dv', imagePoints[1] - imagePoints[0]
        print 'length:', np.linalg.norm(imagePoints[0] - imagePoints[1])

        self.Th_front = self.Th_front - ( 30, 0, 30 )
        imagePoints, jacobian = cv2.projectPoints(points - self.Th_front, self.Rv_yaw_45, self.Th_front, self.Kh, self.zeroDistCoeffs)
        imagePoints = imagePoints.reshape(-1, 2)
        print 'Th:', self.Th_front
        print 'Rotate yaw 45 move 30:', imagePoints
        print 'line du, dv', imagePoints[1] - imagePoints[0]
        print 'length:', np.linalg.norm(imagePoints[0] - imagePoints[1])

        self.Th_front = self.Th_front + ( 60, 0, 60 )
        imagePoints, jacobian = cv2.projectPoints(points - self.Th_front, self.Rv_yaw_45, self.Th_front, self.Kh, self.zeroDistCoeffs)
        imagePoints = imagePoints.reshape(-1, 2)
        print 'Th:', self.Th_front
        print 'Rotate yaw 45 move 30:', imagePoints
        print 'line du, dv', imagePoints[1] - imagePoints[0]
        print 'length:', np.linalg.norm(imagePoints[0] - imagePoints[1])

    def test_keep_size_no_rotate(self):
        points = self.map_corners
        imagePoints, jacobian = cv2.projectPoints(points, self.UnitRv, self.Th_front, self.Kh, self.zeroDistCoeffs)
        imagePoints = imagePoints.reshape(-1, 2)
        print 'Th:', self.Th_front
        print 'No Rotate:', imagePoints
        print 'line du, dv', imagePoints[1] - imagePoints[0]
        print 'length:', np.linalg.norm(imagePoints[0] - imagePoints[1])
        print 'height:', np.linalg.norm(imagePoints[0] - imagePoints[3])
        print 'cross:', np.linalg.norm(imagePoints[0] - imagePoints[2])

        self.Th_front = self.Th_front - ( 30, 0, 0 )
        imagePoints, jacobian = cv2.projectPoints(points, self.UnitRv, self.Th_front, self.Kh, self.zeroDistCoeffs)
        imagePoints = imagePoints.reshape(-1, 2)
        print 'Th:', self.Th_front
        print 'No Rotate:', imagePoints
        print 'line du, dv', imagePoints[1] - imagePoints[0]
        print 'length:', np.linalg.norm(imagePoints[0] - imagePoints[1])
        print 'height:', np.linalg.norm(imagePoints[0] - imagePoints[3])
        print 'cross:', np.linalg.norm(imagePoints[0] - imagePoints[2])

        self.Th_front = self.Th_front + ( 60, 0, 0 )
        imagePoints, jacobian = cv2.projectPoints(points, self.UnitRv, self.Th_front, self.Kh, self.zeroDistCoeffs)
        imagePoints = imagePoints.reshape(-1, 2)
        print 'Th:', self.Th_front
        print 'No Rotate:', imagePoints
        print 'line du, dv', imagePoints[1] - imagePoints[0]
        print 'length:', np.linalg.norm(imagePoints[0] - imagePoints[1])
        print 'height:', np.linalg.norm(imagePoints[0] - imagePoints[3])
        print 'cross:', np.linalg.norm(imagePoints[0] - imagePoints[2])

        self.Th_front = self.Th_front + ( 30, 100, 0 )
        imagePoints, jacobian = cv2.projectPoints(points, self.UnitRv, self.Th_front, self.Kh, self.zeroDistCoeffs)
        imagePoints = imagePoints.reshape(-1, 2)
        print 'Th:', self.Th_front
        print 'No Rotate:', imagePoints
        print 'line du, dv', imagePoints[1] - imagePoints[0]
        print 'length:', np.linalg.norm(imagePoints[0] - imagePoints[1])
        print 'height:', np.linalg.norm(imagePoints[0] - imagePoints[3])
        print 'cross:', np.linalg.norm(imagePoints[0] - imagePoints[2])


    def test_my_project_points(self):
        fm = self.mod_recoverPose.projectPoints

        fx, fy, cx, cy = self.Kh[0][0], self.Kh[1][1], self.Kh[0][2], self.Kh[1][2]
        tvec = self.Th_front * -1
        rm = np.matrix(self.Rh_left)
        refPoints = self.map_corners
        rotPoints, imagePoints = fm(refPoints, rm, tvec, fx, fy, cx, cy)
        print 'tvec:', tvec
        print 'objPoints:', refPoints
        print 'rotPoints:', rotPoints
        print 'imagePoints:', imagePoints

    def test_project_points(self):
        imagePoints, jacobian = cv2.projectPoints(self.map_corners, self.UnitRv, self.Th_front, self.Kh, self.zeroDistCoeffs)
        print 'Th:', self.Th_front
        print 'Front:', imagePoints
        imagePoints, jacobian = cv2.projectPoints(self.map_corners2, self.UnitRv, self.Th_front2, self.Kh, self.zeroDistCoeffs)
        print 'Th2:', self.Th_front2
        print 'Front 2:', imagePoints
        imagePoints, jacobian = cv2.projectPoints(self.map_corners, self.Rv_yaw_10, self.Th_front, self.Kh, self.zeroDistCoeffs)
        print 'Rotate yaw 10:', imagePoints
        imagePoints, jacobian = cv2.projectPoints(self.map_corners, self.Rv_yaw_n10, self.Th_front, self.Kh, self.zeroDistCoeffs)
        print 'Rotate yaw -10:', imagePoints

        imagePoints, jacobian = cv2.projectPoints(self.map_corners, self.UnitRv, self.Th_left, self.Kh, self.zeroDistCoeffs)
        print 'Left:', imagePoints

    def test_find_pose(self):
        fn1, fn2 = 'images/world_map_front.jpg', 'images/world_map_left.jpg'
        H, kp_pairs = self.m_find_homography(fn1, fn2)
        print('H is ', H)

        tvec = self.Th_front * -1

        result = []
        x0 = 30
        for y0 in range(1000, -1000, -20):

            refPoints = np.float64([[-130, 30, 0], [30, -80, 0], [30, -330, 0], [-130, -310, 0], [x0, y0, 0]])
            # refPoints = self.map_corners

            refImagePoints, imagePoints = self.m_calculate_image_points(H, refPoints, self.Kh, tvec)
            # print('tvec is:', tvec)
            # print('Ref points:', refPoints)
            # print('Ref Image points:', refImagePoints)
            # print('Image points:', imagePoints)

            # Fix
            # imagePoints = imagePoints.reshape(-1, 2)
            # imagePoints[2][0] = imagePoints[0][0]
            # imagePoints[1][1] = imagePoints[0][1]
            # print('Fixed Image points:', imagePoints)

            fx, fy, cx, cy = self.Kh[0][0], self.Kh[1][1], self.Kh[0][2], self.Kh[1][2]
            dt = self.Th_front[2]
            x, y, z = self.m_find_pose(refPoints, imagePoints, self.Kh, tvec)
            # print ('x, y, z:', x, y, z )
            result.append('ref points is %s, dx, dz is %d, %d' % (refPoints[-1], x, z))
        print '\n'.join(result)

    def test_horizontal_center_line(self):
        fn1, fn2 = 'images/world_map_front.jpg', 'images/world_map_left.jpg'
        H, kp_pairs = self.m_find_homography(fn1, fn2)
        print('H is ', H)

        tvec = self.Th_front * -1

        refPoints = np.float64([[0, -120, 0], [0, -80, 0], [0, -140, 0], [0, -160, 0]])
        refImagePoints, imagePoints = self.m_calculate_image_points(H, refPoints, self.Kh, tvec)
        # print('tvec is:', tvec)
        # print('Ref points:', refPoints)
        # print('Ref Image points:', refImagePoints)
        # print('Image points:', imagePoints)

        # Fix
        # imagePoints = imagePoints.reshape(-1, 2)
        # imagePoints[2][0] = imagePoints[0][0]
        # imagePoints[1][1] = imagePoints[0][1]
        # print('Fixed Image points:', imagePoints)

        fx, fy, cx, cy = self.Kh[0][0], self.Kh[1][1], self.Kh[0][2], self.Kh[1][2]
        dt = self.Th_front[2]
        self.m_find_pose(refPoints, imagePoints, self.Kh, tvec)

    def test_unhomography(self):
        fm = self.mod_recoverPose.unhomography
        fn1, fn2 = 'images/world_map_front.jpg', 'images/world_map_left.jpg'
        H, kp_pairs = self.m_find_homography(fn1, fn2)

        n = 10
        pts1 = np.float64([kpp[0].pt for kpp in kp_pairs[:n]])
        pts2 = np.float64([kpp[1].pt for kpp in kp_pairs[:n]])

        points = np.int32(fm(H, pts2))
        for i in range(n):
            print pts1[i], pts2[i], points[i]

        w, h = HUAWEI_G520.width - 1, HUAWEI_G520.height - 1
        cx, cy = w / 2, h / 2
        imagePoints = np.float64([[0, 0],  [cx, 0],  [w, 0],
                                  [0, cy], [cx, cy], [w, cy],
                                  [0, h],  [cx, h],  [w, h]])
        points = np.int32(fm(H, imagePoints))
        n = imagePoints.shape[0]
        for i in range(n):
            print imagePoints[i], points[i]

    def test_unproject_homography_points(self):
        fm = self.mod_recoverPose.unproject_homography_points
        fn1, fn2 = 'images/world_map_front.jpg', 'images/world_map_left.jpg'
        H, kp_pairs = self.m_find_homography(fn1, fn2)

        w, h = HUAWEI_G520.width - 1, HUAWEI_G520.height - 1
        cx, cy = w / 2, h / 2
        imagePoints = np.float64([[0, 0],  [cx, 0],  [w, 0],
                                  [0, cy], [cx, cy], [w, cy],
                                  [0, h],  [cx, h],  [w, h]])
        tvec = np.float64([0, -130, -230])
        K = self.Kh
        t = -tvec[2]
        points = fm(imagePoints, H, K, tvec, t)
        print 'imagePoints:', imagePoints
        print 'objectPoints:', np.array(points, dtype=np.float64)

    def test_compose_rotation_matrix(self):
        fm = self.mod_recoverPose.compose_rotation_matrix

        pi = 3.1415926
        pitch, roll = pi / 4, pi / 2
        rm = fm(pitch=pitch)

        v = np.float64([0, 0, 1])
        print 'Pitch 45'
        print 'Excpeted: [ 0.         -0.70710677  0.70710679]'
        print v, ' => ', (rm * v.reshape(3, 1)).ravel()

        rm = fm(pitch=pitch, roll=roll)
        v = np.float64([0, 1, 0])
        # First pitch, then roll
        print 'Firt pitch 45, then roll 90'
        print 'Expected: [ -7.07106791e-01   1.89468536e-08   7.07106772e-01]'
        print v, ' => ', (rm * v.reshape(3, 1)).ravel()

    def test_find_pose_by_vertical_reference(self):
        fm = self.mod_recoverPose.find_pose_by_vertical_reference
        fn1, fn2 = 'images/world_map_front.jpg', 'images/world_map_left.jpg'
        H, kp_pairs = self.m_find_homography(fn1, fn2)
        t = self.Th_front[2]
        tvec = self.Th_front * -1
        Kr = Kc = self.Kh
        print 'Pos is ', fm(H, Kr, tvec, t, Kc)

    def test_find_pose_and_azimuth(self):
        fm = self.mod_recoverPose.find_pose_and_azimuth
        fn1, fn2 = 'images/world_map_front.jpg', 'images/world_map_left.jpg'
        H, kp_pairs = self.m_find_homography(fn1, fn2)
        t = self.Th_front[2]
        tvec = self.Th_front * -1
        Kr = Kc = self.Kh
        print 'Left pos is ', fm(H, Kr, tvec, t, Kc, pitch=None)

        # fn1, fn2 = 'images/world_map_front.jpg', 'images/world_map_right.jpg'
        # H, kp_pairs = self.m_find_homography(fn1, fn2)
        # print 'Right pos is ', fm(H, Kr, tvec, t, Kc)

    def test_recover_pose(self):
        fm = self.mod_recoverPose.recover_pose
        fn1, fn2 = 'images/world_map_front.jpg', 'images/world_map_left.jpg'
        H, kp_pairs = self.m_find_homography(fn1, fn2)
        r, t = fm(self.Kh, kp_pairs)
        print 'left map offset: dx, dy, dz:', (t * -1 * 100).ravel()

        fn1, fn2 = 'images/world_map_front.jpg', 'images/world_map_right.jpg'
        H, kp_pairs = self.m_find_homography(fn1, fn2)
        r, t = fm(self.Kh, kp_pairs)
        print 'right map offset: dx, dy, dz:', (t * -1 * 100).ravel()

        fn1, fn2 = 'test2/accuracy/2.JPG', 'test2/accuracy/1.JPG'
        H, kp_pairs = self.m_find_homography(fn1, fn2)
        r, t = fm(self.Ki, kp_pairs)
        print 'picture 1 offset 2: dx, dy, dz:', (t * -1 * 100).ravel()

        fn1, fn2 = 'test2/accuracy/2.JPG', 'test2/accuracy/5.JPG'
        H, kp_pairs = self.m_find_homography(fn1, fn2)
        r, t = fm(self.Ki, kp_pairs)
        print 'picture 5 offset 1: dx, dy, dz:', (t * -1 * 100).ravel()

        fn1, fn2 = 'test2/accuracy/2.JPG', 'test2/accuracy/6.JPG'
        H, kp_pairs = self.m_find_homography(fn1, fn2)
        r, t = fm(self.Ki, kp_pairs)
        print 'picture 6 offset 1: dx, dy, dz:', (t * -1 * 100).ravel()

    def test_unproject_points(self):
        fm = self.mod_recoverPose.unprojectPoints
        fn1, fn2 = 'images/world_map_front.jpg', 'images/world_map_left.jpg'
        H, kp_pairs = self.m_find_homography(fn1, fn2)

        tvec = np.float64([0, -130, -230])
        K = self.Kh
        t = -tvec[2]

        imagePoints = np.float64([kpp[0].pt for kpp in kp_pairs])
        points = fm(imagePoints, K, tvec, t)
        n = imagePoints.shape[0]

        for i in range(n):
            print imagePoints[i], '=>', points[i]

        tvec1 = np.float64([-120, -120, -340])
        rm = self.mod_recoverPose.compose_rotation_matrix(yaw=-0.38, pitch=0, roll=0)
        rotatePoints, imageTestPoints = self.projectPoints(self.Kh, rm, tvec1, points)
        imagePoints = np.float64([kpp[1].pt for kpp in kp_pairs])
        for i in range(n):
            print np.int32(imagePoints[i]), ':', np.int32(imageTestPoints[i]), ':', int(kp_pairs[i][1].angle)

    def test_find_pose_with_yaw(self):
        fm = self.mod_recoverPose.find_pose_with_yaw
        fn1, fn2 = 'images/world_map_front.jpg', 'images/world_map_left.jpg'
        H, kp_pairs = self.m_find_homography(fn1, fn2)

        tvec = np.float64([0, 0, 0])
        K = self.Kh
        t = 230
        points = np.float64([kpp[0].pt for kpp in kp_pairs])
        refPoints = self.mod_recoverPose.unprojectPoints(points, K, tvec, t)

        imagePoints = np.float64([kpp[1].pt for kpp in kp_pairs])
        yaw = -0.38
        n = imagePoints.shape[0]

        # delta = 100        
        # cx, cy = K[0][2], K[1][2]
        # sx0, sy0, sz0 = 0, 0, 0
        # counter = 0
        # for i in range(n):
        #     du, dv = imagePoints[i] - (cx, cy)
        #     if np.abs(du) > delta and np.abs(dv) > delta:
        #         continue
        #     for j in range(n):
        #         du, dv = imagePoints[i] - imagePoints[j]
        #         if np.abs(du) > delta and np.abs(dv) > delta:
        #             break
        #     p1 = np.array([refPoints[i], refPoints[j]])
        #     p2 = np.array([imagePoints[i], imagePoints[j]])
        #     dx, dy, dz = fm(p1, p2, K, tvec, yaw)
        #     print i, j, dx, dy, dz
        #     if dy < -100:
        #          print p1, p2
        #     counter += 1
        #     sx0 += dx
        #     sy0 += dy
        #     sz0 += dz
        # print 'avg dx, dy:', sx0 / counter, sy0 / counter, sz0 / counter

        # for i in range(n):
        #     j = (i + 10) % n
        #     p1 = np.array([refPoints[i], refPoints[j]])
        #     p2 = np.array([imagePoints[i], imagePoints[j]])
        #     dx, dy = fm(p1, p2, K, tvec, yaw)
        #     print i, j, dx, dy
        #     if dx < -80:
        #         print p2
        yaw, vt = self.mod_recoverPose.solve_pnp(refPoints, imagePoints, K)
        print 'solve pnp say ', yaw, vt.ravel()

    def test_same_k_find_pose_with_yaw(self):
        fm = self.mod_recoverPose.find_pose_with_yaw
        fn1, fn2 = 'images/world_map_front.jpg', 'images/world_map_left.jpg'
        H, kp_pairs = self.m_find_homography(fn1, fn2)

        yaw = -0.38
        tvec = np.float64([0, 0, 0])
        K = self.Kh
        t = 230
        fx, fy, cx, cy = K[0][0], K[1][1], K[0][2], K[1][2]
        n = 100

        # Left-Up corner
        u0, v0 = 0, 0        
        u1, u2 = 10, cx / 2
        v1, v2 = 10, cy / 2

        # Right-Up corner
        # u0, v0 = 0, cy * 2
        # u1, u2 = cx * 0.75, cx * 2
        # v1, v2 = cy * 0.75, cy * 2

        du, dv = (u2 - u1) / n, (v2 - v1) / n
        imageRowPoints = np.insert(np.arange(u1, u2, du).reshape(-1, 1), 1, v0, axis=1)
        imageColPoints = np.insert(np.arange(v1, v2, dv).reshape(-1, 1), 0, u0, axis=1)
        
        refRowPoints = self.mod_recoverPose.unproject_homography_points(imageRowPoints, H, K, tvec, t)
        refColPoints = self.mod_recoverPose.unproject_homography_points(imageColPoints, H, K, tvec, t)

        # print imageRowPoints
        # print imageColPoints
        # print refRowPoints
        # print refColPoints

        for i in range(n):
            p1 = np.array([refRowPoints[i], refColPoints[i]])
            p2 = np.array([imageRowPoints[i], imageColPoints[i]])
            dx, dy, dz = fm(p1, p2, K, tvec, yaw)
            print i, dx, dy, dz

    def test_coffee_same_k_find_pose_with_yaw(self):
        fm = self.mod_recoverPose.find_pose_with_yaw
        hdata = 'images/coffee_match.data'
        self.assertTrue(os.path.exists(hdata), 'No coffee_match.data')
        with open(hdata, 'rb') as f:
            H, kp_data = pickle.load(f)

        yaw = 0.49
        tvec = np.float64([0, 0, 0])
        K = self.Ki
        t = 250
        fx, fy, cx, cy = K[0][0], K[1][1], K[0][2], K[1][2]
        n = 100

        # Left-Up corner
        u0, v0 = 0, 0        
        u1, u2 = 10, cx / 2
        v1, v2 = 10, cy / 2

        # Right-Up corner
        u0, v0 = 0, cy * 2
        u1, u2 = cx * 0.75, cx * 2
        v1, v2 = cy * 0.75, cy * 2

        du, dv = (u2 - u1) / n, (v2 - v1) / n
        imageRowPoints = np.insert(np.arange(u1, u2, du).reshape(-1, 1), 1, v0, axis=1)
        imageColPoints = np.insert(np.arange(v1, v2, dv).reshape(-1, 1), 0, u0, axis=1)
        
        refRowPoints = self.mod_recoverPose.unproject_homography_points(imageRowPoints, H, K, tvec, t)
        refColPoints = self.mod_recoverPose.unproject_homography_points(imageColPoints, H, K, tvec, t)

        # print imageRowPoints
        # print imageColPoints
        # print refRowPoints
        # print refColPoints

        for i in range(n):
            p1 = np.array([refRowPoints[i], refColPoints[i]])
            p2 = np.array([imageRowPoints[i], imageColPoints[i]])
            dx, dy, dz = fm(p1, p2, K, tvec, yaw)
            print i, dx, dy, dz

    def test_solve_pnp_ransas(self):
        fm = self.mod_recoverPose.solve_pnp_ransac
        fn1, fn2 = 'images/world_map_front.jpg', 'images/world_map_right.jpg'
        H, kp_pairs = self.m_find_homography(fn1, fn2)

        tvec = np.float64([0, 0, 0])
        K = self.Kh
        t = 230
        points = np.float64([kpp[0].pt for kpp in kp_pairs])
        refPoints = self.mod_recoverPose.unprojectPoints(points, K, tvec, t)
        imagePoints = np.float64([kpp[1].pt for kpp in kp_pairs])
        rt, vt = fm(refPoints, imagePoints, K)
        print 'solve pnp ransac say ', vt.ravel()
        rt, vt = self.mod_recoverPose.solve_pnp(refPoints, imagePoints, K)
        print 'solve pnp say ', vt.ravel()

    def test_coffee_find_pose_with_yaw(self):
        fm = self.mod_recoverPose.find_pose_with_yaw
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

        tvec = np.float64([0, 0, 0])
        K = self.Ki
        t = 250
        points = np.float64([kpp[0] for kpp in kp_data])
        refPoints = self.mod_recoverPose.unprojectPoints(points, K, tvec, t)
        imagePoints = np.float64([kpp[1] for kpp in kp_data])

        # for i in range(refPoints.shape[0]):
        for i in range(10):
            print points[i], ':', imagePoints[i], '=>', refPoints[i]

        yaw, vt = self.mod_recoverPose.solve_pnp(refPoints, imagePoints, K)
        print 'solve pnp say ', yaw, vt.ravel()
        # rt, vt = self.mod_recoverPose.solve_pnp_ransac(refPoints, imagePoints, K)
        # print 'solve pnp ransac say ', vt.ravel()

        # n = imagePoints.shape[0]
        # yaw = 0.49
        # tvec = np.float32([0, -120, -250])
        # delta = 100
        # cx, cy = K[0][2], K[1][2]
        # sx0, sy0, sz0 = 0, 0, 0
        # counter = 0
        # for i in range(n):
        #     du, dv = imagePoints[i] - (cx, cy)
        #     if np.abs(du) < delta or np.abs(dv) < delta:
        #         continue
        #     for j in range(n):
        #         du, dv = imagePoints[i] - imagePoints[j]
        #         if np.abs(du) > delta and np.abs(dv) > delta:
        #             du, dv = imagePoints[j] - (cx, cy)
        #             if np.abs(du) > delta and np.abs(dv) > delta:
        #                 break
        #     p1 = np.array([refPoints[i], refPoints[j]])
        #     p2 = np.array([imagePoints[i], imagePoints[j]])
        #     dx, dy, dz = fm(p1, p2, K, tvec, yaw)
        #     print i, j, dx, dy, dz
        #     # if dy > 80:
        #     #     print p1, p2
        #     counter += 1
        #     sx0 += dx
        #     sy0 += dy
        #     sz0 += dz
        # print 'avg dx, dy, dz:', sx0 / counter, sy0 / counter, sz0 / counter

    def test_produce_left_data(self):
        # fm = self.mod_recoverPose.find_pose_with_yaw
        fn1, fn2 = 'images/world_map_front.jpg', 'images/world_map_left.jpg'
        H, kp_pairs = self.m_find_homography(fn1, fn2)

        K = self.Kh
        fx, fy, cx, cy = K[0][0], K[1][1], K[0][2], K[1][2]
        tvec = np.float64([0, -130, -230])
        t = -tvec[2]

        tvec2 = np.float64([-120, -120, -340])
        yaw = -0.38
        rm = self.mod_recoverPose.compose_rotation_matrix(yaw=yaw)

        step = 20
        z = 0
        # rows = np.arange(-500, 500, step, dtype=np.float32).reshape(-1, 1)
        # for col in np.arange(-600, 400, step, dtype=np.float32):
        #     points = np.insert(np.insert(rows, 1, col, axis=1), 2, z, axis=1)
        #     _x, A = self.mod_recoverPose.calculate_image_points(H, points, K, tvec)
        #     _x, B = self.mod_recoverPose.projectPoints(points, rm, tvec, fx, fy, cx, cy)
        #     _x, C = self.mod_recoverPose.projectPoints(points, rm, tvec2, fx, fy, cx, cy)
        #     for i in range(points.shape[0]):
        #         print points[i], A[i], B[i], C[i]

        cols = np.arange(-600, 400, step, dtype=np.float32).reshape(-1, 1)
        x = 0
        points = np.insert(np.insert(cols, 0, x, axis=1), 2, z, axis=1)
        _x, A = self.mod_recoverPose.calculate_image_points(H, points, K, tvec)
        _x, B = self.mod_recoverPose.projectPoints(points, rm, tvec, fx, fy, cx, cy)
        _x, C = self.mod_recoverPose.projectPoints(points, rm, tvec2, fx, fy, cx, cy)

        print 'x is', x
        for i in range(points.shape[0]):
            print i, ':', points[i]
            print A[i], C[i]
            print 'A - C:', np.int32(A[i] - C[i]).ravel()
            print

if __name__ == '__main__':
    sys.path.insert(0, __src_path__)

    loader = unittest.TestLoader()
    loader.testMethodPrefix = 'test_recover_pose'
    suite = loader.loadTestsFromTestCase(RecoverPoseTestCases)
    unittest.TextTestRunner(verbosity=2).run(suite)
