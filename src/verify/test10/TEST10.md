# iStar 手机端性能实验 10 #

## 实验目的 ##

* 验证使用手机端使用 OpenCV 进行特征搜索，和参考照片匹配以及定位的性能

## 实验方法 ##

使用 C++ 编写一个简单应用程序，执行下列功能:

* 读取查询照片 t1-3.jpg (3264x2448, 2M大小)
* 提前2000个ORB关键点
* 循环五张参考照片，对于每一张参考照片，进行下面的操作
    * 读取参考照片对应的数据文件（建模好的数据）
    * 参考照片和查询照片进行关键点匹配，并使用 findHomography 进行过滤
    * 如果匹配数目超过阀值，则使用 solvePnPRansac 进行定位
* 输出各个步骤消耗的时间到日志文件

第一组结果在笔记本上运行，生成相应的日志文件作为对比。

第二组结果在手机上运行，输出生成的日志文件。

在手机上目前是在开发环境下运行，基本步骤：

* 使用 OpenCVForAndoridSDK 和 Android NDK 在 Ubuntu上编译 Android 版本的可执行文件
* 连接手机到 Ubuntu
* 在Ubuntu上使用 Android SDK 命令行工具 adb ，把可执行文件上传到手机并执行
* 下载执行得到的结果日志

## 实验结果 ##

* 使用 Homography 过滤匹配结果的定位时间
    * 笔记本上总运行时间： **1560.514ms**
    * 手机上总运行时间： **3697.010ms**

* 不使用 Homography 过滤匹配结果的定位时间
    * 笔记本上总运行时间： **1259.013**
    * 手机上总运行时间： **2894.421**


我的手机是普通的华为手机畅享7（800多元），在配置高的机型上面性能应该有
所提升，需要后续做一些实验进行验证。

检查各个步骤消耗的时间发现，提取关键点特征这一个步骤所占比重较大，在本
实验中手机端为 **1479.406ms/1438.045ms**，占到了总时间的 40%。


## 附录 ##

### 手机配置 ###

```
Hardware Information:
------------------------------------
Mobile HUAWEI SLA-AL00
Memory 2G
Android 7.0
CPU Qualcomm Snapdragon 425
------------------------------------

```

### 笔记本配置 ###

```
Hardware Information:
------------------------------------
Laptop Dell Inspire 1440
Memory 4G
Windows XP (32)
CPU:  Pentium(R) Dual-Core CPU       T4400  @ 2.20GHz
------------------------------------

```

### 运行日志一 ###

手机端使用 homography 过滤的定位方式

```

Query image: Data/t1-3.jpg
Read model from: Data/
Model list: s1-1.yml,s1-2.yml,s1-3.yml,s1-4.yml,s1-5.yml,
========================================

Read image: Data/t1-3.jpg (270.415ms)
Detect 2000 keypoints from Data/t1-3.jpg (1479.406ms)

------------------------------
Load model from Data/s1-1.yml (136.413ms)
Good matches keypoints is 32 (83.492ms)
Filtered by homography is 8 (199.582ms)
Matched keypoints 8 less than thresold 10
Elapse time (this loop): 419.509ms

------------------------------
Load model from Data/s1-2.yml (112.877ms)
Good matches keypoints is 679 (75.186ms)
Filtered by homography is 402 (13.616ms)
Locate result: 14.39 -15.44 -82.39 (12.742ms)
Elapse time (this loop): 214.450ms


------------------------------
Load model from Data/s1-3.yml (50.418ms)
Good matches keypoints is 62 (43.250ms)
Filtered by homography is 15 (226.662ms)
Locate result: -106.28 390.62 1474.13 (37.186ms)
Elapse time (this loop): 357.541ms


------------------------------
Load model from Data/s1-4.yml (176.883ms)
Good matches keypoints is 19 (102.634ms)
Filtered by homography is 4 (295.183ms)
Matched keypoints 4 less than thresold 10
Elapse time (this loop): 574.724ms

------------------------------
Load model from Data/s1-5.yml (167.093ms)
Good matches keypoints is 24 (96.526ms)
Filtered by homography is 7 (110.647ms)
Matched keypoints 7 less than thresold 10
Elapse time (this loop): 374.289ms

========================================
Elapse time (total) 3697.010ms

```

笔记本端使用 homography 过滤的定位方式

