#!/usr/bin python3
# -*- coding: utf-8 -*-

'''
Image similiar distance
'''
import sys
sys.path.append(r'../')

import numpy as np
import os

import const_params as const
import rename
# from const_params import correctPos
# from const_params import dist


def getSimilarity(gist0, gist1, flag=const.dist.ED.value, p=3):
    '''
    parms
    ------
    flag: Enum.dist
        ED = 0 # 欧式距离: np.sqrt(np.sum((gist0 - gist1)**2))
        MD = 1 # 曼哈顿距离: np.sum(np.fabs(gist0 - gist1))
        CD1 = 2
        CD2 = 3
        MSD = 4
        HD = 5
        MKD = 6 # 闵可夫斯基距离：对欧几里得距离及曼哈顿距离的泛化
    '''
    assert np.shape(gist0)[0] == 1 and np.shape(gist1)[0] == 1, \
        'getSimilarity 必须为一维向量'
    
    if flag == 0:
        return np.sqrt(np.sum((gist0 - gist1)**2))
    elif flag == 1:
        return np.sum(np.fabs(gist0 - gist1))
    elif flag == 6:
        return np.power(np.sum(np.power(np.fabs(gist0 - gist1), p)), 1/p)


def similaritiesMapBuilder(MapG, VecG_x):
    '''
    params
    ------
    MapG: {'posGist':[[x,y], ...], 'gists':[VecG, ...]}
    VecG_x: ([x, y], gistFeature)

    return
    ------
    simlMap: {'posGist0': [[x,y], ...],'posGist1': [[x,y], ...],
    similarities':[float, ...]} similarities是测试照片与地图库里的每张照片的相
    似度
    '''
    simlMap = []
    for i in MapG['gists']:
        simlMap.append(getSimilarity(np.array([i], np.float), \
            np.array([VecG_x[1]], np.float)))

    simlMap = {'posGist0': MapG['posGist'], 'posGist1': VecG_x[0],
               'similarities': simlMap}
    return simlMap


def similaritiesMapCollectionBuilder(MapG, testG):
    '''
    return: list_like
    '''
    SimilaritiesMapCollection = []
    for i in range(len(testG['posTest'])):
        SimilaritiesMapCollection.append(similaritiesMapBuilder(MapG,
            (testG['posTest'][i], testG['testG'][i])))

    return SimilaritiesMapCollection


# load gists to build MapG and testG
gists = []
posGist = []
testG = []
posTest = []
for i in rename.findFile('./gistFeatures'):
    fileName = str(i).split('/')[-2].split('_')
    assert len(fileName) == 4,'图片文件名不和规范，请检查！'
    [row, col, seq] = [int(i) for i in fileName[1:]]
    if fileName[0] == 'A':
        gists.append([x for x in np.loadtxt(str(i), np.float)])
        posGist.append([row, col, seq])
    elif fileName[0] == 'T':
        testG.append([x for x in np.loadtxt(str(i), np.float)])
        posTest.append([row, col, seq])
    else:
        print('findGistFile函数传入了一个错误的文件路径：{filepath}， \
                将被忽略！'.format(filepath=i))

gists = np.array(gists, np.float)
testG = np.array(testG, np.float)

MapG = {'posGist': posGist, 'gists': gists}
testG = {'posTest': posTest, 'testG': testG}

del gists, posGist, posTest

# 检所匹配，求解定位结果
# 建立相似度矩阵
similariesMapCollection = similaritiesMapCollectionBuilder(MapG, testG)
# print('similariesMapCollection is :\n{}'.format(similariesMapCollection))

# 经排序后的有序相似度矩阵
mostSimilarCollection = []
for i in similariesMapCollection:

    order = rename.distanceSort(np.array([i['similarities']], np.float))
    i['posGist0'] = [i['posGist0'][j] for j in order]
    i['similarities'] = [i['similarities'][j] for j in order]
    mostSimilarCollection.append(i)
    # print(i,end='\n############################\n')


# 打印结果
if __name__ == '__main__':
    print('序列 测试点            参考点            相似度')
correctPos = const.t2.correctPos.value
Accuracy = 0
res = []
for i,e in enumerate(mostSimilarCollection):
    if __name__ == '__main__':
        print('{i}    {e_1}     {e_0}     {similarity}'.format(i=i, \
            e_1=e['posGist1'], e_0=e['posGist0'][0], \
            similarity=e['similarities'][0]), end='')
    res.append([e['posGist1'], e['posGist0'][0:2]])
    if [e['posGist1'][0:2],e['posGist0'][0][0:2]] in correctPos:
        if __name__ == '__main__':
            print('    成功')
        Accuracy += 1
    elif __name__ == '__main__':
        print('    失败')
if __name__ == '__main__':
    print('\n成功率： {}%'.format(Accuracy * 100 / len(mostSimilarCollection)))

# 保存结果到文件
if __name__ == '__main__':
    import csv

    tocsv = [[mostSimilarCollection[i]['posGist1'], mostSimilarCollection[i]['posGist0'][0], 
        mostSimilarCollection[i]['similarities'][0]] for i in range(len(mostSimilarCollection))]
    table_header = [['测试点','测试点','相似度']]
    tocsv = table_header + tocsv
    
    with open('../gist_res.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(tocsv)