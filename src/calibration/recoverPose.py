# -*- coding: utf-8 -*-
#
# ！！！ 这个文件不再使用，属于前期的探索性代码，已经完成使命。
# ！！！ 保留于此，以作纪念。
# 
# About pinhole camera model
#
# Refer to http://docs.opencv.org/3.2.0/d9/d0c/group__calib3d.html#ga54a2f5b3f8aeaf6c76d4a31dece85d5d
#
# 对于每一种型号的手机来说，它的图像传感器尺寸是固定的。对于照片焦距的
# 信息，我们一般可以通过照片的EXIF信息获取。（如果手机相机的焦距是固定
# 的，那么也可以根据手机型号得到焦距信息）。
#
# 所以对于手机照片来说，它的相机内参
#
#     [   fx     0      cx   ]
#     [   0      fy     cy   ]
#     [   0      0       1   ]
#
# 是已知的。
#
# 为了简化起见，我们暂不考虑相机的畸变，参考照片的拍摄角度总是在正前方，
# 并且假定相机拍摄的时候总是保持竖直（没有俯拍或者仰拍）。那么，我们据
# 此来推导根据参考照片来快速和精确的确定当前照片的拍摄位置的一种算法。
#
# 我们的世界坐标系以正东方向为 X轴 正方向，正北方向为 Z 轴 正方向，正下
# 方为 Y轴 正方向（主要是为了和针孔相机模型坐标系保持一致）；
#
# 坐标原点任意选择一个参考点即可。
#
# 手机拍照的角度以正北方向为 0 度，向东为 90 度，向西为 -90度。
#
# 已知信息：
#
#     参考照片使用相机的内部参数 Kr
#     参考照片的拍摄位置 Tr ( xr, yr, zr )
#     参考照片和相机的距离 Dr
#     参考照片拍摄时相机的方向（参考系以正北方向为 0 度）Ar
#     参考照片
#
# 传入参数：
#
#     当前照片使用的相机内部参数 Kc
#     当前照片
#
# 传出参数：
#
#     当前照片的拍摄位置 Tc （xc, yc, zc )
#
# 计算方法：
#
#     * 获得当前照片和参考照片对应的 Homography 矩阵
#
#     使用 orb 算法查找两幅图片的KP，并使用 flann 算法进行匹配；
#
#     如果无法找到足够的匹配点，则基于 orb 在使用 asift 算法进行匹配；
#     asift 算法比较慢，但是对于不同角度的照片，能够匹配 orb 算法无法匹
#     配的照片；
#
#     根据两幅照片匹配的KP，计算出两幅照片之间的 Homography 矩阵 H，H
#     满足下列的等式
#
#          (uc, vc, 1) = H * (ur, vr, 1)
#
#     其中 (uc, vc, 1) 是当前照片的像素点坐标，(ur, vr, 1) 是参考照片中
#     对应的像素点， H 是 3x3 的矩阵。
#
#     传统的算法根据 Homography 矩阵直接分解得到当前照片拍摄时相机的姿
#     态，相对于拍摄参考照片时相机的旋转和偏移，一般会有多组可能的结果，
#     需要根据一些约束进行筛选，并且结果往往不太精确。而对于我们来说，
#     主要应用于手机定位，并进行了相关约束，可以简化这个计算过程，并且
#     大幅度的提高定位的精度。
#
#     根据针孔相机模型，当 z 不为 0 时，我们有下列等式（参考上面的针孔
#     相机模型）：
#
#         [ x ]            [ X ]
#         | y |   =  R  *  | Y |  +  T
#         [ z ]            [ Z ]
#         x' = x / z
#         y' = y / z
#         u  = fx∗* x'′+ cx
#         v  = fy∗* y'′+ cy
#
#     其中 R 是相机旋转矩阵，T 是相机位置
#          u, v 是像素坐标
#          fx, fy 是相机焦距参数
#          cx，cy 是相机中心位置
#
#     由于我们限定了手机相机只绕 Z 轴进行旋转，那么旋转 a 度对应的
#     旋转矩阵为
#
#           [  cos(a)      -sin(a)      0  ]
#           |  sin(a)       cos(a)      0  |
#           [  0            0           1  ]
#
#     * 计算当前照片和参考照片的拍摄角度差值
#
#     在拍摄参考平面上选取两个点 P1, P2，最好是水平方向的，然后分别计算
#     得到在参考照片对应的像素坐标 M1, M2, 以及当前照片对应的像素坐标
#     MC1, MC2，计算两条线段的夹角就是前后拍摄照片的角度。
#
#     * 计算当前照片拍摄的距离
#
#     使用当前相机对应的内参、旋转角度和参考照片拍摄位置，计算两个参考
#     点的像素坐标，并计算出其对应的欧几里得长度 s1
#
#     使用 Homography 矩阵，计算出两个参考点在当前照片中的像素坐标，计
#     算对应的欧几里得长度 s2
#
#     那么，根据针孔相机模型，有下列关系成立
#
#           s1 * d1 = s2 * d2
#
#     其中 d1，d2 分别是拍摄距离，因为 d1 是已知的，我们可以得到当前照
#     片的拍摄距离
#
#           d2 = s1 * d1 / s2
#
#     * 计算拍摄点偏移量
#
#     * 计算拍摄点坐标
#
#       根据参考照片的拍摄点以及参考照片的角度来确定。
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
    '''
    '''
    if dist_coef is None:
        dist_coef = np.zeros(4)
    rvec, tvec = np.zeros(3, dtype=np.float64), np.zeros(3, dtype=np.float64)
    useExtrinsicGuess = False
    flags = cv2.SOLVEPNP_ITERATIVE
    ret, rvec, tvec = cv2.solvePnP(objPoints, imagePoints, K, dist_coef, rvec, tvec, useExtrinsicGuess, flags)
    rmat = np.matrix(cv2.Rodrigues(rvec)[0])
    dt = np.linalg.inv(rmat) * tvec.reshape(3, 1)
    nv = rmat * np.float64([0, 0, 1]).reshape(3, 1)
    yaw = np.arctan2(nv[0], nv[2]) * 180 / np.pi
    return yaw, dt.ravel()

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

