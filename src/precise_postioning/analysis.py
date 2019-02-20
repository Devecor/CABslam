#!/usr/bin python3
# -*- coding: utf-8 -*-

'''
Info
------
__author__: devecor
'''

import csv

import sys
sys.path.append('../')
import rename as ra

def files2li(path,name='*.txt'):
    textli = ra.findFile(path, name='*.txt')

    res = []
    for i in textli:
        with open(i, 'r', newline='') as f:
            res.append(f.readline().split())
    return res

def li2csv(li, outpath, title=None):
    assert isinstance(outpath, str), 'tupeError: li is not str'

    if title != None and len(li[0]) != len(title):
        print('warning: 表宽与标题宽不一致')

    with open(outpath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(title)
        for i in li:
            writer.writerow(i)

def li2text(li, outpath, title=None):
    assert isinstance(outpath, str), 'tupeError: li is not str'

    if title != None and len(li[0]) != len(title):
        print('warning: 表宽与标题宽不一致')

    with open(outpath, 'w', newline='') as file:
        file.write('\t'.expandtabs().join(title) + '\n')
        for i in li:
            file.write(' '.join(i))
            file.write('\n')

if __name__ == '__main__':
    li = files2li('results')
    title = ['TP','Time(ms)','No.','Angle','X','Y','Total']
    li2csv(li, 'orb_res.csv', title=title)
    li2text(li, 'orb_res.txt', title=title)