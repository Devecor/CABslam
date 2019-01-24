#!/usr/bin python3
# -*- coding: utf-8 -*-

'''
按照const_params.py中提供的数据重命名照片，可选功能为筛选、压缩

usage: rename.py [-h] [-c] [-t TN] [-p PATH]

rename and move imgs

optional arguments:
  -h, --help            show this help message and exit
  -c, --compress        choose if compress pics
  -t TN, --tn TN        choose the n times test
  -p PATH, --path PATH
'''

import numpy as np
import cv2 as cv
import argparse
import os

import const_params as const
# from const_params import num_A
# from const_params import num_T
# from const_params import posli

def pic_compress(input_img, output_img, factor=0.1):
    '''压缩图片，压缩倍率为factor'''
    img = cv.imread(input_img)
    assert img is not None, '输入图片路径有误，请检查！'
    img = cv.resize(img, (0,0), fx=factor, fy=factor)
    is_saved = cv.imwrite(output_img, img)
    return True

def findFile(path, name='*.txt'):
    '''
    搜索path下三层目录，返回文件名列表,name为正则表达式，默认值为'*.txt'
    return: list
    '''
    name = '\'{}\''.format(name)

    return os.popen('find {dir} -maxdepth 3 -name {fileName}'.format(dir=path,\
        fileName=name)).read().split('\n')[0:-1]

def distanceSort(li):
    '''间接排序，返回表示原数组的顺序的索引，而不改变原数组'''
    # print('the function distanceSort input param is {shape}'.format(
    # shape=np.shape(li)))
    assert np.shape(li)[0] == 1, 'distanceSort输入需为一维的行向量！'
    return np.argsort(li).tolist()[0]

if __name__ == '__main__':

    import timeit

    parser = argparse.ArgumentParser(description='rename and move imgs')
    parser.add_argument('-c', '--compress', default=0, action='store_const', 
        const=0.1, help='choose if compress pics')
    parser.add_argument('-t', '--tn', default='t2', 
        help='choose the n times test')
    parser.add_argument('-p', '--path', default='./test2Imgs/right')
    args = parser.parse_args()

    # 获取文件名
    imglist = findFile(args.path, '*.jpg')
    
    # 按照文件名给图片排序
    ind = []
    for i in imglist:
        i = i.split('_')[-1].split('.')[0]
        try:
            ind.append(int(i))
        except ValueError as err:
            print(err)
            ind.append(int(i[0:6]) + 10000)
            print('notice:{i_0} is changed to {i_1}'.format(i_0=i, i_1=i[0:6]))
    ind = distanceSort(np.array(np.reshape(ind,(1,-1))/1000, np.float))
    imglist = [imglist[i] for i in ind]
    del ind

    if int(args.tn[1:]) == 1:
        num_A = const.t1.num_A.value
        num_T = const.t1.num_T.value
        pos = (const.t1.pos_A.value, const.t1.pos_T.value)
    elif int(args.tn[1:]) == 2:
        num_A = const.t2.num_A.value
        num_T = const.t2.num_T.value
        pos = (const.t2.pos_A.value, const.t2.pos_T.value)
        img_filter = True
    else:
        print('test{}\'s const_params is not exit!'.format(int(args.tn[1:-1])))
    

    if img_filter:
        img_num0 = (num_A[0] + 1) * num_A[1]
        img_num1 = (num_T[0] + 1) * num_T[1] 
        img_num = img_num0 + img_num1
        assert len(imglist) == img_num, '图片数量不对，请检查！'
        imglist = [imglist[i] for i in range(img_num) 
            if not (i<img_num0 and (i+1)%(num_A[0]+1)==0 or 
            i>=img_num0 and (i-img_num0+1)%(num_T[0]+1)==0)]
        # imglist = [imglist[i] for i in range(315) if ((i<117 and (i+1)%9 != 0) or (i >= 117 and (i-116)%6 != 0))]
        del img_num, img_num0, img_num1
    else:
        assert len(imglist) == num_A[0]*num_A[1] + num_T[0]*num_T[1], \
            '图片数量不对，请检查！'

    os.system('mkdir ./{img}/A'.format(img=args.path))
    os.system('mkdir ./{img}/T'.format(img=args.path))


    fulltime = 0
    for i,e in enumerate(imglist):
        filePath = str(e).split('/')[0:-1]
        filePath = '/'.join(filePath)
        if i < num_A[0]*num_A[1]:
            temp = num_A[0]
            j = pos[0][i//temp]
            fileName = '_'.join(['{}'.format(i) for i in j])  + \
                '_{}.jpg'.format(i%temp + 1)
        else:
            temp = num_T[0]
            j = pos[1][(i-num_A[0]*num_A[1])//temp]
            fileName = '_'.join(['{}'.format(i) for i in j])  + \
                '_{}.jpg'.format((i-num_A[0]*num_A[1])%temp + 1)
        
        
        input_img = '\'{e}\''.format(e=e)

        if args.compress:
            if i < num_A[0]*num_A[1]:
                output_img = '{path}/A/A_{name}'.format(path=filePath, 
                    name=fileName)
            else:
                output_img = '{path}/T/T_{name}'.format(path=filePath, 
                    name=fileName)
            
            t = timeit.Timer(
                stmt='pic_compress(e, output_img, factor=args.compress)', 
                setup='from __main__ import pic_compress',globals=globals())
            t_ = t.timeit(number=1)
            fulltime = fulltime + t_
            print('processing {i}/{len}'.format(i=i+1, len=len(imglist)))
            print(e)
            print('used {s}s'.format(s=t_))
            print('saved to {output_img}'.format(output_img=output_img))
            print('\ncurrent total used {fulltime}s'.format(fulltime=fulltime))

        else:
            if i < num_A[0]*num_A[1]:
                os.system('cp {input_img} \'{path}/A/A_{name}\''.format(path=filePath, 
                    name=fileName, input_img=input_img))
                print('cp {input_img} \'{path}/A/A_{name}\''.format(path=filePath, 
                    name=fileName, input_img=input_img))
            else:
                os.system('cp {input_img} \'{path}/T/T_{name}\''.format(path=filePath, 
                    name=fileName, input_img=input_img))
                print('cp {input_img} \'{path}/T/T_{name}\''.format(path=filePath, 
                    name=fileName, input_img=input_img))
