# -*- coding: utf-8 -*-
#
# 本程序主要用来管理数据，包括添加和删除参考照片，添加和删除区域以及添
# 加和删除Wifi指纹信息等。
#
# 根据参考图片生成的对象空间坐标以参考相机为坐标系原点，相机正前方为 Z
# 轴，下方为 Y 轴，相机右侧为 X 轴的右手系，单位为 厘米。
#
# 参考相机的位置使用的坐标系以建筑物某处为原点，正北为 Y 轴，正东为 X
# 轴，向上为 Z 轴。
#
# 建筑物的原点是使用 EPSG:4326 坐标系的地理坐标，单位为 米。
#
#
# 使用方法:
#
#     add building XXX
#     remove building XXX
#     add region XXX
#     update region XXX A=B C=D
#
#     add image -b BUILDING FILENAME
#     remove image -b BUILDING IMAGE-INDEX
#     build image --asift --feature --n IMAGE-INDEX
#
#     add relation REGION IMAGE-INDEX
#     remove relation REGION IMAGE-INDEX
#
#     test match
#     test build
#     test locate
#
import getopt
import json
import logging
import os
import time
import sys

import numpy as np
import cv2

from config import StarException, \
    base_data_path, data_filename, image_list_filename, wifi_data_filename, \
    kp_feature_name, kp_feature_count, kp_feature_asift_count, \
    kp_image_threshold_count, kp_stereo_match_threshold, \
    vigor_index_filename
from calibration.feature import init_feature, asift_detect_compute, match_images
from calibration.recover import unproject_image_points, rotation_matrix

def write_yaml(path, keypoints, descriptors, points3d):
    '''写入 yaml 格式的数据 path 指定的文件中。

    在我的Xp上运行只能写入单个的值，写 np.array 的数据直接崩溃，原因暂
    时不明，所以现在暂时不用这种格式，而是直接用 np 的存储格式。
    '''
    fs = cv2.FileStorage(path, cv2.FILE_STORAGE_WRITE)
    fs.write('keypoints', keypoints)
    fs.write('descriptors', descriptors)
    fs.write('points3d', points3d)
    fs.release()

def read_yaml(path):
    '''读取 yaml 格式的数据，返回 keypoints, descriptors, points3d。'''
    fs = cv2.FileStorage(path, cv2.FILE_STORAGE_READ)
    keypoints = fs.getNode('keypoints')
    descriptors = fs.getNode('descriptors')
    points3d = fs.getNode('points3d')
    fs.release()
    return keypoints, descriptors, points3d

def save_keypoint_data(filename, keypoints, descriptors, points3d):
    '''写入 npz 格式的数据到 path 指定的文件中。'''
    kpdata =  np.array([(kp.pt[0], kp.pt[1], kp.size, kp.angle, kp.response, kp.octave, kp.class_id)
                        for kp in keypoints])
    np.savez(filename, keypoints=kpdata, descriptors=descriptors, points3d=points3d)
    return filename

def load_keypoint_data(building, rindex, name):
    '''读取 npz 格式的数据，返回 keypoints, descriptors, points3d。'''
    path = get_region_path(building, rindex)
    npzfile = np.load(os.path.join(path, name if name.endswith('.npz') else (name + '.npz')))
    keypoints = [cv2.KeyPoint(x, y, size, angle, response, int(octave), int(class_id))
                 for x, y, size, angle, response, octave, class_id in npzfile['keypoints']]
    return keypoints, npzfile['descriptors'], npzfile['points3d']

def get_refplane_path(building):
    return os.path.join(base_data_path, building, 'refplanes')

def get_region_images(building, region):
    filename = get_region_path(building, region) + '.json'
    with open(filename, 'r') as f:
        data = json.load(f)
    path = get_refplane_path(building)
    return [ os.path.join(path, name) for name in data['refplanes'] ]

def get_region_list(building):
    filename = os.path.join(base_data_path, building, data_filename)
    with open(filename, 'r') as f:
        return json.load(f)['regions']

def get_region_path(building, region):
    return os.path.join(base_data_path, building, region)

