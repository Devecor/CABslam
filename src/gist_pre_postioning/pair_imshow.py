#! /usr/bin python3
# -*- coding:utf-8  -*-

'''
usage:
    show_pics
'''
import cv2 as cv
from matplotlib import pyplot as plt
import argparse

from distanceSimilarity import res

def pair_imshow(path0='demo1.jpg', path1='demo2.jpg'):
    img0 = cv.imread(path0)
    img1 = cv.imread(path1)
    plt.subplot(121)
    plt.imshow(img0)
    plt.subplot(122)
    plt.imshow(img1)
    plt.show()
    return True

def mult_imshow(pathlist,row=1,col=-1):
    img_n = len(pathlist)
    check = [i for i in pathlist if isinstance(i,str)]

    assert img_n==0 and len(check)==img_n, 'mult_imshow: 图片列表不合法！'

    if row==1 or col==-1:
        col = img_n

    assert row*col >= img_n, '区块数必须大于或等于图片数'

    for i in range(img_n):
        plt.subplot([row,col,i])
        plt.imshow(cv.imread(pathlist[i]))
    plt.show()
    return True

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('ord', help='path to imgDir', type=int)
parser.add_argument('-p','--path',default='test2Imgs/right')
# parser.add_argument('--img_li', default=res)
args = parser.parse_args()

if __name__ == '__main__':
    rowt,colt,anglet = res[args.ord][0]
    rowa,cola,anglea = res[args.ord][1]
    try:
        rowt,colt,anglet = res[args.ord][0]
        rowa,cola,anglea = res[args.ord][1]
    except NameError as err:
        print(err)

    pic0 = '{img}/T/T_{row}_{col}_{angle}.jpg'.format(
        row=rowt, col=colt, angle=anglet, img=args.path)
    pic1 = '{img}/A/A_{row}_{col}_{angle}.jpg'.format(
        row=rowa, col=cola, angle=anglea, img=args.path)
    print(pic0)
    print(pic1)
    pair_imshow(pic0, pic1)