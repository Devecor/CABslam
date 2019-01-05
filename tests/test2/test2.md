# 实验二测试结果

# 鲁棒性

将[robust](robust)中[11](robust/11.png)-[44](robust/44.png) 图片和[原图](robust/00.jpg)进行特征提取、匹配。原图用 asift+orb，11-44用orb。试下不同的最多特征点个数，记录特征点的匹配个数，和匹配时间。

## [orb 参数](http://docs.opencv.org/3.2.0/db/d95/classcv_1_1ORB.html)

* nfeatures = 测试参数

    The maximum number of features to retain.

* scaleFactor = 1.2

    Pyramid decimation ratio, greater than 1. scaleFactor==2 means the classical pyramid, where each next level has 4x less pixels than the previous, but such a big scale factor will degrade feature matching scores dramatically. On the other hand, too close to 1 scale factor will mean that to cover certain scale range you will need more pyramid levels and so the speed will suffer.

* nlevels = 8

    The number of pyramid levels. The smallest level will have linear size equal to input_image_linear_size/pow(scaleFactor, nlevels).

* edgeThreshold = 31

    This is size of the border where the features are not detected. It should roughly match the patchSize parameter.

* firstLevel = 0

    It should be 0 in the current implementation.

* WTA_K = 2

    The number of points that produce each element of the oriented BRIEF descriptor. The default value 2 means the BRIEF where we take a random point pair and compare their brightnesses, so we get 0/1 response. Other possible values are 3 and 4. For example, 3 means that we take 3 random points (of course, those point coordinates are random, but they are generated from the pre-defined seed, so each element of BRIEF descriptor is computed deterministically from the pixel rectangle), find point of maximum brightness and output index of the winner (0, 1 or 2). Such output will occupy 2 bits, and therefore it will need a special variant of Hamming distance, denoted as NORM_HAMMING2 (2 bits per bin). When WTA_K=4, we take 4 random points to compute each bin (that will also occupy 2 bits with possible values 0, 1, 2 or 3).

* scoreType = ORB::HARRIS_SCORE

    The default HARRIS_SCORE means that Harris algorithm is used to rank features (the score is written to KeyPoint::score and is used to retain best nfeatures features); FAST_SCORE is alternative value of the parameter that produces slightly less stable keypoints, but it is a little faster to compute.

* patchSize = 31

    size of the patch used by the oriented BRIEF descriptor. Of course, on smaller pyramid layers the perceived image area covered by a feature will be larger.

* fastThreshold = 20

## asift 取样参数

取样 43 次，其数值 (tilt, phi) 分别为

```
    (1.0, 0.0)
    (1.41,  0)
    (1.41, 51)
    (1.41, 102)
    (1.41, 153)
    (2.00,  0)
    (2.00, 36)
    (2.00, 72)
    (2.00, 108)
    (2.00, 144)
    (2.83,  0)
    (2.83, 25)
    (2.83, 51)
    (2.83, 76)
    (2.83, 102)
    (2.83, 127)
    (2.83, 153)
    (2.83, 178)
    (4.00,  0)
    (4.00, 18)
    (4.00, 36)
    (4.00, 54)
    (4.00, 72)
    (4.00, 90)
    (4.00, 108)
    (4.00, 126)
    (4.00, 144)
    (4.00, 162)
    (5.66,  0)
    (5.66, 13)
    (5.66, 25)
    (5.66, 38)
    (5.66, 51)
    (5.66, 64)
    (5.66, 76)
    (5.66, 89)
    (5.66, 102)
    (5.66, 115)
    (5.66, 127)
    (5.66, 140)
    (5.66, 153)
    (5.66, 165)
    (5.66, 178)

```
## FLANN 匹配算法参数

* algorithm = FLANN_INDEX_LSH,
* table_number = 6
* key_size = 12
* multi_probe_level = 1

## 测试结果

查询照片的最多关键点数目分别为 1000,2000,3000,4000,5000,6000,7000,8000,9000,100000，对应于结果表格中查询参数