def find_region_by_position(regions, position):
    index = 0
    z = position[2]
    p = tuple(position[:2])
    for r in regions:
        height, polygon = r['height'], np.int32(r['polygon'])
        if (z >= height[0]
            and z <= height[1]
            and cv2.pointPolygonTest(polygon, p, False) >= 0):
            return index
        index += 1

def merge_image_into_region(building, position, azimuth, camera, keypoints, descriptors, points3d, name=None):
    regions = get_region_list(building)
    rindex = find_region_by_position(regions, position)
    if rindex is None:
        raise StarException('坐标 %s 没有对应的区域' % position)
    path = get_region_path(building, rindex)
    if not os.path.exists(path):
        os.mkdir(path)
    if name is None:
        name = time.strftime('img-%Y%m%d-%H%M%S')
    save_keypoint_data(os.path.join(path, name), keypoints, descriptors, points3d)
    filename = os.path.join(path, image_list_filename)
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            data = json.load(f)
    else:
        data = []
    data.append({
        'name': name,
        'position': position,
        'azimuth': azimuth * np.pi / 180,
        'camera': camera,
    })
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    return name

def load_vigor_index(building):
    filename = os.path.join(base_data_path, building, vigor_index_filename)
    with open(filename, 'r') as f:
        return json.load(f)

def triangulate_points(projMatr1, projMatr2, projPoints1, projPoints2):
    points4D = cv2.triangulatePoints(projMatr1, projMatr2, projPoints1, projPoints2)
    return cv2.convertPointsFromHomogeneous(points4D.T);

def stereo_rectify(cameraMatrix1, distCoeffs1, cameraMatrix2, distCoeffs2, imageSize, R, T):
    R1, R2, P1, P2, Q, validPixROI1, validPixROI2 = cv2.stereoRectify(
        cameraMatrix1, distCoeffs1, cameraMatrix2, distCoeffs2, imageSize, R, T
        )
    return P1, P2, Q

def compute_stereo_images(imgL, imgR, K, rvec, tvec, dist):
    window_size = 3
    min_disp = 16
    num_disp = 112-min_disp
    stereo = cv2.StereoSGBM_create(minDisparity = min_disp,
        numDisparities = num_disp,
        blockSize = 16,
        P1 = 8*3*window_size**2,
        P2 = 32*3*window_size**2,
        disp12MaxDiff = 1,
        uniquenessRatio = 10,
        speckleWindowSize = 100,
        speckleRange = 32
    )

    print('computing disparity...')
    disp = stereo.compute(imgL, imgR).astype(np.float32) / 16.0

    print('generating 3d point cloud...',)
    h, w = imgL.shape[:2]
    P1, P2, Q = stereo_rectify(K, dist, K, dist, (h, w), rvec, tvec)
    points = cv2.reprojectImageTo3D(disp, Q)
    colors = cv2.cvtColor(imgL, cv2.COLOR_BGR2RGB)
    mask = disp > disp.min()
    out_points = points[mask]
    out_colors = colors[mask]

def add_image(building, position, azimuth, focal, mask, distance, filename, asift=True):
    feature_name, count = kp_feature_name, kp_feature_asift_count if asift else kp_feature_count
    detector, matcher = init_feature(feature_name, n=count)

    img = cv2.imread(filename, 0)
    h, w = img.shape[:2]
    if mask is None:
        maskData = None
    else:
        x0, y0, x1, y1 = mask
        maskData = np.zeros((h, w), dtype=np.uint8)
        maskData[y0:y1, x0:x1] = 255

    keypoints, descriptors = asift_detect_compute(detector, img, maskData) if asift \
        else detector.detectAndCompute(img, maskData)
    n = len(keypoints)
    if n < kp_image_threshold_count:
        raise StarException('参考照片的关键点个数 %i 少于最低值 %i', n, kp_image_threshold_count)
    logging.info('参考图片关键点数目为 %d', n)

    fx, fy = focal[0] * w, focal[1] * h
    cx, cy = (w-1)/2, (h-1)/2
    K = np.float64([[fx, 0,  cx],
                    [0,  fy, cy],
                    [0,  0,  1]])
    impoints = np.float64([kp.pt for kp in keypoints])
    points3d = unproject_image_points(impoints, K, distance)
    camera = fx, fy, cx, cy
    name = os.path.splitext(os.path.basename(filename))[0]
    return merge_image_into_region(building, position, azimuth, camera, keypoints, descriptors, points3d, name)

