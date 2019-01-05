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

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('ord', help='path to imgDir', type=int)
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

    pic0 = 'img/T/T_{row}_{col}_{angle}.jpg'.format(
        row=rowt, col=colt, angle=anglet)
    pic1 = 'img/A/A_{row}_{col}_{angle}.jpg'.format(
        row=rowa, col=cola, angle=anglea)
    print(pic0)
    print(pic1)
    pair_imshow(pic0, pic1)