def calculate_camera_offset_by_uv_offset(t, du, dv, fx, fy, xt=0, yt=0, zt=0):
    '''根据两张照片中同一个对象的像素偏移量来计算对应的相机拍摄位置偏移，
    假设相机没有旋转，前后两次没有缩放，并且暂不考虑相机畸变。

    t 是相机和拍摄参考物的距离
    du, dv 是像素偏移量
    fx, fy, cx, cy 是相机参数
    xt, yt, zt 是第一次拍摄的位置坐标

    返回第二次拍摄时相机的位置坐标 X, Y, Z，因为后两次拍摄的照片没有缩
    放，也就是 Z = zt，实际上需要计算的只有 X, Y 两个值而已。

    因为相机没有旋转，所有旋转矩阵为单位矩阵，且不考虑畸变，任取一个点
    (x0, y0, z0), 其前后两次拍摄对应的像素坐标分别为 （u1, v1) 和
    （u2, v2), 根据针孔相机模型，有下列等式成立

        u1 = fx * ( x0 - xt ) / ( z0 - zt )
        v1 = fy * ( y0 - yt ) / ( z0 - zt )

        u2 = fx * ( x0 - X ) / ( z0 - zt )
        v2 = fy * ( y0 - Y ) / ( z0 - zt )

        du = u2 - u1 = fx * ( ( x0 - xt ) / ( z0 - zt ) - ( x0 - X ) / ( z0 - zt ) ) = fx * ( X - xt ) / ( z0 - zt )
        dv = v2 - v1 = fy * ( ( y0 - yt ) / ( z0 - zt ) - ( y0 - Y ) / ( z0 - zt ) ) = fy * ( Y - yt ) / ( z0 - zt )

    其中 z0 - zt 就是相机和拍摄参考物的距离 t，代入上面的等式，得到

        du * t = fx * ( X - xt )
        dv * t = fy * ( Y - yt )

    于是

        X = du * t / fx + xt
        Y = dv * t / fy + yt

    '''
    return du * t / fx + xt, dv * t / fy + yt, zt

def projectPoints(objPoints, rm, tvec, fx, fy, cx, cy):
    '''计算对象坐标映射到像素坐标。

    fx, fy, cx, cy  相机内参
    rm              旋转矩阵
    tvec            相机位置
    objPoints       需要转换的三维点

    '''
    refPoints = objPoints - tvec
    rotPoints = np.array([(rm * p.reshape(3, 1)).A.reshape(-1) for p in refPoints.reshape(-1, 3)])
    imagePoints = np.array([[p[0] * fx + cx, p[1] * fy + cy]
                            for p in cv2.convertPointsFromHomogeneous(rotPoints).reshape(-1, 2)])
    return rotPoints, imagePoints

def unprojectPoints(imagePoints, K, tvec, t):
    '''转换当前照片像素点坐标为对应的空间坐标

    imagePoints   当前相片对应的像素点坐标
    K             相机内部参数
    tvec          相机位置
    t             参考平面和相机的距离，两个平面是水平关系

    计算方法，

    使用相机的内参矩阵和相机位置，将照片的像素坐标转换成为对应的空间坐
    标，不考虑旋转矩阵

    相机必须和被拍摄的平面水平，否则下面的公式并不适用。

    '''
    fx, fy, cx, cy = K[0][0], K[1][1], K[0][2], K[1][2]
    results = np.float64([[t * (p[0] - cx) / fx, t * (p[1] - cy) / fy ] for p in imagePoints])
    return np.insert(results, 2, t, axis=1) + tvec

