# istar 室内手机定位导航系统实验一

istar 系统被设计用来在手机上进行室内定位导航，期望能够达到如下目标：

* 室内定位精度小于 60cm
* 每次定位的时间基本在 5s 之内

第一次实验主要目的是验证核心功能是否达到要求，基本的方法和步骤如下：

* 编写核心算法和主程序，使用 Python，Numpy 和 OpenCV 实现

* 以物信楼的一层为例，初始化下列数据

  - 划分区域
  - 初始化区域内的Wifi指纹数据
  - 初始化区域内的参考照片数据

* 任意选取楼层内十个测试点，在各个测试点拍照，记录Wifi数据和拍摄位置

* 启动主程序，传入测试点的照片和Wifi数据，比较主程序计算得到的测试点拍
  摄位置和实际拍摄位置的误差。

## 核心算法实现说明

### Wifi 指纹定位区域

根据手机的Wifi信号，使用Knn算法得到几个备选区域。

```
   传入参数是Wifi信号列表： (BSSID1, RSSI), （BSSID2, RSSI), ...
   其中BSSID是Wifi标识，RSSI 是信号强度

   传出参数是区域索引列表： REGION1, REGION2, REGION3

```

### 参考照片定位

根据Wifi指纹得到的备选区域，依次取出区域内部的参考照片，和当前照片进行
匹配定位。

照片的关键点算法使用 ORB： An efficient alternative to SIFT or SURF in
2011. As the title says, it is a good alternative to SIFT and SURF in
computation cost, matching performance and mainly the patents. Yes,
SIFT and SURF are patented and you are supposed to pay them for its
use. But ORB is not !!!

**参考** Ethan Rublee, Vincent Rabaud, Kurt Konolige, Gary R. Bradski: ORB: An efficient alternative to SIFT or SURF. ICCV 2011: 2564-2571.

关键点的匹配算法使用 Flann，FLANN stands for Fast Library for
Approximate Nearest Neighbors. It contains a collection of algorithms
optimized for fast nearest neighbor search in large datasets and for
high dimensional features. It works more faster than BFMatcher for
large datasets. We will see the second example with FLANN based
matcher.

参考照片在数据库中直接保存的是关键点以及对应的空间坐标，还包括参考照片
的相机参数、拍摄位置和角度等信息。为了保证能够匹配不同角度的照片，我们
使用 asift 算法为参考照片生成关键点。Uses the affine transformation
space sampling technique, called ASIFT [1]. While the original
implementation is based on SIFT, you can try to use SURF or ORB
detectors instead. Homography RANSAC is used to reject
outliers. Threading is used for faster affine sampling.

[1] http://www.ipol.im/pub/algo/my_affine_sift/

asift 算法会计算照片旋转一定角度之后的关键点，然后把不同角度照片上的关
键点汇总起来。这样，我们相当于有了和当前照片不同角度的多张照片的关键点，
可以大大增加关键点的匹配率。但是 asift 算法比较耗费时间，所以参考照片可
以使用 asift 算法，把生成的关键点保存在文件中。而在和当前照片匹配的时候，
直接从文件中读取参考照片的关键点，当前照片关键点查找并不使用 ASIFT 算法，
而是直接使用 ORB 算法，这样即提高了照片的匹配度，又基本和 ORB 算法耗时
相当。

如果当前照片和参考照片匹配的关键点数目达到一定值，现在是 60 个，那么就
可以使用该参考照片进行定位。

相机定位使用 opencv 中 solvePnP 来实现，SOLVEPNP_ITERATIVE Iterative
method is based on Levenberg-Marquardt optimization. In this case the
function finds such a pose that minimizes reprojection error, that is
the sum of squared distances between the observed projections
imagePoints and the projected (using projectPoints ) objectPoints .

传入参数：

```
    手机相机的内部参数，主要是焦距 fx, fy
    当前照片匹配的关键点
    当前照片匹配的关键点对应的空间坐标

    因为在数据库中保存着参考照片中所有关键点对应的空间坐标，根据两张照
    片的关键点匹配关系可以得到当前照片
```

返回结果

```
  当前相机和参考相机的相对位移
  当前相机和参考相机的相对水平偏转角度
```

因为参考相机的位置和方位角都是已知的，我们据此可以得到当前相机的位置和
方位角。

## 实验详细步骤

实验需要一台电脑，用于运行 istar 实验程序。

### istar 运行环境建立

运行 istar 需要在电脑上安装，

* Python2.7
* Numpy
* OpenCV

然后下载istar程序和代码，在电脑上执行下列命令

```
  $ mkdir ~/workspace
  $ cd workspace
  $ git clone https://github.com/jondy/istar.git
```

### 数据采集

区域划分原则，