测试结果表格参数说明

* 查询参数        查询照片的最多关键点数目
* 取样数目        使用 asift + orb 算法时候每一次取样获取的最多关键点数目
* 取样次数        使用 asift + orb 算法的取样次数，目前都是 43
* 关键点数        查询获取到的图片的关键点数目
* 查询时间        获取照片关键点花费的时间，单位为毫秒
* 匹配时间        匹配原图关键点花费的时间，单位为毫秒
* 匹配个数        inlier / matcher

原图的查询时间第一次为使用 asift 实际消耗的时间，后面的是取保存的数据花费的时间。

在浏览器里面表格标题可能会对不齐，可以直接用文本工具查看文件 [results/robust/result.txt](results/robust/result.txt)

### 测试数据
```
         __________原图__________  __________________11__________________  __________________22__________________  __________________33__________________  __________________44__________________ 
查询参数 原图取样 查询时间 关键点数 查询时间 关键点数 匹配时间 匹配数目     查询时间 关键点数 匹配时间 匹配数目     查询时间 关键点数 匹配时间 匹配数目     查询时间 关键点数 匹配时间 匹配数目     
1000       500    32914.9   21500     36.7     1000    425.5   32 / 248       39.4     1000    315.6   184 / 453      30.3     996     409.5   22 / 199       33.7     1000    322.7   124 / 367    
1000       1000   32269.9   43000     37.2     1000    726.9   79 / 605       39.0     1000    583.7   304 / 915      29.8     996     694.4   64 / 560       35.0     1000    613.4   284 / 839    
1000       2000   33552.7   86000     37.1     1000    1280.8  167 / 1219     39.2     1000    1207.4  569 / 1515     30.1     996     1268.5  204 / 1196     34.4     1000    1234.5  481 / 1594   
2000       500      90.1    21500     43.3     2000    568.8   13 / 199       45.5     2000    471.2   143 / 339      32.3     1438    484.6   18 / 229       39.8     2000    448.5   110 / 318    
2000       1000    176.6    43000     43.3     2000    1015.2  56 / 408       46.8     2000    941.1   265 / 670      32.2     1438    857.4   41 / 451       40.5     2000    978.5   210 / 590    
2000       2000    343.2    86000     43.3     2000    1962.7  189 / 951      46.8     2000    1800.9  465 / 1394     32.6     1438    1433.5  126 / 1141     41.2     2000    1801.6  409 / 1320   
3000       500      91.3    21500     49.5     2941    722.1   18 / 171       52.4     3000    572.6   133 / 327      33.1     1438    494.4   20 / 214       45.8     3000    630.0   83 / 236     
3000       1000    173.7    43000     48.0     2941    1211.0  48 / 387       52.0     3000    1228.4  258 / 638      32.2     1438    887.3   45 / 442       46.8     3000    1203.3  156 / 490    
3000       2000    344.3    86000     48.3     2941    2401.8  172 / 835      52.8     3000    2212.6  445 / 1263     32.3     1438    1531.6  146 / 1057     45.7     3000    2504.3  355 / 1080   
4000       500      91.7    21500     52.3     3640    849.4   22 / 179       58.2     3999    705.7   128 / 303      32.3     1438    487.5   15 / 216       50.0     3877    731.3   74 / 232     
4000       1000    174.7    43000     51.8     3640    1434.6  63 / 371       57.7     3999    1600.9  215 / 585      34.0     1438    852.4   42 / 458       50.4     3877    1435.2  174 / 490    
4000       2000    349.9    86000     51.2     3640    3089.4  162 / 779      57.7     3999    2964.2  387 / 1201     32.3     1438    1506.6  118 / 1091     49.7     3877    3036.7  310 / 971    
5000       500      89.6    21500     52.6     3984    797.7   18 / 179       60.7     4877    831.0   119 / 269      32.4     1438    487.9   19 / 211       53.0     4534    866.0   70 / 224     
5000       1000    174.4    43000     52.9     3984    1529.2  72 / 388       61.1     4877    1670.4  222 / 571      32.5     1438    835.6   52 / 486       52.8     4534    1729.1  139 / 427    
5000       2000    343.2    86000     52.6     3984    2905.1  144 / 802      61.0     4877    3527.6  380 / 1063     32.1     1438    1545.1  142 / 1138     52.8     4534    3048.1  302 / 923    
6000       500      89.5    21500     53.7     3984    834.6   23 / 176       64.1     5528    890.6   111 / 272      32.3     1438    490.2   19 / 212       54.2     4861    941.2   71 / 237     
6000       1000    172.9    43000     53.4     3984    1519.0  46 / 379       64.2     5528    1715.9  229 / 536      34.6     1438    830.5   44 / 475       54.9     4861    1786.6  154 / 418    
6000       2000    342.2    86000     53.3     3984    3226.6  144 / 824      66.1     5528    3276.8  378 / 1004     32.4     1438    1611.9  113 / 1036     55.0     4861    3395.9  330 / 992    
7000       500      91.1    21500     53.3     3984    839.4   16 / 166       66.8     5879    883.5   127 / 289      33.7     1438    490.3   20 / 210       54.4     4861    897.2   79 / 234     
7000       1000    173.7    43000     52.8     3984    1575.2  49 / 398       65.7     5879    1972.0  192 / 538      32.6     1438    799.4   45 / 520       54.5     4861    1724.7  142 / 438    
7000       2000    359.1    86000     65.9     3984    3196.6  160 / 826      65.8     5879    3959.4  372 / 968      32.1     1438    1640.8  117 / 1037     61.1     4861    3711.0  323 / 991    
8000       500      92.9    21500     53.2     3984    887.6   13 / 167       67.9     5879    923.5   127 / 275      32.7     1438    485.5   17 / 220       58.4     4861    867.3   81 / 231     
8000       1000    174.8    43000     53.7     3984    1605.9  46 / 393       65.6     5879    1493.1  194 / 520      32.5     1438    808.7   44 / 556       55.2     4861    1560.9  156 / 470    
8000       2000    345.8    86000     53.0     3984    3046.9  158 / 815      65.8     5879    3804.9  375 / 976      32.7     1438    1556.1  151 / 1098     54.5     4861    3488.2  305 / 916    
9000       500      90.0    21500     53.3     3984    859.6   13 / 184       65.6     5879    896.9   130 / 277      32.9     1438    470.4   20 / 232       57.4     4861    885.9   78 / 229     
9000       1000    173.5    43000     52.9     3984    1600.6  76 / 392       65.8     5879    1662.9  194 / 547      33.3     1438    833.7   41 / 495       55.0     4861    1766.5  162 / 433    
9000       2000    341.4    86000     53.0     3984    2875.6  127 / 825      66.2     5879    3409.0  373 / 1011     32.6     1438    1514.3  147 / 1130     56.8     4861    3309.2  334 / 958    
10000      500      90.7    21500     53.0     3984    867.0   20 / 165       65.9     5879    985.2   117 / 250      32.4     1438    481.4   15 / 218       54.2     4861    851.5   81 / 232     
10000      1000    172.0    43000     53.3     3984    1579.8  44 / 402       67.0     5879    2005.1  208 / 492      35.7     1438    842.9   53 / 488       54.6     4861    1531.4  156 / 468    
10000      2000    338.8    86000     53.0     3984    3184.2  163 / 813      66.2     5879    3126.6  375 / 981      32.4     1438    1630.0  127 / 1041     54.4     4861    3767.8  287 / 940    
```

