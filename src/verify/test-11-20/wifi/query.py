# -*- coding: utf-8 -*-
#

import argparse
import json
import logging
import os
import sys

import numpy as np

def query_region(config):
    logging.info("读取Wifi指纹数据库文件 %s", config.data)
    with open(config.data, "r") as f:
        data = json.load(f)

    regions = data['region']
    aps = data['ap']
    fdata = np.float64(data['data'])

    if config.filters:
        faps = config.filters.split(',')        
        logging.info("使用过滤后的 AP 进行定位：%s", faps)
        ai = []
        for ap in faps:
            if ap not in aps:
                logging.info("AP 在Wifi数据库中不存在：", ap)
                return
            ai.append(aps.index(ap))
        aps = faps
        fdata = np.float64(data['data']).take(ai, axis=1)
    acount = len(aps)

    # print "Wifi 指纹数据库："
    # print "%-10s %-15s %-15s" % ("采集点", aps[0], aps[1])
    # for i in range(len(regions)):        
    #     print "%-10s %-15s %-15s" % (regions[i], fdata[i][0], fdata[i][1])

    filename = config.filenames[0]
    logging.info("处理输入文件: %s", filename)
    with open(filename, "r") as f:
        lines = f.readlines()
    logging.info("输入数据共 %d 行", len(lines))
    tpoints = []
    tcount = -1
    tdata = []
    for line in lines[1:]:
        r, t = line.split(None, 1)
        if r not in tpoints:
            logging.info("处理测试点 %s ", r)
            tpoints.append(r)
            tcount += 1
            if tcount > 0:
                logging.info("测试点 %s 数据处理完毕", r)
                tdata.append(row)
            row = [0] * acount
        ap, v = t.rsplit(None, 1)
        try:
            index = aps.index(ap)
        except ValueError:
            if not config.filters: 
                logging.info("采集点 %s 的 AP %s 没有在数据库中发现，忽略这个值", r, ap)
        else:
            row[index] = int(v)
    tdata.append(row)
    
    logging.info("处理测试点: %s", tpoints)
    logging.info("开始查询定位")
    result = {}
    # logging.info("FP 数据: %s", fdata)
    # logging.info("AP is: %s", aps)
    for i in range(tcount+1):
        row = np.float64(tdata[i])
        # print "测试点 %s 数据： %s" % (tpoints[i], row)
        # print "欧几里得距离:"
        # d = np.linalg.norm(fdata - row, axis=1)
        # for j in range(len(regions)):        
        #     print "%-10s %-s" % (regions[j], d[j])        
        d = np.argsort(np.linalg.norm(fdata - row, axis=1))
        result[tpoints[i]] = regions[d[0]], regions[d[1]], regions[d[2]]
        # print "测试点 {0} 的备选区域: {1}".format(tpoints[i], regions[d[0]])
    return result

def compare_result(config):
    pass

def main(params=None):
    parser = argparse.ArgumentParser(description='Wifi指纹定位')
    parser.add_argument('filenames', metavar='FILENAME', nargs=1, help='包含多个测试点的Wifi指纹数据，经过处理过后的数据文件')
    parser.add_argument('--output', required=False, help='输出文件的名称')
    parser.add_argument('--data', required=True, help='Wifi指纹数据库，json文件')
    parser.add_argument('--base', required=True, help='测试点期望结果')
    parser.add_argument('--filters', help='使用部分AP进行匹配')
    args = parser.parse_args(params)

    np.set_printoptions(suppress=True)

    for filename in [args.filenames[0], args.data, args.base]:
        if not os.path.exists(filename):
            logging.info("不存在的输入文件: %s", filename)
            return

    result = query_region(args)
    with open(args.base, "r") as f:
        lines = f.readlines()
    output = ['%-10s %-10s %-s' % ("测试点", "期望结果", "计算结果")]
    for line in lines:
        if line.strip() == "":
            continue
        tp, pt = line.split()
        output.append("%-10s %-10s %-s" % (tp, pt, str(" ".join(result[tp]))))
    logging.info("计算结果:\n %s", "\n".join(output))
    logging.info("计算结果保存到文件: %s", args.output)
    with open(args.output, "w") as f:
        f.write("\n".join(output))

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    main()
