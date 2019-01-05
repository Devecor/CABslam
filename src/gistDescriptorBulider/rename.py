#!/usr/bin python3
# -*- coding: utf-8 -*-

import os
import numpy as np
import cv2 as cv
import argparse

import distanceSimilarity as ds
# import const_params as const
from const_params import num_A
from const_params import num_T
from const_params import posli

def pic_compress(input_img, output_img, factor=0.1):
    '''压缩图片，压缩倍率为factor'''
    img = cv.imread(input_img)
    assert img is not None, '输入图片路径有误，请检查！'
    img = cv.resize(img, (0,0), fx=factor, fy=factor)
    is_saved = cv.imwrite(output_img, img)
    print('save {i} to {o}'.format(i=input_img, o=output_img), end='  ')
    if is_saved:
        print('Done')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='choose if compress pics')
    parser.add_argument('-c', '--compress', default=0, action='store_const', 
        const=0.1, help='choose if compress pics')
    args = parser.parse_args()

    imglist = ds.findFile('./img', '*.jpg')
    ind = []
    for i in imglist:
        i = i.split('_')[-1].split('.')[0]
        try:
            ind.append(int(i))
        except ValueError as err:
            # print(err)
            ind.append(int(i[0:6]) + 10000)
            print('{i_0} is changed to {i_1}'.format(i_0=i, i_1=i[0:6]))
    ind = ds.distanceSort(np.array([ind]))
    imglist = [imglist[i] for i in ind]

    assert len(imglist) == num_A + num_T, '图片数量不对，请检查！'

    os.system('mkdir ./img/A')
    os.system('mkdir ./img/T')


    for i,e in enumerate(imglist):
        filePath = str(e).split('/')[0:-1]
        filePath = '/'.join(filePath)
        img_ord = i//8 + 1
        j = posli[img_ord-1]
        fileName = '_'.join(['{}'.format(i) for i in j])  + '_{}.jpg'.format(i%8 + 1)
        input_img = '\'{e}\''.format(e=e)

        if args.compress:
            if i < num_A:
                output_img = '{path}/A/A_{name}'.format(path=filePath, 
                    name=fileName)
                pic_compress(e, output_img, factor=args.compress)
            elif i < num_A+num_T:
                output_img = '{path}/T/T_{name}'.format(path=filePath, 
                    name=fileName)
                pic_compress(e, output_img, factor=args.compress)

        else:
            if i < num_A:
                os.system('cp {input_img} \'{path}/A/A_{name}\''.format(path=filePath, 
                    name=fileName, input_img=input_img))
                print('cp {input_img} \'{path}/A/A_{name}\''.format(path=filePath, 
                    name=fileName, input_img=input_img))
            elif i < num_A+num_T:
                os.system('cp {input_img} \'{path}/T/T_{name}\''.format(path=filePath, 
                    name=fileName, input_img=input_img))
                print('cp {input_img} \'{path}/T/T_{name}\''.format(path=filePath, 
                    name=fileName, input_img=input_img))