def calculate_image_points(H, refPoints, cameraMatrix, tvec):
    '''计算参考点在当前照片的像素坐标。

    传入参数：
        H            Homography 转换矩阵
        refPoints    参考点，三维坐标
        cameraMatrix 参考照片相机的内部参数
        tvec         参考相机位置坐标

    返回 参考照片像素坐标，当前照片对应的像素坐标

    计算方法如下，首先根据参考相机的内参，将三维对象坐标转换成为参考照
    片上像素坐标，注意这里我们以相机拍摄位置为参考原点，并且假定相机正
    对着参考照片，没有旋转。

    得到参考照片的像素坐标之后，在使用 Homography 转换矩阵转换成为当前
    照片对应的像素坐标。
    '''
    rvec = np.zeros(3)
    distCoeffs = np.zeros(4)
    imagePoints, jacobian = cv2.projectPoints(refPoints, rvec, tvec * -1, cameraMatrix, distCoeffs)
    return imagePoints, cv2.perspectiveTransform(imagePoints, H)

def unhomography(H, imagePoints):
    '''使用 Homography 的逆反矩阵将当前照片的像素转换成为参考照片的像素
    坐标。
    '''
    HI = np.linalg.inv(np.matrix(H))
    return cv2.perspectiveTransform(imagePoints.reshape(1, -1, 2), HI.A).reshape(-1, 2)

def unproject_homography_points(imagePoints, H, K, tvec, t):
    '''转换当前照片像素点坐标为对应的空间坐标

    imagePoints   当前相片对应的像素点坐标
    H             Homography 矩阵
    K             参考相机内部参数
    tvec          参考相机位置
    t             参考平面和相机的距离，两个平面是水平关系

    计算方法，

    1. 使用 Homography 的逆反矩阵把当前照片的像素坐标转换成为参考照片对
       应的像素坐标

    2. 使用参考相机的内参矩阵和相机位置，将参考照片的像素坐标转换成为对
       应的空间坐标，参考相机不需要考虑旋转矩阵，因为我们是以参考相机的
       姿态作为参考，来表示当前相机的旋转的。

       并且参考相机必须和被拍摄的平面水平，否则下面的公式并不适用。

    '''
    # points = np.insert(np.float64(unhomography(H, imagePoints)), 2, 1.0, axis=1)
    # KI = np.linalg.inv(np.matrix(K))
    # return np.float64([(KI * p.reshape(3, 1)).A.reshape(-1) for p in points]) + tvec.reshape(-1)

    # 矩阵运算搞不定，我自己算还不行嘛
    fx, fy, cx, cy = K[0][0], K[1][1], K[0][2], K[1][2]
    results = np.float64([
            [t * (p[0] - cx) / fx, t * (p[1] - cy) / fy ] for p in unhomography(H, imagePoints)
            ])
    return np.insert(results, 2, t, axis=1) + tvec

def find_pose_by_yaw_pitch_roll():
    '''根据参考照片，在当前相机的空间姿态已知的情况下，计算当前相机的位置的一种算法。

    '''
    pass

def find_pose_with_yaw(objectPoints, imagePoints, cameraMatrix, tvec, yaw):
    '''计算当前相机的拍摄位置，以参考照片拍摄地点为坐标原点作为参考坐标系。

    传入参数：
        objectPoints 参考点的空间三维坐标
        imagePoints  参考点在当前照片对应的像素坐标
        cameraMatrix 当前相机的内部参数
        tvec         参考相机的位置
        yaw          当前相机的水平方位角

    返回当前相机的拍摄位置

    '''
    assert objectPoints.shape[0] == imagePoints.shape[0] == 2

    # 根据像素坐标偏移计算相机位置偏移
    fx, fy, cx, cy = cameraMatrix[0][0], cameraMatrix[1][1], cameraMatrix[0][2], cameraMatrix[1][2]

    rmat = compose_rotation_matrix(yaw=yaw)

    # 计算旋转相机水平方位角为 yaw 之后，在参考位置拍摄得到的像素坐标
    refPoints, refImagePoints = projectPoints(objectPoints, rmat, tvec, fx, fy, cx, cy)

    u, v = np.split((imagePoints - (cx, cy)) * (fy, fx), 2)
    k = u.ravel() / v.ravel()
    dx, dy = np.linalg.solve(
        np.insert(k.reshape(-1, 1), 0, -1, axis=1),
        -1 * refPoints.T[0] + k * refPoints.T[1]
        )
    um = imagePoints.T[0] - cx
    dz = np.average(((um * refPoints.T[2] - fx * (refPoints.T[0] - dx)) / um).ravel())
    return dx, dy, dz

