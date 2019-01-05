# 实验 11-20 测试结果

## 特征匹配

特征点结果图片存放在 features 目录下面

- 2000个 ORB 关键点 [features/orb-2000](features/orb-2000)
- 5000个 ORB 关键点 [features/orb-2000](features/orb-5000)
- 8000个 ORB 关键点 [features/orb-2000](features/orb-8000)

例如 1-1.JPG 对应的关键点结果图片分别为

- [features/orb-2000/1-1-orb.jpg](features/orb-2000/1-1-orb.jpg)
- [features/orb-5000/1-1-orb.jpg](features/orb-5000/1-1-orb.jpg)
- [features/orb-8000/1-1-orb.jpg](features/orb-8000/1-1-orb.jpg)

匹配结果存放在 matches 目录下面

- 2000个 ORB 关键点匹配结果 [matches/orb-h2000](matches/orb-h2000)
- 5000个 ORB 关键点匹配结果 [matches/orb-h2000](matches/orb-h5000)
- 8000个 ORB 关键点匹配结果 [matches/orb-h2000](matches/orb-h8000)

例如 5-1.JPG 和 1-1.JPG 使用 2000 个 关键点的匹配结果图片

- [matches/orb-h2000/5-1-1-1.jpg](matches/orb-h2000/5-1-1-1.jpg)

匹配结果数据汇总结果

- [match-result-orb-2000.txt](match-result-orb-2000.txt)
- [match-result-orb-5000.txt](match-result-orb-5000.txt)
- [match-result-orb-8000.txt](match-result-orb-8000.txt)

每一行的格式如下

```
  IMG-1  IMG-2  unique     inlier     outlier
  5-1    1-1    4          8          61

  IMG-1: 图片1
  IMG-2: 图片2
  unique: 除去相同关键点之后的匹配数目
  inlier: 匹配点总数目（使用Homography过滤）
  outlier: 原始的匹配数目（经过 k-flann 和 关键点 distance 进行简单过滤）

```

## Wifi 匹配

处理原始数据，存放在 data2/ 下面的所有 txt 文件，保存的是每一个 ap 的平均值

```
  gawk -f wifi/handle-raw-data.awk $(find ./data2 -name "*.txt") > wifi/data/wifi-input.txt
```

生成 json 的 wifi 数据

```
  C:/Python27/python wifi/make-data.py --output wifi/data/wifi-data.json wifi/data/wifi-input.txt
```

处理 测试点的原始数据，存放在 test2/ 下面的所有 txt 文件

```
  gawk -f wifi/handle-raw-data.awk $(find ./test2 -name "t*.txt") > wifi/data/test-input.txt
```

输入测试点的期望结果，存放在 wifi/data/test-base.txt，内容如下

```
t1 1
t2 5
t3 5
t4 5
t5 6
t6 2
t7 3
t8 3
t9 3
t10 3
```

? t3 距离采集点 1 和 5 相差不多，暂时选取的是 5
? t5 距离采集点 2 和 6 相差不多，暂时选取的是 6

生成测试点的 json 数据

```
  C:/Python27/python wifi/make-test.py --output wifi/data/test-data.json --base wifi/data/test-base.txt wifi/data/wifi-test.txt
```


### 实验数据一

只使用两个为本次实验配置的AP进行匹配，执行下面的命令

```
  C:/Python27/python wifi/query.py --data wifi/data/wifi-data.json \
                                   --base wifi/data/test-base.txt \
                                   --filters="TP-LINK_C866,TP-LINK_A970D6" \
                                   --output wifi-result-1.txt \
                                   wifi/data/test-input.txt
```

输出结果在 [wifi-result-1.txt](wifi-result-1.txt)

### 实验数据二

使用测试点全部的AP数据进行匹配，执行下面的命令

```
  C:/Python27/python wifi/query.py --data wifi/data/wifi-data.json \
                                   --base wifi/data/test-base.txt \
                                   --output wifi-result-2.txt \
                                   wifi/data/test-input.txt
```

输出结果在 [wifi-result-2.txt](wifi-result-2.txt)