### 图片匹配结果

* [R1000-A500-11](results/robust/orb-1000-asift-500-11.jpg)
* [R1000-A500-22](results/robust/orb-1000-asift-500-22.jpg)
* [R1000-A500-33](results/robust/orb-1000-asift-500-33.jpg)
* [R1000-A500-44](results/robust/orb-1000-asift-500-44.jpg)
* [R1000-A1000-11](results/robust/orb-1000-asift-1000-11.jpg)
* [R1000-A1000-22](results/robust/orb-1000-asift-1000-22.jpg)
* [R1000-A1000-33](results/robust/orb-1000-asift-1000-33.jpg)
* [R1000-A1000-44](results/robust/orb-1000-asift-1000-44.jpg)
* [R1000-A2000-11](results/robust/orb-1000-asift-2000-11.jpg)
* [R1000-A2000-22](results/robust/orb-1000-asift-2000-22.jpg)
* [R1000-A2000-33](results/robust/orb-1000-asift-2000-33.jpg)
* [R1000-A2000-44](results/robust/orb-1000-asift-2000-44.jpg)
* [R2000-A500-11](results/robust/orb-2000-asift-500-11.jpg)
* [R2000-A500-22](results/robust/orb-2000-asift-500-22.jpg)
* [R2000-A500-33](results/robust/orb-2000-asift-500-33.jpg)
* [R2000-A500-44](results/robust/orb-2000-asift-500-44.jpg)
* [R2000-A1000-11](results/robust/orb-2000-asift-1000-11.jpg)
* [R2000-A1000-22](results/robust/orb-2000-asift-1000-22.jpg)
* [R2000-A1000-33](results/robust/orb-2000-asift-1000-33.jpg)
* [R2000-A1000-44](results/robust/orb-2000-asift-1000-44.jpg)
* [R2000-A2000-11](results/robust/orb-2000-asift-2000-11.jpg)
* [R2000-A2000-22](results/robust/orb-2000-asift-2000-22.jpg)
* [R2000-A2000-33](results/robust/orb-2000-asift-2000-33.jpg)
* [R2000-A2000-44](results/robust/orb-2000-asift-2000-44.jpg)
* [R3000-A500-11](results/robust/orb-3000-asift-500-11.jpg)
* [R3000-A500-22](results/robust/orb-3000-asift-500-22.jpg)
* [R3000-A500-33](results/robust/orb-3000-asift-500-33.jpg)
* [R3000-A500-44](results/robust/orb-3000-asift-500-44.jpg)
* [R3000-A1000-11](results/robust/orb-3000-asift-1000-11.jpg)
* [R3000-A1000-22](results/robust/orb-3000-asift-1000-22.jpg)
* [R3000-A1000-33](results/robust/orb-3000-asift-1000-33.jpg)
* [R3000-A1000-44](results/robust/orb-3000-asift-1000-44.jpg)
* [R3000-A2000-11](results/robust/orb-3000-asift-2000-11.jpg)
* [R3000-A2000-22](results/robust/orb-3000-asift-2000-22.jpg)
* [R3000-A2000-33](results/robust/orb-3000-asift-2000-33.jpg)
* [R3000-A2000-44](results/robust/orb-3000-asift-2000-44.jpg)
* [R4000-A500-11](results/robust/orb-4000-asift-500-11.jpg)
* [R4000-A500-22](results/robust/orb-4000-asift-500-22.jpg)
* [R4000-A500-33](results/robust/orb-4000-asift-500-33.jpg)
* [R4000-A500-44](results/robust/orb-4000-asift-500-44.jpg)
* [R4000-A1000-11](results/robust/orb-4000-asift-1000-11.jpg)
* [R4000-A1000-22](results/robust/orb-4000-asift-1000-22.jpg)
* [R4000-A1000-33](results/robust/orb-4000-asift-1000-33.jpg)
* [R4000-A1000-44](results/robust/orb-4000-asift-1000-44.jpg)
* [R4000-A2000-11](results/robust/orb-4000-asift-2000-11.jpg)
* [R4000-A2000-22](results/robust/orb-4000-asift-2000-22.jpg)
* [R4000-A2000-33](results/robust/orb-4000-asift-2000-33.jpg)
* [R4000-A2000-44](results/robust/orb-4000-asift-2000-44.jpg)
* [R5000-A500-11](results/robust/orb-5000-asift-500-11.jpg)
* [R5000-A500-22](results/robust/orb-5000-asift-500-22.jpg)
* [R5000-A500-33](results/robust/orb-5000-asift-500-33.jpg)
* [R5000-A500-44](results/robust/orb-5000-asift-500-44.jpg)
* [R5000-A1000-11](results/robust/orb-5000-asift-1000-11.jpg)
* [R5000-A1000-22](results/robust/orb-5000-asift-1000-22.jpg)
* [R5000-A1000-33](results/robust/orb-5000-asift-1000-33.jpg)
* [R5000-A1000-44](results/robust/orb-5000-asift-1000-44.jpg)
* [R5000-A2000-11](results/robust/orb-5000-asift-2000-11.jpg)
* [R5000-A2000-22](results/robust/orb-5000-asift-2000-22.jpg)
* [R5000-A2000-33](results/robust/orb-5000-asift-2000-33.jpg)
* [R5000-A2000-44](results/robust/orb-5000-asift-2000-44.jpg)
* [R6000-A500-11](results/robust/orb-6000-asift-500-11.jpg)
* [R6000-A500-22](results/robust/orb-6000-asift-500-22.jpg)
* [R6000-A500-33](results/robust/orb-6000-asift-500-33.jpg)
* [R6000-A500-44](results/robust/orb-6000-asift-500-44.jpg)
* [R6000-A1000-11](results/robust/orb-6000-asift-1000-11.jpg)
* [R6000-A1000-22](results/robust/orb-6000-asift-1000-22.jpg)
* [R6000-A1000-33](results/robust/orb-6000-asift-1000-33.jpg)
* [R6000-A1000-44](results/robust/orb-6000-asift-1000-44.jpg)
* [R6000-A2000-11](results/robust/orb-6000-asift-2000-11.jpg)
* [R6000-A2000-22](results/robust/orb-6000-asift-2000-22.jpg)
* [R6000-A2000-33](results/robust/orb-6000-asift-2000-33.jpg)
* [R6000-A2000-44](results/robust/orb-6000-asift-2000-44.jpg)
* [R7000-A500-11](results/robust/orb-7000-asift-500-11.jpg)
* [R7000-A500-22](results/robust/orb-7000-asift-500-22.jpg)
* [R7000-A500-33](results/robust/orb-7000-asift-500-33.jpg)
* [R7000-A500-44](results/robust/orb-7000-asift-500-44.jpg)
* [R7000-A1000-11](results/robust/orb-7000-asift-1000-11.jpg)
* [R7000-A1000-22](results/robust/orb-7000-asift-1000-22.jpg)
* [R7000-A1000-33](results/robust/orb-7000-asift-1000-33.jpg)
* [R7000-A1000-44](results/robust/orb-7000-asift-1000-44.jpg)
* [R7000-A2000-11](results/robust/orb-7000-asift-2000-11.jpg)
* [R7000-A2000-22](results/robust/orb-7000-asift-2000-22.jpg)
* [R7000-A2000-33](results/robust/orb-7000-asift-2000-33.jpg)
* [R7000-A2000-44](results/robust/orb-7000-asift-2000-44.jpg)
* [R8000-A500-11](results/robust/orb-8000-asift-500-11.jpg)
* [R8000-A500-22](results/robust/orb-8000-asift-500-22.jpg)
* [R8000-A500-33](results/robust/orb-8000-asift-500-33.jpg)
* [R8000-A500-44](results/robust/orb-8000-asift-500-44.jpg)
* [R8000-A1000-11](results/robust/orb-8000-asift-1000-11.jpg)
* [R8000-A1000-22](results/robust/orb-8000-asift-1000-22.jpg)
* [R8000-A1000-33](results/robust/orb-8000-asift-1000-33.jpg)
* [R8000-A1000-44](results/robust/orb-8000-asift-1000-44.jpg)
* [R8000-A2000-11](results/robust/orb-8000-asift-2000-11.jpg)
* [R8000-A2000-22](results/robust/orb-8000-asift-2000-22.jpg)
* [R8000-A2000-33](results/robust/orb-8000-asift-2000-33.jpg)
* [R8000-A2000-44](results/robust/orb-8000-asift-2000-44.jpg)
* [R9000-A500-11](results/robust/orb-9000-asift-500-11.jpg)
* [R9000-A500-22](results/robust/orb-9000-asift-500-22.jpg)
* [R9000-A500-33](results/robust/orb-9000-asift-500-33.jpg)
* [R9000-A500-44](results/robust/orb-9000-asift-500-44.jpg)
* [R9000-A1000-11](results/robust/orb-9000-asift-1000-11.jpg)
* [R9000-A1000-22](results/robust/orb-9000-asift-1000-22.jpg)
* [R9000-A1000-33](results/robust/orb-9000-asift-1000-33.jpg)
* [R9000-A1000-44](results/robust/orb-9000-asift-1000-44.jpg)
* [R9000-A2000-11](results/robust/orb-9000-asift-2000-11.jpg)
* [R9000-A2000-22](results/robust/orb-9000-asift-2000-22.jpg)
* [R9000-A2000-33](results/robust/orb-9000-asift-2000-33.jpg)
* [R9000-A2000-44](results/robust/orb-9000-asift-2000-44.jpg)
* [R10000-A500-11](results/robust/orb-10000-asift-500-11.jpg)
* [R10000-A500-22](results/robust/orb-10000-asift-500-22.jpg)
* [R10000-A500-33](results/robust/orb-10000-asift-500-33.jpg)
* [R10000-A500-44](results/robust/orb-10000-asift-500-44.jpg)
* [R10000-A1000-11](results/robust/orb-10000-asift-1000-11.jpg)
* [R10000-A1000-22](results/robust/orb-10000-asift-1000-22.jpg)
* [R10000-A1000-33](results/robust/orb-10000-asift-1000-33.jpg)
* [R10000-A1000-44](results/robust/orb-10000-asift-1000-44.jpg)
* [R10000-A2000-11](results/robust/orb-10000-asift-2000-11.jpg)
* [R10000-A2000-22](results/robust/orb-10000-asift-2000-22.jpg)
* [R10000-A2000-33](results/robust/orb-10000-asift-2000-33.jpg)
* [R10000-A2000-44](results/robust/orb-10000-asift-2000-44.jpg)