def find_azimuth(objectPoints, imagePoints, fx, fy, cx, cy):
    k1, k2, k3 = [p[0] / p[1] for p in (imagePoints - (cx, cy)) * (fy, fx)]
    x1, y1, z1 = objectPoints[0]
    x2, y2, z2 = objectPoints[1]
    x3, y3, z3 = objectPoints[2]

    dy = (k1 * y1 * (x3 - x2) - k3 * y3 * (x1 - x2)) / (k1 * (x3 - x2) - k3 * (x1 - x2))
    value = (k1 * (y1 - dy) - k3 * (y3 - dy)) / (x1 - x3)
    if np.abs(value) > 1:
        return None, None, None
    a = np.arccos(value)  - np.pi / 2
    return dy, value, a

def find_pose_and_azimuth(H, Kr, tvec, t, Kc, pitch=None, roll=None):
    '''根据参考照片定位当前相机所在的位置，当前相机的仰角和旋转已知。

    H          Homography 矩阵
    Kr         参考相机内参
    tvec       参考相机位置
    t          参考相机和参考照片之间的距离，照片和参考面平行
    Kc         当前相机内参
    pitch      当前相机仰角
    roll       当前相机旋转角度

    返回当前相机位置

    '''
    # 当前照片参考点像素坐标： 左上角，上边中点，右上角
    fx, fy, cx, cy = Kc[0][0], Kc[1][1], Kc[0][2], Kc[1][2]
    imagePoints = np.float64([[0, 0], [cx, 0], [cx * 2, 0]])
    imagePoints = np.float64([[-2 * cx, 0], [0, 0], [cx * 2, 0]])
    imagePoints = np.float64([[0, cy/2], [cx, cy/2], [cx * 2, cy/2]])

    # 参考点对应的空间坐标
    objectPoints = unproject_homography_points(imagePoints, H, Kr, tvec, t)

    # 假设当前相机位于参考位置，使用已知的仰角和旋转，计算相应的旋转后
    # 的空间坐标和对应的像素坐标，我们称这个相机为虚拟相机和虚拟照片
    rmat = compose_rotation_matrix(pitch=pitch, roll=roll)
    refObjectPoints, refImagePoints = projectPoints(objectPoints, rmat, tvec, fx, fy, cx, cy)

    # 虚拟相机和当前相机的姿态仅仅就是水平方位角的差别，那么，虚拟坐标
    # 系中空间点 P0 ( x0, y0, z0 ) 在当前相机坐标系为 P
    #
    #     x0' = x0 * cos(a) + z0 * sin(a) + dx
    #     y0' = y0 + dy
    #     z0' = -x0 * sin(a) + z0 * cos(a) + dz
    #
    # 其中
    #
    #     dx, dy, dz 是当前相机和虚拟相机之间的偏移量
    #
    #     a 是当前相机相对于虚拟相机的水平旋转角度，相机坐标系垂直方向
    #     是 Y 轴，根据绕坐标轴旋转公式得出上面的等式
    #
    #
    # 根据针孔相机成像模型公式
    #
    #     u = fx * x / z + cx      ===>   (u - cx) / fx = x / z
    #     v = fx * y / z + cy      ===>   (v - cy) / fy = y / z
    #
    # 我们可以得到空间坐标点 P 在当前照片像素坐标为
    #
    #
    #    u0' - cx   fx * (x0 * cos(a) + z0 * sin(a) + dx)
    #    -------- = -------------------------------------
    #       fx        -x0 * sin(a) + z0 * cos(a) + dz
    #
    #
    #    v0' - cy               y0 + dy
    #    -------- = -------------------------------------
    #       fy        -x0 * sin(a) + z0 * cos(a) + dz
    #
    #
    # 然后让两个公式相除，得到
    #
    #     ( u0' - cx )   fy   x0 * cos(a) + z0 * sin(a) + dx
    #     ------------ * -- = ------------------------------
    #     ( v0' - cy )   fx            y0 + dy
    #
    # 这里面有三个变量，a dx dy ，所以我们至少需要选择三个参考点 P1,
    # P2, P3。
    #
    # 我们注意到如果参考点的 v0' - cy 为 0 ，左边趋于无穷大，这个等式就
    # 没有意义，所以参考点选取的第一个原则就是：
    #
    #     [*1]: 参考点对应的像素坐标不能在当前照片的水平中线上
    #
    # 另外如果 u0' - cx ，那么 y0 + dy 就没有意义，所以参考点选取第二原则：
    #
    #     [*2]: 选取的参考点也不能全在照片的中垂线上
    #
    # 为了简化说明，令
    #
    #          ( u0' - cx )   fy
    #     k0 = ------------ * --
    #          ( v0' - cy )   fx
    #
    # 并将 y0 + dy 移到等式左边，那么，选取的三个参考点 P1, P2, P3 对应
    # 下面三个等式
    #
    #     k1 * ( y1 + dy ) = x1 * cos(a) + z1 * sin(a) + dx     (1)
    #     k2 * ( y2 + dy ) = x2 * cos(a) + z2 * sin(a) + dx     (2)
    #     k3 * ( y3 + dy ) = x3 * cos(a) + z3 * sin(a) + dx     (3)
    #

    # *****************************************************************
    # *
    # * 当前相机没有仰角的情况
    # *
    # *****************************************************************
    #
    # 因为参考照片和相机平行，当没有仰角的时候，有 z1 = z2 = z3，那么
    # （1） - （2） 和 （3）- （2） 分别为
    #
    #     k1 * y1 - k2 * y2 + dy * (k1 - k2) = (x1 - x2) * cos(a) （4）
    #     k3 * y3 - k2 * y2 + dy * (k3 - k2) = (x3 - x2) * cos(a)  (5)
    #
    # 消去 cos(a)，得到
    #
    #          k1 * y1 * (x2 - x3) + k2 * y2 * (x3 - x1) + k3 * y3 * (x1 - x2)
    #     dy = ---------------------------------------------------------------
    #                k1 * (x3 - x2) + k2 * (x1 - x3) + k3 * (x2 - x1)
    #
    # 把 dy 代入（4），得到
    #
    #              k1 * y1 - k2 * y2 + dy * (k1 - k2)
    #     cos(a) = ----------------------------------
    #                       x1 - x2
    #
    #     在实际情况中，a 角度小于 90 度，我们可以得到唯一的一个水平方位角 a
    #
    #
    # 因为 dy，a 已知，代入（1），得到
    #
    #     dx = k1 * (y1 + dy) - (x1 * cos(a) + z1 * sin(a))
    #
    # 又，根据针孔相机成像公式
    #
    #     u1 = fx * x1' / z1' + cx
    #
    #     x1' = x1 * cos(a) + z1 * sin(a) + dx
    #
    #     z1' = -x1 * sin(a) + z1 * cos(a) + dz
    #
    # 得到
    #
    #     dz = fx / (u1 - cx) * (x1 * cos(a) + z1 * sin(a) + dx) + x1 * sin(a) - z1 * cos(a)
    #
    # 还是挺麻烦的啊，下面有仰角的情况怎么办呢.....
    #

    # *****************************************************************
    # *
    # * 当前相机存在仰角的情况
    # *
    # *****************************************************************
    #
    # 因为存在仰角，参考点的 Z 值可能不相等，还需要另辟蹊径。
    #
    # 也许就是选择 Z 值都相等的参考点就可以了，就是同一个水平线上的点，
    # 而 roll 又不会改变 Z 的值，所以不需要考虑  roll 的影响。
    #
    # 这里我们得到了参考点选择第三原则：
    #
    #     [*3]： 参考点必须位于同一水平线上，并且至少是三个
    #

    #
    # 综合上面的情况，选择的参考点为相片左上角，上边四分之一处和右上角
    # 三个点。
    k1, k2, k3 = [p[0] / p[1] for p in (imagePoints - (cx, cy)) * (fy, fx)]
    x1, y1, z1 = refObjectPoints[0]
    x2, y2, z2 = refObjectPoints[1]
    x3, y3, z3 = refObjectPoints[2]
    u1 = imagePoints[0][0]

    cos, sin = np.cos, np.sin

    dy = (k1 * y1 * (x2 - x3) + k2 * y2 * (x3 - x1) + k3 * y3 * (x1 - x2)) / (k1 * (x3 - x2) + k2 * (x1 - x3) + k3 * (x2 - x1))
    dy = -dy
    a = np.arccos((k3 * y3 - k2 * y2 + dy * (k3 - k2))/(x3 - x2))

    # 水平方位角的范围修正为： -pi/2 ~ pi/2
    if a > np.pi / 2:
        a -= np.pi

    dx = k1 * (y1 + dy) - (x1 * cos(a) + z1 * sin(a))
    dz = fx / (u1 - cx) * (x1 * cos(a) + z1 * sin(a) + dx) + x1 * sin(a) - z1 * cos(a)

    dy2 = (k1 * y1 * (x3 - x2) - k3 * y3 * (x1 - x2)) / (k1 * (x3 - x2) - k3 * (x1 - x2))
    cosa2 = (k1 * (y1 - dy2) - k3 * (y3 - dy2)) / (x1 - x3)
    a2 = np.arccos(cosa2)
    print "======== dy, dy2:", dy, dy2
    print "cosa2, a2:", cosa2, a2

    print "tvec, t:", tvec, t
    print "cx, cy, fx, fy:", cx, cy, fx, fy
    print "imagePoints:", imagePoints
    print "refObjectPoints:", refObjectPoints
    print "k:", k1, k2, k3
    print 'alpha is ', a
    print 'dx, dy, dz:', dx, dy, dz

    # 因为 dx, dy, dz 是虚拟相机坐标系，所以要使用虚拟坐标系旋转矩阵进
    # 行逆操作，得到世界坐标系的位移量
    tvec2 = (rmat.T * np.float64([dx, dy, dz]).reshape(3, 1)).A.reshape(-1) + tvec
    tvec2 = np.float64([-120, -135, -340])
    print 'objectPoints:', objectPoints
    print 'tvec2:', tvec2
    m = compose_rotation_matrix(yaw=-0.38, pitch=0, roll=-0.01)
    _r1, _p1 = projectPoints(objectPoints, m, tvec2, fx, fy, cx, cy)
    print "after rot point:", _r1
    print "after pro point:", np.int32(_p1)
    return tvec2

