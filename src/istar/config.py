# -*- coding: utf-8 -*-
#

class StarException(Exception):
    pass

base_data_path = 'data'

#
# 建筑物的数据文件，包括 Wifi 的 BSSID 信息和 区域的范围，用来确定
# wifi 和 区域的索引
#
#   {
#     "wifis": [ "xx-xx-xx", "xx-xx-xx", ... ],
#     "regions": [ [x0, y0, z0, x1, y1, z1], ... ],
#   }
#
data_filename = 'index.json'

#
# 参考图片数据
#
#   [
#     {
#       "position": [ x, y z ],
#       "azimuth": 0,
#       "camera": [ fx, fy, cx, cy ],
#       "data": "filename.npz"
#     },
#     ...
#   ]
#   
image_list_filename= 'images.json'

#
# Wifi 指纹数据，是以行为 wifi 索引，列为区域索引的二维 numpy 的数组
# 
wifi_data_filename = 'wifi-finger.npy'

#
# 关键点匹配算法
#
kp_feature_name = 'orb-flann'

#
# 关键点的最多个数
#
kp_feature_count = 2000
kp_feature_asift_count = 800

#
# 参考照片关键点的最多个数，少于这个的参考照片不被接受
#
kp_image_threshold_count = 100

#
# 添加双目参考照片时候，匹配的关键点的最少个数，低于这个数目认为两个照
# 片不匹配
#
kp_stereo_match_threshold = 300

#
# 匹配的关键点的最少个数，低于这个数目认为两个照片不匹配
#
kp_query_match_threshold = 30

#
# 参考照片的活力指数文件
#
vigor_index_filename = 'vigor-index.json'

#
# 参考照片的活力指数字典
#
vigor_index = {}

#
# 查询模式，用户使用手机定位时候的相应的参数
#
query_modes = {
    
    'default': {        
        'feature': {
            'name': 'orb',
            'count': 2000,
        },
        'matcher': {
            'name': 'flann',
            'threshold': 30,
        },
    }

}

#
# 训练模式，生成特征平面对象的时候的模式
#
train_modes = {

    'default': {
        'feature': {
            'name': 'orb',
            'count': 600,
        },
        'asift': {
        },        
    },

    'orb': {
        'feature': {
            'name': 'orb',
            'count': 3000,
        }
    }

}
