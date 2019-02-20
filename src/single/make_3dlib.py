#!/usr/bin python3
# -*- coding: utf-8 -*-
'''批量生成三维坐标库'''

import sys
import os
import time
import argparse

import matches
sys.path.append('../')
import rename as ra

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='批量生成三维坐标库')
    parser.add_argument('-imgdir', '--images_dir', metavar='path', 
        default='images/A', help='参考照片目录')
    parser.add_argument('-kpdir', '--key_points_dir', metavar='path', 
        default='features/orb8000',help='特征文件目录')
    parser.add_argument('-o', '--output', metavar='path', default='models',
        help='输出路径')
    args = parser.parse_args()

    imglist = ra.findFile(args.images_dir, name='A*.jpg')
    kplist = ra.findFile(args.key_points_dir, name='*.npz')
    kpfile1,kpfile2,img1,img2 = matches.get_kpfiles(imglist, kplist, args)

    matches.mk_dir(args.output)

    begin = time.time()
    begin_cpu = time.thread_time()    

    for i in range(len(kpfile1)):

        assert kpfile1[i] in kplist and kpfile2[i] in kpfile2, '又凉了'
        
        start = time.time()
        start_cpu = time.thread_time()
        os.system('python3 make_model.py --size 3000,4000 --homography \
            --refpos 10,0,0 -K 3123.8,3122.3,1497.6,2022.3 \
            --focals=1.04127,0.780575 --save --output {path} \
            {kpfile1} {kpfile2}'.format(kpfile1=kpfile1[i], kpfile2=kpfile2[i],
             path=args.output))
        print('process ' + kpfile1[i] + ' used cpu time: {t}s'.format(
            t=time.thread_time() - start_cpu))
        print('process ' + kpfile1[i] + ' used: {t}s'.format(
            t=time.time() - start))
    print('all used cpu time: {t}s'.format(t=time.thread_time() - begin_cpu))
    print('all used {t}s'.format(t=time.time() - begin))