def find_pose_without_roll(H, Kr, tvec, Kc, t, roll=None):
    if roll is None:
        find_pose_by_vertical_reference(H, Kr, tvec, t, Kc)

def find_pose_by_vertical_reference(H, Kr, tvec, t, Kc):
    '''当参考照片选取的参考平面为垂直平面时候，在相机参考系中，参考平面
    上所有点的 Z 值均相同。在这种情况下根据当前照片计算当前相机所在的位
    置，并且还假定当前相机绕Z轴的旋转 roll = 0。

    H          Homography 矩阵
    Kr         参考相机内参
    tvec       参考相机位置
    t          参考相机和参考照片之间的距离，照片和参考面平行
    Kc         当前相机内参

    返回当前相机位置

    '''

    # Z 的最小差值，低于这个值则认为参考点选取不正确
    min_delta_z = 10

    # 虚拟仰角的大小，主要是为了让参考平面的 Z 值产生差别
    virtual_pitch = -0.114

    # 当前照片参考点像素坐标，五个参考点： 左上角，上边中点，下边中点，
    # 左边中点，右边中点
    fx, fy, cx, cy = Kc[0][0], Kc[1][1], Kc[0][2], Kc[1][2]
    imagePoints = np.float64([[0, 0], [cx, 0], [cx, cy * 2], [0, cy], [cx * 2, cy]])

    # 参考点对应的空间坐标
    objectPoints = unproject_homography_points(imagePoints, H, Kr, tvec, t)

    # 假设当前相机位于参考位置，使用虚拟仰角进行旋转，计算相应的旋转后
    # 的空间坐标和对应的像素坐标，我们称这个相机为虚拟相机和虚拟照片，
    # 这样主要是为了让参考点空间坐标的Z值不相等，如果Z值都相等，后面的
    # 计算公式就没有意义。
    rmat = compose_rotation_matrix(pitch=virtual_pitch)
    refObjectPoints, refImagePoints = projectPoints(objectPoints, rmat, tvec, fx, fy, cx, cy)

    # 假设当前相机和虚拟相机的水平方位角为 a，仰角为 b，位移量为 dx,
    # dy, dz, 位移量以虚拟相机坐标系进行度量。那么，根据坐标轴旋转公式
    # （水平方位角是绕Y轴的旋转，仰角是绕X轴的旋转），虚拟坐标系中空间
    # 点 P ( x, y, z ) 在当前相机坐标系为 P'
    #
    #     x' = x * cos(a) + z * sin(a) - dx
    #     y' = y * cos(b) - (z * cos(a) - x * sin(a)) * sin(b) - dy
    #     z' = y * sin(b) + (z * cos(a) - x * sin(a)) * cos(b) - dz
    #
    # 其中，坐标系旋转是首先绕 Y 轴，然后在绕 X 轴。
    #
    # 根据针孔相机成像模型公式
    #
    #     u = fx * x / z + cx
    #     v = fx * y / z + cy
    #
    # 我们可以得到空间坐标点 P 在当前照片中的像素坐标为
    #
    #     u' = fx * x' / z' + cx   => x' = z' * ( u' - cx ) / fx
    #     v' = fy * y' / z' + cy   => y' = z' * ( v' - cy ) / fy
    #
    # 对于位于照片中垂线上点，有
    #
    #     u' - cx = 0
    #
    # 那么，当 z' 不等于 0 时，对于中垂线上任意空间坐标点，满足下面的关系
    #
    #    x' = 0
    #
    #    ==>
    #
    #    x * cos(a) + z * sin(a) - dx = 0
    #
    # 选取任意两个中垂线上点（例如相片上下边的中点），代入上面的等式，得到
    #
    #    x1 * cos(a) + z1 * sin(a) - dx = 0
    #    x2 * cos(a) + z2 * sin(a) - dx = 0
    #
    # 消去 dx 即有
    #
    #    tg(a) = (x2 - x1) / (z1 - z2)
    #
    # 当 z1 不等于 z0 时候，我们就可以求得对应的水平方位角。
    #
    # 把 a 代入上面任意一个等式，可以求得 dx。
    #
    # 同理，我们取相片水平中线上的参考点，有
    #
    #    v' - cy = 0    ==>    v' = 0    ==>   y' = 0
    #
    #    == >
    #
    #    y * cos(b) - (z * cos(a) - x * sin(a)) * sin(b) - dy = 0
    #
    # 因为 a 已知，上式中只有 b 和 dy 两个未知量，取水平中线上的两个参
    # 考点（例如相片左右边的中点），得到
    #
    #    y3 * cos(b) - (z3 * cos(a) - x3 * sin(a)) * sin(b) - dy = 0
    #    y4 * cos(b) - (z4 * cos(a) - x4 * sin(a)) * sin(b) - dy = 0
    #
    # 消去 dy，得到
    #
    #    tg(b) = (y4 - y3) / ((z3 * cos(a) - x3 * sin(a)) - (z4 * cos(a) - x4 * sin(a)))
    #
    # 当 (z3 * cos(a) - x3 * sin(a)) - (z4 * cos(a) - x4 * sin(a)) 不为
    # 0 时候，可以求得仰角 b
    #
    # 把 b 代入上面任意一个等式，求得 dy。
    #
    # 最后选取任意一个不在中线上的点（例如左上角），代入针孔相机成像模型公式，即有
    #
    #    u0 = fx * x0' / z0' + cx
    #    x0' = x0 * cos(a) + z0 * sin(a) - dx
    #    z0' = y0 * sin(b) + (z0 * cos(a) - x0 * sin(a)) * cos(b) - dz
    #
    # 这里面只有一个变量 dz 未知，即
    #
    #    dz = y0 * sin(b) + (z0 * cos(a) - x0 * sin(a)) * cos(b) + (x0 * cos(a) + z0 * sin(a) - dx) * fx / (u0 - cx)
    #
    x0, y0, z0 = refObjectPoints[0]
    x1, y1, z1 = refObjectPoints[1]
    x2, y2, z2 = refObjectPoints[2]
    x3, y3, z3 = refObjectPoints[3]
    x4, y4, z4 = refObjectPoints[4]

    cos, sin = np.cos, np.sin

    delta = np.abs(z1 - z2)
    if delta < min_delta_z:
        raise Exception('中垂线上两个参考点Z值相距太近（约为 %s )' % delta)

    a = np.arctan2(x2 - x1, z1 - z2)
    dx = x1 * cos(a) + z1 * sin(a)

    kz3, kz4 = z3 * cos(a) - x3 * sin(a), z4 * cos(a) - x4 * sin(a)
    delta = np.abs(kz3 - kz4)
    if delta < min_delta_z:
        raise Exception('水平中线上两个参考点Z值相距太近（约为 %s )' % delta)

    b = np.arctan2(y4 - y3, kz3 - kz4)
    dy = y3 * cos(b) - kz3 * sin(b)

    u0 = imagePoints[0][0]
    dz = y0 * sin(b) + (z0 * cos(a) - x0 * sin(a)) * cos(b) + (x0 * cos(a) + z0 * sin(a) - dx) * fx / (u0 - cx)

    # 因为 dx, dy, dz 是虚拟相机坐标系，所以要使用虚拟坐标系旋转矩阵进
    # 行逆操作，得到世界坐标系的位移量
    return (rmat.T * np.float64([dx, dy, dz]).reshape(3, 1)).A.reshape(-1) + tvec