# 准确度

测试坐标系单位为厘米（cm），原点在位置1

* x 轴为相机右方
* y 轴朝下
* z 轴为相机前方

拍摄点的坐标和角度

* 1:    0度  (0,     0,    0)
* 2:    0度 （0,     0, -100)
* 3:  -30度 （115,   0,    0)
* 4:  -60度 （200,   0,    0)
* 5:   30度 （-115,  0,    0)
* 6:   60度 （-200,  0,    0)

[原图](accuracy/1.jpg)采用asift+orb算法获取关键点，每次取样最多关键点数目为 500，查询照片使用orb算法，最多关键点数目分别为 2000,5000,8000


## 测试结果

测试结果表格参数说明

* 查询时间    查询关键点花费的时间，毫秒
* 匹配时间    匹配关键点花费的实际，毫秒
* 匹配数目    inlier / matcher
* 角度/位置   计算结果，角度为度数，位置单位为厘米
* 期望结果    实际拍摄位置
* 误差        计算结果减去期望结果

在浏览器里面表格标题可能会对不齐，可以直接用文本工具查看文件 [results/accuracy/result.txt](results/accuracy/result.txt)

[原图](accuracy/1.jpg)关键点数目 21500

### 结果 1

查询照片最多关键点数目: 2000

```
查询图片 查询时间 匹配时间 匹配数目   角度/期望/误差         位置/期望/误差
2        469.9    440.6    431/757      -0 / 0 / 0         [ -1.33  -2.29 -64.75] / [   0    0 -100] / [ -1.33  -2.29  35.25]
3        459.2    444.9    446/779     -27 / -30 / -3      [ 71.61   0.15 -66.  ] / [115   0   0] / [-43.39   0.15 -66.  ]
4        450.4    468.7    372/669     -45 / -45 / 0       [ 137.78   -5.28  -74.31] / [200   0   0] / [-62.22  -5.28 -74.31]
5        468.5    457.1    426/686      27 / 30 / 2        [-72.25  -0.46 -64.88] / [-115    0    0] / [ 42.75  -0.46 -64.88]
6        446.7    450.2    422/711      42 / 45 / 3        [-131.05   -1.62  -61.42] / [-200    0    0] / [ 68.95  -1.62 -61.42]
```