def add_depth_image(building, position, azimuth, focal, rotate, offset, depth_filename, filename, asift=True):
    disp = cv2.imread(depth_filename, 0)
    img = cv2.imread(filename, 0)
    h, w = img.shape[:2]

    fx, fy = focal
    cx, cy = (w-1)/2, (h-1)/2
    K = np.float64([[fx, 0, cx],
                    [0, fy, cy],
                    [0,  0,  1]])
    dist = np.zeros(4)
    R = rotation_matrix(rotate, axis='y').A
    T = np.float64(offset)
    P1, P2, Q = stereo_rectify(K, dist, K, dist, (h, w), R, T)
    # f = 0.8*w
    # Q = np.float32([[1, 0,  0, -0.5*w],
    #                 [0, 1,  0, -0.5*h],
    #                 [0, 0,  0,      f],
    #                 [0, 0, -1,      0]])
    points3d = cv2.reprojectImageTo3D(disp, Q)

    keypoints, descriptors = asift_detect_compute(detector, img) if asift else detector.detectAndCompute(img)
    n = len(keypoints)
    if n < kp_image_threshold_count:
        raise StarException('参考照片的关键点个数 %i 少于最低值 %i', n, kp_image_threshold_count)
    logging.info('参考图片关键点数目为 %d', n)

    camera = fx, fy, cx, cy
    name = os.path.splitext(filename)[0]
    points3d = points3d[[kp.pt for kp in keypoints]]
    return merge_image_into_region(building, position, azimuth, camera, keypoints, descriptors, points3d, name=name)

def add_stereo_images(building, position, azimuth, focal, rotate, offset, filename1, filename2):
    imgLeft, imgRight = cv2.imread(filename1, 0), cv2.imread(filename2, 0)
    h, w = imgLeft.shape[:2]
    R = rotation_matrix(rotate, axis='y').A
    T = np.float64(offset)
    distCoeffs = np.zeros(4)
    fx, fy = focal
    cx, cy = (w-1)/2, (h-1)/2
    K = np.float64([[fx, 0, cx],
                    [0, fy, cy],
                    [0,  0,  1]])
    P1, P2, Q = stereo_rectify(K, distCoeffs, K, distCoeffs, (h, w), R, T)

    feature_name, count = kp_feature_name, kp_feature_count
    detector, matcher = init_feature(feature_name, n=count)
    pts1, pts2, keypoints, descriptors = match_images(imgLeft, imgRight, feature_name, count)
    if len(keypoints) < kp_stereo_match_threshold:
        raise StarException('双目照片匹配的关键点个数少于 %i' % kp_stereo_match_threshold)

    points3d = triangulate_points(P1, P2, pts1.T, pts2.T)
    camera = fx, fy, cx, cy
    name = os.path.splitext(os.path.basename(filename1))[0]
    return merge_image_into_region(building, position, azimuth, camera, keypoints, descriptors, points3d, name=name)

def get_wifi_list(building):
    filename = os.path.join(base_data_path, building, data_filename)
    with open(filename, 'r') as f:
         data = json.load(f)['bssids']
    return data

def append_wifi_bssid(building, bssid):
    filename = os.path.join(base_data_path, building, data_filename)
    with open(filename, 'r+') as f:
         data = json.load(f)
         if bssid not in data['bssids']:
             data['bssids'].append(bssid)
             f.seek(0)
             json.dump(data, f, indent=2)

def build_finger_from_rssi(building, rssiData):
    regions = get_region_list(building)
    finger = np.zeros(len(regions), dtype=np.float64)
    for data in rssiData:
        rssi = data[0]
        pos = data[1:]
        r = find_region_by_position(regions, pos)
        if r is None:
            logging.warning('位置 %s 没有在区域定义的范围内', pos)
        else:
            finger[r] = rssi
    return finger