def find_pose_by_center_without_pitch(objPoint, imgPoint, azimuth, fx, fy, cx, cy, tvec):
    '''根据参考照片计算当前相机没有 pitch 情况下的位置，这是一种简化处理。

    objPoint   当前照片中点对应的空间坐标
    imgPoint   当前照片中对应的像素坐标，其实应该等于 (cx, cy)
    azimuth    当前相机的水平方位角
    fx, fy,
    cx, cy     当前相机内部参数
    tvec       当前相机位置
    '''
    rmat = rotation_matrix(-azimuth, axis='y')
    rotPoints, imageRotPoints = projectPoints(np.array([objPoint]), rmat, tvec, fx, fy, cx, cy)

    x0, y0, z0 = rotPoints.reshape(-1, 3)[0]
    ma = imageRotPoints.reshape(-1, 2)[0]
    Ma = imgPoint;

    du, dv = (Ma - ma).reshape(-1, 2)[0]
    dz = z0 - y0 / ( dv / fy + y0 / z0 )
    dx = x0 - ( du / fx + x0 / z0 ) * ( z0 - dz )

    dx, _dy, dz = (rmat.T * np.float64([dx, 0, dz]).reshape(3, 1)).A.reshape(-1, 3)[0]
    return dx, _dy, dz

def find_pose_by_center_with_pitch():
    '''根据参考照片计算当前相机有仰角的情况下的位置。
    '''
    pass