```
Query image: Data/t1-3.jpg
Read model from: Data/
Model list: s1-1.yml,s1-2.yml,s1-3.yml,s1-4.yml,s1-5.yml,
========================================

Read image: Data/t1-3.jpg (157.585ms)
Detect 2000 keypoints from Data/t1-3.jpg (525.102ms)

------------------------------
Load model from Data/s1-1.yml (55.981ms)
Good matches keypoints is 37 (48.152ms)
Filtered by homography is 9 (94.242ms)
Matched keypoints 9 less than thresold 10
Elapse time (this loop): 198.387ms

------------------------------
Load model from Data/s1-2.yml (46.229ms)
Good matches keypoints is 661 (45.205ms)
Filtered by homography is 419 (4.428ms)
Locate result: 3.19 -22.31 -77.50 (5.516ms)
Elapse time (this loop): 101.390ms


------------------------------
Load model from Data/s1-3.yml (20.741ms)
Good matches keypoints is 63 (27.004ms)
Filtered by homography is 15 (99.845ms)
Locate result: -270.43 453.01 2855.34 (14.050ms)
Elapse time (this loop): 161.652ms


------------------------------
Load model from Data/s1-4.yml (72.084ms)
Good matches keypoints is 15 (62.956ms)
Filtered by homography is 5 (26.706ms)
Matched keypoints 5 less than thresold 10
Elapse time (this loop): 161.755ms

------------------------------
Load model from Data/s1-5.yml (67.856ms)
Good matches keypoints is 30 (56.009ms)
Filtered by homography is 6 (127.650ms)
Matched keypoints 6 less than thresold 10
Elapse time (this loop): 251.526ms

========================================
Elapse time (total) 1560.514ms


```

### 运行日志二 ###

手机端没有使用 homography 过滤的定位方式

```
Query image: Data/t1-3.jpg
Read model from: Data/
Model list: s1-1.yml,s1-2.yml,s1-3.yml,s1-4.yml,s1-5.yml,
========================================

Read image: Data/t1-3.jpg (267.711ms)
Detect 2000 keypoints from Data/t1-3.jpg (1438.045ms)

------------------------------
Load model from Data/s1-1.yml (135.448ms)
Good matches keypoints is 32 (75.605ms)
Locate result: 239.17 -109.65 325.98 (38.156ms)
Elapse time (this loop): 249.236ms


------------------------------
Load model from Data/s1-2.yml (112.467ms)
Good matches keypoints is 679 (69.035ms)
Locate result: 12.73 -16.09 -82.45 (16.601ms)
Elapse time (this loop): 198.128ms


------------------------------
Load model from Data/s1-3.yml (50.129ms)
Good matches keypoints is 62 (40.999ms)
Locate result: 116.25 -5.57 -207.17 (41.963ms)
Elapse time (this loop): 133.116ms


------------------------------
Load model from Data/s1-4.yml (175.976ms)
Good matches keypoints is 19 (99.398ms)
Locate result: -29.31 89.31 1278.20 (37.040ms)
Elapse time (this loop): 312.439ms


------------------------------
Load model from Data/s1-5.yml (166.174ms)
Good matches keypoints is 24 (85.485ms)
Locate result: 1005.61 498.31 2065.83 (37.363ms)
Elapse time (this loop): 289.048ms


========================================
Elapse time (total) 2894.421ms

```

笔记本端没有使用 homography 过滤的定位方式

```
Query image: Data/t1-3.jpg
Read model from: Data/
Model list: s1-1.yml,s1-2.yml,s1-3.yml,s1-4.yml,s1-5.yml,
========================================

Read image: Data/t1-3.jpg (147.914ms)
Detect 2000 keypoints from Data/t1-3.jpg (524.989ms)

------------------------------
Load model from Data/s1-1.yml (55.738ms)
Good matches keypoints is 37 (50.858ms)
Locate result: -306.84 150.95 132.89 (14.723ms)
Elapse time (this loop): 121.331ms


------------------------------
Load model from Data/s1-2.yml (46.546ms)
Good matches keypoints is 661 (49.543ms)
Locate result: -1.44 -17.71 -83.05 (7.795ms)
Elapse time (this loop): 103.897ms


------------------------------
Load model from Data/s1-3.yml (20.909ms)
Good matches keypoints is 63 (26.798ms)
Locate result: -9.98 818.58 2182.01 (15.235ms)
Elapse time (this loop): 62.954ms


------------------------------
Load model from Data/s1-4.yml (73.542ms)
Good matches keypoints is 15 (66.221ms)
Locate result: 263.72 -380.03 -415.46 (13.859ms)
Elapse time (this loop): 153.635ms


------------------------------
Load model from Data/s1-5.yml (68.555ms)
Good matches keypoints is 30 (58.247ms)
Locate result: -653.31 838.20 1452.15 (14.285ms)
Elapse time (this loop): 141.098ms


========================================
Elapse time (total) 1259.013ms

```