### 结果 2

查询照片最多关键点数目: 5000

```
查询图片 查询时间 匹配时间 匹配数目   角度/期望/误差         位置/期望/误差
2        492.7    802.6    325/657      -0 / 0 / 0         [ -1.42   0.34 -64.92] / [   0    0 -100] / [ -1.42   0.34  35.08]
3        479.1    769.7    370/663     -27 / -30 / -3      [ 71.72  -0.09 -65.64] / [115   0   0] / [-43.28  -0.09 -65.64]
4        469.5    846.9    368/589     -45 / -45 / 0       [ 137.73   -5.2   -75.56] / [200   0   0] / [-62.27  -5.2  -75.56]
5        494.9    821.4    336/578      27 / 30 / 3        [-71.67  -0.38 -64.34] / [-115    0    0] / [ 43.33  -0.38 -64.34]
6        471.7    925.6    339/584      42 / 45 / 2        [-131.52   -1.51  -61.59] / [-200    0    0] / [ 68.48  -1.51 -61.59]
```

### 结果 3

查询照片最多关键点数目: 8000

```
查询图片 查询时间 匹配时间 匹配数目   角度/期望/误差         位置/期望/误差
2        520.9    1015.4   316/583      -1 / 0 / 0         [ -0.63  -1.04 -65.01] / [   0    0 -100] / [ -0.63  -1.04  34.99]
3        515.1    1035.0   379/620     -27 / -30 / -3      [ 71.62   0.08 -65.96] / [115   0   0] / [-43.38   0.08 -65.96]
4        493.1    965.9    303/519     -45 / -45 / 0       [ 137.73   -5.26  -74.5 ] / [200   0   0] / [-62.27  -5.26 -74.5 ]
5        519.3    1054.3   308/514      27 / 30 / 2        [-72.39  -0.6  -64.82] / [-115    0    0] / [ 42.61  -0.6  -64.82]
6        498.5    941.5    374/560      42 / 45 / 3        [-131.09   -1.42  -61.27] / [-200    0    0] / [ 68.91  -1.42 -61.27]
```

