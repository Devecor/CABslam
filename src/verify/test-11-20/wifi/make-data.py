# -*- coding: utf-8 -*-
#

import argparse
import json
import logging
import os
import sys

def make_data(config):
    filename = config.filenames[0]
    if not os.path.exists(filename):
        logging.info("不存在的文件: %s", filename)
        return
    logging.info("处理输入文件: %s", filename)
    with open(filename, "r") as f:
        lines = f.readlines()

    logging.info("输入数据共 %d 行", len(lines))
    regions = []
    rcount = -1
    aps = []
    acount = 0
    data = []
    row = None
    for line in lines[1:]:
        r, t = line.split(None, 1)
        if r not in regions:
            logging.info("处理采集点 %s ", r)
            regions.append(r)
            rcount += 1
            if row is not None:
                logging.info("采集点 %s 数据处理完毕", r)
                data.append(row)
            row = {}
        ap, v = t.rsplit(None, 1)
        row[ap] = int(v)
        if ap not in aps:
            aps.append(ap)
            acount += 1
    data.append(row)

    logging.info("处理采集点: %s", regions)
    logging.info("AP 列表: %s", aps)

    logging.info("规范化输出数据")
    data2 = []
    for i in range(rcount+1):
        row = [0] * acount
        for ap in data[i]:
            row[aps.index(ap)] = data[i][ap]
        data2.append(row)

    logging.info("测试数据写入到文件: %s", config.output)
    with open(config.output, "w") as f:
        json.dump(dict(region=regions, ap=aps, data=data2), f, indent=2)

def main(params=None):
    parser = argparse.ArgumentParser(description='生成测试数据')
    parser.add_argument('filenames', metavar='FILENAME', nargs=1, help='处理过后的数据文件')
    parser.add_argument('--output', required=True, help='输出文件的名称')
    args = parser.parse_args(params)
    
    make_data(args)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    main()