* 区域长宽不小于 5 米
* 区域一般以墙为自然界限，对于特别长的区域，例如走廊，可以分段建立区域

按照上述原则，将物信楼划分好区域，并依此编号，从 0 开始。

在 istar 系统中，需要知道参考照片中关键点对应的空间坐标，所以有两种方式

* 参考平面法

  参考平面法只需要拍一张照片，普通手机相机即可。要求选取一个垂直的参考
  平面，相机拍摄的时候正对该参考平面，还需要记录相机到参考平面的距离。

* 双目相机法

  双目相机法是使用深度相机进行拍摄，这样可以直接获取到照片的深度信息，
  从而直接得到对应的空间坐标。这也是和 iMoon 相比，能够提高定位精度的一
  种方式之一。

参考照片采集方法，

* 对于长宽小于 5 米的区域，一般在中心位置朝四个方向各拍一张或者多张
* 对于长宽比较大的区域，可以每5米进行一组拍摄
* 一般要尽量选取有丰富色彩的空间对象
* 参考照片拍摄时候相机不要有仰角和旋转
* 记录拍摄位置，包括和参考点的方向和距离，以及拍摄高度
* 记录拍摄方位角，以正北方向为 0 度，向东为正，向西为负，范围正负180度
* 如果是参考平面法，那么还需要记录相机到参考平面的距离

Wifi数据采集方法和步骤

* 在区域内选取 1 ~ 5 个代表性的测试点，记录各个Wifi数据信息

测试点数据采集，测试点数据主要是为了验证 istar 的定位结果

* 选取十个测试点
* 随机拍下照片，记录拍摄位置，相机水平方位角
* 记录该测试点对应的wifi数据信息

### 初始化数据

打开电脑，把采集到数据文件拷贝到相关目录

```
    区域信息和Wifi列表数据，存放在 istar/data/wuxin/index.json
   
```

Wifi指纹数据

```
     Wifi数据存放在 istar/data/wuxin/wifi-finger.npy

     Wifi原始数据处理成为每一个 wifi 对应一个文本文件，文件名称为 rssid.txt
     每一行包括一个位置的 rssi 数据
     
         rssi x y z
     
     例如 TP-LINK_A970D6.txt

         -50 0.25 0.36 0
         -86 0.33 0.29 0
         ...

     然后执行下列命令

     $ cd ~/workspace/istar
     $ cd src
     $ python main.py add wifi TP-LINK_A970D6.txt

     将数据导入到 wifi-finger.npy 中
```

参考照片数据

```
    参考照片数据按照区域不同存放在 istar/data/wuxin/rN

    其中 N 是区域的索引编号

    原始参考照片要经过处理之后存放到对应的区域路径下
```

测试点数据

```
    存放路径 istar/data/test/
    照片     istar/data/test/img_1.jpg, img_2.jpg ...
    wifi数据 istar/data/test/wifi_1.json, wifi_2.json ...

    其中 wifi_1.json 的数据内容为

        [ [ "TP-LINK_C866", -80 ], ["TP-LINK_5G_A7AC", -60 ] ]
```

### 测试点定位

在电脑上运行下面的命令，计算测试点的位置

```
   $ cd ~/workspace/istar
   $ cd src
   $ python main.py query --focal=3528,3528 --wifi=../data/test/wifi_1.json --image=img_1.jpg
     ...
   $ python main.py query --focal=3528,3528 --wifi=../data/test/wifi_9.json --image=img_9.jpg
```

记录各个命令输出的定位结果。

### 结果验证

比较上一步各个测试点的定位结果，和记录的实际结果，就可以得到误差报告。

## 参考数据

### 区域划分

大厅有两种划分方式

- 以中间的显示屏为界，一分为二，共两个区域
- 在上一步的基础上，每个区域在等分为三个小区域，共六个区域

其他区域按照墙壁形成的封闭区域，共分为六个区域。

### 区域Wifi指纹采集点

测量各个区域的中心，和四个边界中心的Wifi信号强度。

### 参考照片拍摄点

大厅取六个点，分别在上面定义的大厅六个区域的中心位置，朝四个方向各照一张照片。

其他区域基本也是在中心照四张照片。是否存在没有关键点的照片呢？

### 测试点选取

大厅

- 和显示屏平行的墙从入口处各取两个，拍照方向为显示屏
- 和显示屏垂直的墙从入口处各取三个，拍照方向为显示屏
- 以大厅的中间矩形为参考，取顶点和各边中点，共八个参考点，顶点以对角线
  方向两个方向的各照一张，中点则以垂线方向各照一张
- 以大厅四个柱子形成的矩形，在各边中点两个方向各照一张

其他区域则每个房间随机选取一个测试点，分别照三个角度的照片。