### 图片匹配结果

* [L2000-A500-2](results/accuracy/orb-2000-asift-500-2.jpg)
* [L2000-A500-3](results/accuracy/orb-2000-asift-500-3.jpg)
* [L2000-A500-4](results/accuracy/orb-2000-asift-500-4.jpg)
* [L2000-A500-5](results/accuracy/orb-2000-asift-500-5.jpg)
* [L2000-A500-6](results/accuracy/orb-2000-asift-500-6.jpg)
* [L5000-A500-2](results/accuracy/orb-5000-asift-500-2.jpg)
* [L5000-A500-3](results/accuracy/orb-5000-asift-500-3.jpg)
* [L5000-A500-4](results/accuracy/orb-5000-asift-500-4.jpg)
* [L5000-A500-5](results/accuracy/orb-5000-asift-500-5.jpg)
* [L5000-A500-6](results/accuracy/orb-5000-asift-500-6.jpg)
* [L8000-A500-2](results/accuracy/orb-8000-asift-500-2.jpg)
* [L8000-A500-3](results/accuracy/orb-8000-asift-500-3.jpg)
* [L8000-A500-4](results/accuracy/orb-8000-asift-500-4.jpg)
* [L8000-A500-5](results/accuracy/orb-8000-asift-500-5.jpg)
* [L8000-A500-6](results/accuracy/orb-8000-asift-500-6.jpg)
