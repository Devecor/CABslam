#!/usr/bin python3
# -*- coding: utf-8 -*-

'''批量提取照片特征点

author: devecor
'''

import argparse
import os
import time

import sys
sys.path.append(r'/home/devecor/CABslam/src')
import rename as ra

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='批量提取照片的特征点')
    parser.add_argument('path', help='dir of images')
    parser.add_argument('-o', '--output', default='features/orb8000', help='path of output')
    parser.add_argument('-n', '--nfeatures', default=8000, help='number of features')
    args = parser.parse_args()

    imglist = ra.findFile(args.path, name='*.jpg')
    
    for i in args.output.split('/'):
        if isinstance(i, str):
            os.system('mkdir {dir}'.format(dir=i))

    begin = time.time()
    begin_cpu = time.thread_time()
    for i in imglist:
        start = time.time()
        start_cpu = time.thread_time()

        os.system('python3 check_feature.py {imgname} --save --output {output} \
            --feature orb --nFeatures {n}'.format(imgname=i, output=args.output, 
            n=args.nfeatures))
        
        escape = time.time() - start
        escape_cpu = time.thread_time() - start_cpu

        print('detect {img} used: {t} seconds'.format(img=i, t=escape))
        print('detect {img} used cpu time: {t} seconds'.format(img=i, t=escape_cpu))

    print('all used: {} seconds'.format(time.time() - begin))
    print('all used cpu time: {} seconds'.format(time.thread_time() - begin_cpu))