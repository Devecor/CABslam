#!/usr/bin python3
# -*- coding: utf-8 -*-

'''docstring'''

import time
import os
import argparse

import matches as m
import sys
sys.path.append('../')
import const_params as const

def query(query, *imgs, size='3000,4000', focals='1.04127,0.780575', 
    filter='homography', output='results'):
    '''
    Description
    ------------
    用于查询定位
    
    Parameters
    ------------
    query: 待查询图片
    imgs: 参考图片模型文件
    '''

    # query = query[0:len(query)-3]
    # IMGS = []
    # for i in imgs:
    #     IMGS.append(i[0:len(imgs-3)])
    if isinstance(imgs[0],list):
        imgs = ' '.join(imgs[0])
    else:
        imgs = ' '.join(imgs)

    start = time.time()
    start_cpu = time.thread_time()

    cmd = 'python3 query_location.py --size {size} \
--focals {focals} --{filter} --save --output {output} --debug \
{query} {imgs}'.format(
            size=size, focals=focals, filter=filter, output=output, 
            query=query, imgs=imgs
        )
    debug = os.system(cmd)

    escape_cpu = time.thread_time() - start_cpu
    escape = time.time() - start
    print('查询{}, 耗费cpu时间: {}s'.format(query, escape_cpu))
    print('查询{}, 耗时: {}s'.format(query, escape))
    return debug

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='查询测试照片定位结果')
    parser.add_argument('query', 
        help='测试照片特征存储目录，默认为features/orb2000')
    parser.add_argument('imgs', help='坐标库目录')
    parser.add_argument('-o', '--output', default='results', metavar='Path',
        help='指定输出目录，若不存在，将被创建')
    parser.add_argument('--size', default='3000,4000', metavar='W,L', 
        help='图像像素尺寸')
    parser.add_argument('--focals', metavar='fx,fy', default='1.04127,0.780575',
        help='相机内参')
    parser.add_argument('--filter', default='homography', help='过滤器', 
        choices=['homography',''])
    args = parser.parse_args()

    m.mk_dir(args.output)

    li = m.csv2list('../gist_res.csv')

    debug = []
    for i in li:
        img1 = args.query + '/T_' + '_'.join(i[0]) +'-orb'
        img2 = args.imgs + '/A_' + '_'.join(i[1])
        temp = img2[0:len(img2)-1]
        imgs = []
        
        for i in range(const.t2.num_A.value[0]):
            imgs.append(temp + str(i+1))
        del img2

        bug = query(img1, imgs, size=args.size, focals=args.focals, filter='homography', 
            output=args.output)
        
        debug.append(bug)
    
    cout = 0
    for i in debug:
        if i == 256:
            cout += 1
    print('\n共查询{}张，成功{}张，失败{}张'.format(len(debug), len(debug)-cout, cout))