def verify_pose():
    '''调整不同的方位角，比较结果

    delta = 0.1       大约每6度
            0.05      大约每3度
            0.02      大约每1.2度

    范围为 5 度，也就是从 -5 ~ +5，总共是 10 度，分别需要计算 2、4、8 次。
    范围为 10 度，共需要搜索是 20 度，分别需要计算 4、8、16 次。

    '''
    pass

def find_pose(refPoints, imagePoints, cameraMatrix, tvec):
    '''计算当前相机的拍摄位置，以参考照片拍摄地点为坐标原点作为参考坐标系。

    传入参数：
        refPoints    三个参考点，三维坐标，前两个点是参考平面上一条水平线，
                     第一个点和第三个是参考平面上的垂线
        imagePoints  两个参考点在当前照片对应的像素坐标
        cameraMatrix 当前相机的内部参数
        tvec         参考相机的位置

    返回当前相机的拍摄位置

    '''
    # 根据像素坐标偏移计算相机位置偏移
    fx, fy, cx, cy = cameraMatrix[0][0], cameraMatrix[1][1], cameraMatrix[0][2], cameraMatrix[1][2]

    # 计算照片的旋转角度，因为假定参考点是水平线，所以两个像素坐标点与
    # 水平线的夹角就是拍摄角度
    Ma, Mb = imagePoints.reshape(-1, 2)[:2]
    roll = np.arctan2(Mb[1] - Ma[1], Mb[0] - Ma[0])

    angle = 0.36
    # rmat = rotation_matrix(roll, axis='z') * rotation_matrix(angle, axis='y')
    rmat = rotation_matrix(-angle, axis='y')
    print ('roll is ', roll, ', angle is ', angle)

    # 计算旋转参考平面 angle 之后，使用当前相机，在参考位置拍摄得到的像素坐标
    rotPoints, imageRotPoints = projectPoints(refPoints, rmat, tvec, fx, fy, cx, cy)
    print 'tvec is ', tvec
    print "rotPoints", rotPoints.reshape(-1, 3)
    print "Rotated Image Points", imageRotPoints.reshape(-1, 2)

    for i in range(rotPoints.shape[0]):
        x0, y0, z0 = rotPoints.reshape(-1, 3)[i]
        ma = imageRotPoints.reshape(-1, 2)[i]
        assert(not z0 == 0)
        print "Point ", i, refPoints[i]
        print "Rotate:", x0, y0, z0

        Ma = imagePoints.reshape(-1, 2)[i]

        print "Ma, ma:", Ma, ma
        du, dv = (Ma - ma).reshape(-1, 2)[0]
        print "du, dv:", du, dv

        dz = z0 - y0 / ( dv / fy + y0 / z0 )
        dx = x0 - ( du / fx + x0 / z0 ) * ( z0 - dz )
        print "dx', dz':", dx, dz

        # s1 = dx2 * np.tan(angle)
        # s2 = dz2 - s1
        # dz = s2 * np.cos(angle)
        # dx = dx2 / np.cos(angle) + s2 * np.sin(angle)
        dx, _x, dz = (rmat.T * np.float64([dx, 0, dz]).reshape(3, 1)).A.reshape(-1, 3)[0]
        print "dx, dz:", dx, dz
        print "?===="
    return dx, 0, dz

