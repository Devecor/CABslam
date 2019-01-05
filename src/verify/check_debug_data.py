# -*- coding: utf-8 -*-

import argparse
import json
import logging
import os
import sys

import numpy as np
import cv2 as cv

def loadJson(filename):
	with open(filename) as f:
		locationResult = json.load(f)
		return locationResult

def draw_str(dst, target, s):
	x, y = target
	cv.putText(dst, s, (x+10, y+10), cv.FONT_HERSHEY_PLAIN, 10.0, (0, 255, 0), thickness = 10, lineType=cv.FILLED)

def explore_match(imgPath, refImgPath, kp1, kp2):
	img = cv.imread(imgPath, 0)
	refImg = cv.imread(refImgPath, 0)
	h1, w1 = img.shape[:2]
	h2, w2 = refImg.shape[:2]
	vis = np.zeros((max(h1, h2), w1+w2), np.uint8)
	vis[:h1, :w1] = img
	vis[:h2, w1:w1+w2] = refImg
	vis = cv.cvtColor(vis, cv.COLOR_GRAY2BGR)
	for i in range(0, len(kp2)):
		kp2[i][0] = kp2[i][0] + w1
	green = (0, 255, 0)
	red = (0, 0, 255)
	white = (255, 255, 255)
	kp_color = (51, 103, 236)
	for pos1, pos2 in zip(kp1, kp2) :
		cv.circle(vis, (int(pos1[0]), int(pos1[1])), 3, red, -1)
		cv.circle(vis, (int(pos2[0]), int(pos2[1])), 3, red, -1)
		cv.line(vis, (int(pos1[0]), int(pos1[1])), (int(pos2[0]), int(pos2[1])), green, 2)
	draw_str(vis, (100, 200), str(len(kp1)))
	return vis

def main(params = None):
	parser = argparse.ArgumentParser(description = '检查定位结果数据')
	parser.add_argument('filename', help = '查询定位结果debug文件')
	parser.add_argument('imgDirPath', help = '测试图片存储位置')
	parser.add_argument('refImgDirPath', help = '参考图片存储位置')
	parser.add_argument('--show', action='store_true', help='在窗口中显示匹配结果')
	parser.add_argument('--imgSuffix', '-is', default = '.jpg', help = '照片后缀名')
	parser.add_argument('--refImgSuffix', '-rs', default = '.jpg', help = '参考照片后缀名')
	parser.add_argument('--save', action='store_true', help='是否保存匹配结果')
	parser.add_argument('--outputDirPath', '-o', default = './', help='输出文件的路径')
	args = parser.parse_args(params)
	locationResult = loadJson(args.filename)
	imgPath = os.path.join(args.imgDirPath, locationResult['image']['url'] + args.imgSuffix)
	refImgPath = os.path.join(args.refImgDirPath, locationResult['refimage']['url'] + args.refImgSuffix)
	kp1 = locationResult['image']['points']
	kp2 = locationResult['refimage']['points']
	result = explore_match(imgPath, refImgPath, kp1, kp2)
	if args.show:
		w, h = result.shape[:2]
		img = cv.resize(result, (w/4, h/8))
		cv.imshow('image', img)
		cv.waitKey(0)
	if args.save:
		name = '%s-%s.jpg' % (locationResult['image']['url'], locationResult['refimage']['url'])
		name = os.path.join(args.outputDirPath, name)
		if os.path.exists(args.outputDirPath) == False:
			logging.error('%s 目录不存在', args.outputDirPath)
			return
		cv.imwrite(name, result)

if __name__ == '__main__':
	logging.basicConfig(format='%(asctime)s %(message)s', level = logging.INFO)
	main()