def merge_wifi_data(building, bssid, rssiData):
    '''添加wifi指纹到数据库。

    building     当前建筑物，字符串
    bssid        wifi 对应的 bssid
    rssiData     位置和 rssi 的列表，格式为 [ ( rssi, x, y, z ), ... ]

    '''
    wifiBssids = get_wifi_list(building)
    try:
        index = wifiBssids.index(bssid)
    except ValueError:
        index = -1

    finger = build_finger_from_rssi(building, rssiData)

    filename = os.path.join(base_data_path, building, wifi_data_filename)
    if os.path.exists(filename):
        wifiData = np.load(filename)
    else:
        row = len(wifiBssids)
        col = len(finger)
        wifiData = np.zeros((row, col), dtype=np.float64)

    if index == -1:
        logging.info('添加Wifi %s 到数据文件', bssid)
        append_wifi_bssid(building, bssid)
        wifiData = np.concatenate((wifiData, finger.reshape(1, -1)))
    else:
        wifiData[index] = finger

    np.save(filename, wifiData)

def add_wifi_finger(building, rssid, filename):
    data = np.loadtxt(filename)
    merge_wifi_data(building, rssid, data)

def do_add_image(argv):
    try:
        opts, args = getopt.getopt(
            argv,
            'a:b:c:f:m:p:r:s:t:',
            ['azimuth=', 'building=', 'distance=', 'focal=',
             'mask=', 'position=', 'region=', 'ssize=']
            )
    except getopt.GetoptError:
        logging.exception('输入的参数不正确')
        sys.exit(1)

    azimuth = .0
    building = 'wuxin'
    distance = .0
    mask = None
    position = .0, .0, .0
    focal = None
    cmos = 3.6, 4.8
    rindex = None
    for o, a in opts:
        if o in ('-a', '--azimuth'):
            azimuth = float(a)
        elif o in ('-b', '--building'):
            building = a
        elif o in ('-f', '--focal'):
            focal = float(a)
        elif o in ('-m', '--mask'):
            mask = [int(s) for s in a.split(',')]
        elif o in ('-p', '--position'):
            position = [float(s) for s in a.split(',')]
        elif o in ('-t', '--distance'):
            distance = float(a)
        elif o in ('-r', '--region'):
            rindex = int(a)
        elif o in ('-s', '--ssize'):
            cmos = [float(s) for s in a.split(',')]

    try:
        filename = args[0]
    except IndexError:
        logging.warning('缺少图像文件名称')
        return

    if not os.path.exists(filename):
        logging.warning('图像文件 %s 不存在', filename)
        return

    if focal is None:
        logging.waring('缺少相机参数')
        return

    if len(args[1:]):
        logging.warning('只有第一个图像文件 %s 被处理，其他文件都会被忽略', filename)

    if rindex is None:
        regions = get_region_list()
        rindex = find_region_by_position(regions, position)
        if rindex is None:
            logging.warning('位置 %s 对应的区域在数据库中不存在', position)
            return

    focal = [ focal / x for x in cmos ]
    add_image(building, position, azimuth, focal, mask, distance, filename)

def do_remove_image(argv):
    pass

def do_add_stereo_images(argv):
    try:
        opts, args = getopt.getopt(
            argv,
            'a:b:f:r:p:t:',
            ['azimuth=', 'building=', 'focal=', 'offset=', 'rotate=', 'position=']
            )
    except getopt.GetoptError:
        logging.exception('输入的参数不正确')
        sys.exit(1)

    azimuth = .0
    building = 'wuxin'
    offset = .0, .0, .0
    rotate = 0
    position = .0, .0, .0
    focal = None
    for o, a in opts:
        if o in ('-a', '--azimuth'):
            azimuth = float(a)
        elif o in ('-b', '--building'):
            building = a
        elif o in ('-f', '--focal'):
            focal = [float(s) for s in a.split(',')]
        elif o in ('-o', '--offset'):
            offset = [float(s) for s in a.split(',')]
        elif o in ('-r', '--rotate'):
            rotate = float(a)
        elif o in ('-p', '--position'):
            position = [float(s) for s in a.split(',')]

    try:
        filename1, filename2 = args[:2]
    except IndexError:
        logging.warning('缺少图像文件名称，必须有左右视野的两张照片')
        return

    for s in filename1, filename2:
        if not os.path.exists(s):
            logging.warning('图像文件 %s 不存在', s)
            return

    if focal is None:
        logging.waring('缺少相机参数')
        return

    if len(args[2:]):
        logging.warning('只有第一组图像文件 %s 被处理，其他文件都会被忽略', (filename1, filename2))

    regions = get_region_list()
    rindex = find_region_by_position(regions, position)
    if rindex is None:
        logging.warning('位置 %s 对应的区域在数据库中不存在', position)
        return

    add_stereo_images(building, position, azimuth, focal, rotate, offset, filename1, filename2)


