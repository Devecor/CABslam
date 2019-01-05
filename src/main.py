# -*- coding: utf-8 -*-
#

import getopt
import json
import logging
import sys

import numpy as np
import cv2

from istar import main as istar_entry
from manager import main as manager_entry

__usage__ = '''
使用方法：

* 增加 Wifi 指纹数据

  python main.py add wifi FILENAME

* 增加参考图片

  python main.py add image
         --position=0.5,1.5,0
         --azimuth=90
         --distance=2.3
         --focal=3528,3528
         --mask=0,0,64,128
         IMAGE_FILENAME

* 增加深度图片

  python main.py add depth
         --position=0.5,1.5,0
         --azimuth=90
         --focal=3528,3528
         --depth=DEPTH_FILENAME
         IMAGE_FILENAME

* 增加双目参考图片

  python main.py add stereo
         --position=0.5,1.5,0
         --azimuth=90
         --focal=3528,3528
         --offset=2.3
         --rotate=10
         LEFT_IMAGE RIGHT_IMAGE

* 定位照片位置

  python main.py query
         --focal=3528,3528
         --wifi=test.json
         IMAGE_FILENAME
'''

def main(argv):
    try:
        cmd = argv[0]
    except IndexError:
        print( __usage__ )
        logging.error('缺少命令行参数')
        return

    if cmd == 'add' or cmd == 'remove':
        manager_entry(cmd, argv[1:])
    elif cmd == 'query':
        istar_entry(argv[1:])
    else:
        logging.error('非法的命令 %s', cmd)

if __name__ == '__main__':
    logging.basicConfig(
        format='%(levelname)s %(message)s',
        )
    main(sys.argv[1:])
