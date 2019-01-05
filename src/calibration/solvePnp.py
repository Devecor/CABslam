# -*- coding: utf-8 -*-
#

import numpy as np
import cv2

def rotation_matrix(angle, axis='y'):
    '''根据旋转弧度和坐标轴返回对应的旋转矩阵。
    关于旋转方向，以 Y 轴为例，Z->X 为正，反之为负。
    '''
    ca = np.cos(angle)
    sa = np.sin(angle)
    axis = axis.lower()
    m = np.float64([[1,  0,   0],
                    [0,  ca, -sa],
                    [0,  sa,  ca]]) if axis == 'x' else \
        np.float64([[ca,  0, sa],
                    [0,   1, 0],
                    [-sa, 0, ca]]) if axis == 'y' else \
        np.float32([[ca, -sa, 0],
                    [sa,  ca, 0],
                    [0,   0,  1]])
    return np.matrix(m)

def compose_rotation_matrix(yaw=None, pitch=None, roll=None):
    '''首先 yaw，绕 Y 轴旋转，然后 pitch，绕 X 轴旋转，最后是 roll，绕
    Z 轴旋转。
    '''
    rm = np.matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float64)
    if roll is not None:
        rm *= rotation_matrix(roll, axis='z')
    if pitch is not None:
        rm *= rotation_matrix(pitch, axis='x')
    if yaw is not None:
        rm *= rotation_matrix(yaw, axis='y')
    return rm

def unproject_image_points(imagePoints, K, t):
    '''转换当前照片像素点坐标为对应的空间坐标

    imagePoints   当前相片对应的像素点坐标
    K             相机内部参数
    t             参考平面和相机的距离，两个平面是水平关系

    计算方法，

    使用相机的内参矩阵和相机位置，将照片的像素坐标转换成为对应的空间坐
    标，不考虑旋转矩阵

    相机必须和被拍摄的平面水平，否则下面的公式并不适用。

    '''
    fx, fy, cx, cy = K[0][0], K[1][1], K[0][2], K[1][2]
    results = np.float64([[t * (p[0] - cx) / fx, t * (p[1] - cy) / fy ] for p in imagePoints])
    return np.insert(results, 2, t, axis=1)

def decompose_homography(K, H):
    '''opencv 中的相机定位方法，参考相机和当前相机内参必须一致

    K 相机内参，
    H Homography 矩阵

    返回结果
    rotations	Array of rotation matrices.
    translations	Array of translation matrices.
    normals	Array of plane normal matrices.

    This function extracts relative camera motion between two views
    observing a planar object from the homography H induced by the
    plane. The intrinsic camera matrix K must also be provided. The
    function may return up to four mathematical solution sets. At
    least two of the solutions may further be invalidated if point
    correspondences are available by applying positive depth
    constraint (all points must be in front of the camera). The
    decomposition method is described in detail in [104] .
    '''
    retval, rotations, translations, normals = cv2.decomposeHomographyMat(H, K)
    return rotations, translations, normals

def decompose_essential(K, kp_pairs):
    '''opencv 中的相机定位方法，参考相机和当前相机内参必须一致

    K         相机内参
    kp_paris  参考照片和当前照片中匹配像素坐标

    返回结果
    R1	One possible rotation matrix.
    R2	Another possible rotation matrix.
    t	One possible translation.

    This function decompose an essential matrix E using svd
    decomposition [66] . Generally 4 possible poses exists for a given
    E. They are [R1,t], [R1,−t], [R2,t], [R2,−t]. By decomposing E,
    you can only get the direction of the translation, so the function
    returns unit t.
    '''

    pts1 = np.float64([kpp[0].pt for kpp in kp_pairs])
    pts2 = np.float64([kpp[1].pt for kpp in kp_pairs])

    E, mask = cv2.findEssentialMat(pts1, pts2, K)
    R1, R2, t = cv2.decomposeEssentialMat(E)
    return R1, R2, t

def recover_pose(K, kp_pairs):
    '''opencv 中的相机定位方法，参考相机和当前相机内参必须一致

    K         相机内参
    kp_pairs  参考照片和当前照片中匹配像素坐标

    返回结果
    R	Recovered relative rotation.
    t	Recoverd relative translation.
    '''

    pts1 = np.float64([kpp[0].pt for kpp in kp_pairs])
    pts2 = np.float64([kpp[1].pt for kpp in kp_pairs])

    E, mask = cv2.findEssentialMat(pts1, pts2, K)
    retval, R, t, mask = cv2.recoverPose(E, pts1, pts2, K)
    return R, t

def solve_pnp(objPoints, imagePoints, K, dist_coef=None):
    '''调用opencv中的函数 solvePnP 进行相机定位。

    objPoints      参考点三维坐标
    imagePoints    参考点在当前照片中对应的像素坐标
    K              当前相机内参
    dist_coef      当前相机畸变系数

    返回相机的方位角和参考相机之间的位移
    
        yaw       正值表示当前相机顺时针方向旋转到参考相机的角度
                  负值表示当前相机逆时针方向旋转到参考相机的角度
                  yaw 范围为 正负 pi / 2
                  
        tvec      当前相机到参考相机的位移量，也就是说，参考相机
                  的位置减去 tvec 就是当前相机的位置

    参考点的三维坐标系选择的不同，对结果应该不影响，但是实际上会造成不
    同的结果（尚未详细测试），所以当前参考点的三维坐标系选择以参考相机
    的位置为原点的相机坐标系进行计算。
    '''
    if dist_coef is None:
        dist_coef = np.zeros(4)
    rvec, tvec = np.zeros(3, dtype=np.float64), np.zeros(3, dtype=np.float64)
    useExtrinsicGuess = False
    flags = cv2.SOLVEPNP_ITERATIVE  # cv2.SOLVEPNP_EPNP
    ret, rvec, tvec = cv2.solvePnP(objPoints, imagePoints, K, dist_coef, rvec, tvec, useExtrinsicGuess, flags)
    rmat = np.matrix(cv2.Rodrigues(rvec)[0])
    dt = np.linalg.inv(rmat) * tvec.reshape(3, 1)
    nv = rmat * np.float64([0, 0, 1]).reshape(3, 1)
    yaw = np.arctan2(nv[0], nv[2])
    # return yaw, dt.A.ravel()
    return yaw, tvec.ravel()

def solve_pnp_ransac(objPoints, imagePoints, K, dist_coef=None):
    if dist_coef is None:
        dist_coef = np.zeros(4)
    rvec, tvec = np.zeros(3, dtype=np.float64), np.zeros(3, dtype=np.float64)
    useExtrinsicGuess = False
    iterationsCount = 100
    reprojectionError = 10.0
    confidence = 0.99
    inliers = None
    flags = cv2.SOLVEPNP_ITERATIVE
    ret, rvec, tvec, inliers = cv2.solvePnPRansac(
        objPoints, imagePoints, K, dist_coef, rvec, tvec,
        useExtrinsicGuess, iterationsCount, reprojectionError,
        confidence, inliers, flags
        )
    return rvec.ravel(), tvec.ravel()