def do_add_depth_image(argv):
    try:
        opts, args = getopt.getopt(
            argv,
            'a:b:d:f:o:p:r:',
            ['azimuth=', 'building=', 'depth=', 'focal=',
             'offset=', 'position=', 'rotate=']
            )
    except getopt.GetoptError:
        logging.exception('输入的参数不正确')
        sys.exit(1)

    azimuth = .0
    building = 'wuxin'
    depth_filename = None
    position = .0, .0, .0
    offset = .0, .0, .0
    rotate = 0
    focal = None
    for o, a in opts:
        if o in ('-a', '--azimuth'):
            azimuth = float(a)
        elif o in ('-b', '--building'):
            building = a
        elif o in ('-d', '--depth'):
            depth_filename = a
        elif o in ('-f', '--focal'):
            focal = [float(s) for s in a.split(',')]
        elif o in ('-o', '--offset'):
            offset = [float(s) for s in a.split(',')]
        elif o in ('-p', '--position'):
            position = [float(s) for s in a.split(',')]
        elif o in ('-r', '--rotate'):
            rotate = float(a)

    try:
        filename = args[0]
    except IndexError:
        logging.warning('缺少图像文件名称')
        return

    if not os.path.exists(filename):
        logging.warning('图像文件 %s 不存在', filename)
        return

    if depth_filename is None:
        logging.warning('缺少深度图像文件')
        return

    if not os.path.exists(depth_filename):
        logging.warning('深度图像文件 %s 不存在', depth_filename)
        return

    if focal is None:
        logging.waring('缺少相机参数')
        return

    regions = get_region_list()
    rindex = find_region_by_position(regions, position)
    if rindex is None:
        logging.warning('位置 %s 对应的区域在数据库中不存在', position)
        return

    add_depth_image(building, position, azimuth, focal, rotate, offset, depth_filename, filename)

def do_add_wifi(argv):
    try:
        opts, args = getopt.getopt(argv, 'b:r:s:', ['building=', 'rssid=', 'ssid='])
    except getopt.GetoptError:
        logging.exception('输入的参数不正确')
        sys.exit(1)

    building = 'wuxin'
    rssid = None
    ssid = None
    for o, a in opts:
        if o in ('-b', '--building'):
            building = a
        elif o in ('-r', '--rssid'):
            rssid = a
        elif o in ('-s', '--ssid'):
            ssid = a

    for filename in args:
        if os.path.exists(filename):
            logging.error('文件 %s 不存在', filename)
            continue
        if rssid is None:
            rssid = os.path.splitext(os.path.basename(filename))[0]
        add_wifi_finger(building, rssid, filename)

def do_remove_wifi(argv):
    pass

def do_add_region(argv):
    pass

def do_remove_region(argv):
    pass

def add_building(name):
    pass

def main(cmd, argv):
    if cmd not in ('add', 'build', 'list', 'remove', 'show', 'update'):
        logging.warning('无法识别的命令: %s', cmd)
        return

    try:
        name = argv[0]
    except IndexError:
        logging.error('命令 %s 缺少参数', cmd)
        return

    try:
        if name == 'stereo':
            do_add_stereo_images(argv[1:]) if cmd == 'add' else do_remove_images(argv[1:])
        elif name == 'image':
            do_add_image(argv[1:]) if cmd == 'add' else do_remove_image(argv[1:])
        elif name == 'depth':
            do_add_depth_image(argv[1:]) if cmd == 'add' else do_remove_image(argv[1:])
        elif name == 'wifi':
            do_add_wifi(argv[1:]) if cmd == 'add' else do_remove_wifi(argv[1:])
        elif name == 'region':
            do_add_region(argv[1:]) if cmd == 'add' else do_remove_region(argv[1:])
        else:
            logging.warning('无法识别的类型: %s', name)
    except StarException as e:
        logging.error(e)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2:])