def calculate_camera_offset(objectPoints, imagePoints, fx, fy, cx, cy, yaw):
    if objectPoints.shape[0] < 2  or imagePoints.shape[0] < 2:
        raise ValueError('参考点至少是二个')

    # rm = np.matrix(rt)
    rm = np.matrix(rotation_matrix(yaw, 'y'))
    p1 = (rm * objectPoints[0].reshape(3, 1)).A.reshape(-1)
    p2 = (rm * objectPoints[1].reshape(3, 1)).A.reshape(-1)

    m = np.float64(imagePoints.reshape(-1, 2) - (cx, cy))
    if m[0][1] == 0 or m[1][1] == 0:
        raise ValueError('参考点不能位于中垂线')


    dt = m[1][0] / m[1][1] - m[0][0] / m[0][1]
    if dt == 0:
        raise ValueError('两个参考点不能和原点共线')

    print ('p1:', p1)
    print ('p2:', p2)
    print('m:', m)
    yc = ((p1[1] - p2[1]) * fy / fx + p2[0] * m[1][1] / m[1][0] - p1[0] * m[0][1] / m[0][0]) / dt
    xc = - (p1[1] - yc) / m[0][1] * fy / fx * m[0][0] + p1[0]
    zc = - fy * (p1[1] - yc) / m[0][1] + p1[2]

    print 'yaw is ', yaw

    p = np.float64([xc, yc, zc])
    rm = np.matrix(rotation_matrix(-yaw, 'y'))
    ps = (rm * p.reshape(3, 1)).A.reshape(-1)
    print 'Ps:', ps
    return xc, yc, zc
