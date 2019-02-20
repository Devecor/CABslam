# istar 相机定位实验指导书 #

本实验指导书详细说明了进行一次相机定位实验的过程和步骤，以及使用的方法。

实验过程中产生的文档和数据都存放在 github 库中，本指导书下面的内容中，
默认的当前目录没有特别说明的，都是指 github 库在本地的克隆地址，例如
**d:/workspace/istar**

每一次实验根据老师设定的实验目的开始启动。

## 实验准备 ##

创建目录，例如本次实验为第 11 次实验，那么

```
    # 所有实验都在 src/verify 目录下面
    mkdir src/verify/test11
    cd src/verify/test11

    # 创建保存图片的目录
    mkdir images
```

绘制数据采集点示意图 **test-spots.jpg**, 拷贝模板

```
    cp ../test8/house.jpg test-spots.jpg
```

根据实验目的，使用绘图工具在上面添加数据采集点和测试点，参考实验9
的 [test-spots.jpg](../src/verify/test9/test-spots.jpg)

* 可选工具 [Greenfish Icon Editor](http://greenfishsoftware.org)

编写实验报告书 **TEST11.md**，格式为 Markdown，可以参考实验
9 [TEST9.md](../src/verify/test9/TEST9.md)，把前两个章节 **实验目的**
和 **数据采集** 完成。

* [Markdown 参考手册](https://help.github.com/articles/basic-writing-and-formatting-syntax/)

确认实验报告书，实验报告书完成之后，一般要和老师确认一下，然后在开始下面的实验。

## 照片采集 ##

按照实验报告书的内容进行照片采集。

## 数据处理 ##

把所有的照片从手机复制到 **images** 下面

### 重命名照片 ###

所有的参考点照片存放在 **images/star** 目录下面，命名规范： sN-X.jpg, sN-Xa.jpg

所有的测试点照片存放在 **images/tp** 目录下面，命名规范： tN-X.jpg

编写重命名脚本 **rename.sh**，参考脚本 [rename.sh](../src/verify/test9/rename.sh)

执行重命名脚本

```
    cd src/verify/test11
    cd images
    bash ../rename.sh
```

### 获取照片 orb 关键点 ###

执行下面的命令


```
    # 所有参考照片获取 8000 个 orb 关键点，保存在 features/orb-8000 目录下面
    bash ../test5/query-feature.sh images/star features 8000

    # 所有查询照片获取 2000 个参考点，保存在 features/test-orb-2000 下面
    bash ../test5/query-feature.sh images/tp "features/test-" 2000

```

[query-feature.sh](../src/verify/test5/query-feature.sh) 脚本支持的参数

* 第一个参数是图片存放的路径
* 第二个参数是关键点结果的保存路径，提取的关键点是以 .npz 格式保存
* 第三个参数是关键点的提取个数
* 第四个参数是使用的特征名称，默认为 orb，或者为 asift

单独查看某一张图片的关键点使用命令

```
    C:/Python27/python ../check_feature.py --show --nFeatures=2000 images/star/s1-1.jpg
```

支持的参数列表

```
    C:/Python27/python ../check_feature.py -h
    usage: check_feature.py [-h] [--show] [--save] [--output OUTPUT] [--grid]
                            [--mask MASK] [--asift] [--tilt TILT]
                            [--feature {orb,sift,surf}] [--nFeatures n]
                            [--pose POSE] [--camera CAMERA]
                            FILENAME [FILENAME ...]
```

主要参数说明：

* --show 显示图片
* --save 保存结果
* --output 关键点的保存路径，仅仅当指定 --save 才有效
* --asift 使用 asift 取样
* --feature 使用的特征名称
* --nFeatures 最大的特征数目

### 匹配参考照片 ###

生成输入文件 **star-input.txt**，参考实验8 [star-input.txt](../src/verify/test8/star-input.txt)

执行下面的命令

```
    # 匹配两张参考照片，使用 findFundamentalMat 进行过滤
    #     匹配图片存放到 matches/f-orb-8000.orb-8000 目录下面
    #     匹配汇总结果存放在 results/match-f-result-orb-8000.orb-8000.star-input.txt
    bash ../test5/match-feature.sh star-input.txt "matches/f-" features/orb-8000 features/orb-8000 f

    # 匹配两张参考照片，使用 findHomography 进行过滤，
    #     匹配图片存放到 matches/orb-8000.orb-8000 目录下面
    #     匹配汇总结果存放在 results/match-h-result-orb-8000.orb-8000.star-input.txt
    bash ../test5/match-feature.sh star-input.txt "matches" features/orb-8000 features/orb-8000

    # 匹配两张参考照片，不进行过滤，
    #     匹配图片存放到 matches/n-orb-8000.orb-8000 目录下面
    #     匹配汇总结果存放在 results/match-n-result-orb-8000.orb-8000.star-input.txt
    bash ../test5/match-feature.sh star-input.txt "matches/f-" features/orb-8000 features/orb-8000 n

```

统计匹配结果的命令

```
    gawk -f ../test3/sum-match.awk results/match-f-result-orb-8000.orb-8000.star-input.txt
    gawk -f ../test3/sum-match.awk results/match-h-result-orb-8000.orb-8000.star-input.txt
    gawk -f ../test3/sum-match.awk results/match-n-result-orb-8000.orb-8000.star-input.txt
```

[match-feature.sh](../src/verify/test5/match-feature.sh) 脚本使用方法

```
    bash match-feature.sh INPUT OUTPUT QPATH TPATH [f|h|n]

```

* 第一个参数 输入文件，每一行包含需要匹配的两个文件
* 第二个参数 是输出路径的前缀，如果以 "-" 结束则表示同一输出路径下面的不同输出
* 第三个参数 存放查询照片 关键点的路径
* 第四个参数 存放参考照片 关键点的路径
* 第五个参数是匹配模式：
    * f 使用 findFundamentalMat 进行匹配
    * h 使用 findHomography 进行匹配，这也是默认值
    * n 表示简单匹配



单独匹配两张照片的命令

```
    C:/Python27/python ../check_match.py --kpfile1=features/orb-8000/s1-1.npz --kpfile1=features/orb-8000/s1-1a.npz \
         --show images/star/s1-1.jpg images/star/s1-1a.jpg
```

使用方法

```
usage: check_match.py [-h] [--kpfile1 KPFILE1] [--kpfile2 KPFILE2]
                      [--homography] [--fundamental] [--show] [--save]
                      [--output OUTPUT]
                      FILENAME FILENAME

匹配两个图片的关键点

positional arguments:
  FILENAME           训练图片，查询图片

optional arguments:
  -h, --help         show this help message and exit
  --kpfile1 KPFILE1  训练图片关键点文件
  --kpfile2 KPFILE2  查询图片关键点文件
  --homography       是否使用 homography 过滤匹配结果
  --fundamental      是否使用 fundamental 过滤匹配结果
  --show             在窗口中显示匹配结果
  --save             是否保存匹配结果
  --output OUTPUT    输出文件的路径

```

### 匹配测试照片 ###

创建测试点和参考点对应关系文件 **test-ref-star.txt**，参考实验8 [test-ref-star.txt](../src/verify/test8/test-ref-star.txt)

生成输入文件 **test-star-input.txt**

```
    gawk -f ../test8/make-test-star.awk test-ref-star.txt > test-star-input.txt
```

awk 语言简介，参考脚本 [make-test-star.awk](../src/verify/test8/make-test-star.awk)


执行下面的命令，匹配测试照片

```
    # 使用 findHomography 进行过滤，匹配结果存放在 results/match-h-result-orb-8000.test-orb-2000.test-star-input.txt
    bash ../test5/match-feature.sh test-star-input.txt "matches" features/test-orb-2000 features/orb-8000

    # 使用 findFundamentalMat 进行过滤，匹配结果存放在 results/match-f-result-orb-8000.test-orb-2000.test-star-input.txt
    bash ../test5/match-feature.sh test-star-input.txt "matches/f-" features/test-orb-2000 features/orb-8000 f

```

汇总匹配结果，把显示出来的结果要拷贝到实验报告书实验结果（**测试点和采集点照片的匹配成功率**）下面

```
    gawk -f ../test3/sum-match.awk results/match-h-result-orb-8000.test-orb-2000.test-star-input.txt
```


### 生成关键点三维坐标库 ###

了解相机定位基础，相机内参，照片焦距，底片大小

[针孔相机模型](https://docs.opencv.org/3.2.0/d9/d0c/group__calib3d.html)

如何查看照片焦距，通过 jpg 文件 EXIF 信息，直接在手机上查看照片的详细信息，使用等效焦距的值

常见手机的底片大小，CCD-CMOS

```
型号    宽 高(mm)
1/3    4.8 3.6
1/2.5  5.8 4.3
1/1.8  7.2 5.3
2/3    8.8 6.6
```

如何简单的测量手机底片的大小，

  * 打开手机相机
  * 距离某一个已知宽度为 w 的物体
  * 前后移动手机，使宽度为 w 的物体正好等于照片的宽度，记录相机和物体的距离 d
  * 拍下照片，查看照片详细信息，得到等效焦距的值 f (mm)
  * 相机底片较短的边长 = f * w / d (mm)

创建输入文件 **model-input.txt**, 参考实验 9 [model-input.txt](../src/verify/test9/model-input.txt)

修改 **build-model.sh** 中的 size 和 focals 参数，size 是相机的宽度和高度，focals = 焦距 / 底片大小

```
    BUILDCMD="C:/Python27/python ../make_model.py --size=2448,3264 --focals=0.9722,0.7292"
```

执行下面的命令, 保存生成的三维模型库到目录 **models**

```
    bash ../test5/build-model.sh model-input.txt "models" features/orb-8000 f
```



```
    cat results/model-f-model-input.txt
```

[build-model.sh](../src/verify/test5/build-model.sh) 脚本使用方法可参考文件头部的注释


单张照片的建模命令，查看三维坐标信息，使用 --show

```
    C:/Python27/python ../make_model.py --size=2448,3264 --focals=0.9722,0.7292 \
    --show --homography --refpos=-10,0,0 \
    features/orb-8000/s1-1-orb.npz features/orb-8000/s1-1a-orb.npz
```

使用说明
```
    C:/Python27/python ../make_model.py --help
    
    usage: make_model.py [-h] [--refpos REFPOS] --size SIZE [--show]
                         [--save] [--output path] [--homography]
                         [--fundamental] [--focals fx,fy] [--maximum D]
                         IMAGE REFIMAGE
    
    生成图片的三维特征点文件
    
    positional arguments:
      IMAGE            图片对应的特征文件
      REFIMAGE         参考图片对应的特征文件
    
    optional arguments:
      -h, --help       show this help message and exit
      --refpos REFPOS  参考图片拍摄位置相对偏移量 dx,dy,dz
      --size SIZE      图片大小 w,h
      --show           打印获取到的关键点三维信息
      --save           保存三维关键点数据
      --output path    输出文件的路径
      --homography     使用 Homography 进行过滤
      --fundamental    使用 fundamental 过滤匹配结果
      --focals fx,fy   相机内参（fx,fy)
      --maximum D      最远的三维关键点距离，单位是厘米，默认值是 3000
    
```

### 查询定位 ###

执行下面的命令对所有的测试照片进行定位，输入文件为 **test-star-input.txt**

```
    # 根据 test-star-input.txt 的输入进行测试照片的定位
    # 输出的结果存放的路径是 locations 
    # 测试照片关键点的保存路径是 features/test-orb-2000
    # 参考照片三维关键点的数据存放在 models 下面
    bash ../test5/query-location.sh test-star-input.txt locations features/test-orb-2000 models
```

该命令执行完之后，会提示生成的汇总定位结果文件，一般是 **results/location-h-models.test-orb-2000.test-star-input.txt**

[query-location.sh](../src/verify/test5/query-location.sh) 脚本使用方法可参考文件头部的注释


有时候发现某一张照片定位有问题，可以对单张照片进行定位

```
    c:/Python27/python ../query_location.py --size=2448,3264 --focals=0.9722,0.7292 --homography \
    features/test-orb-2000/t1-2-orb models/s1-1 models/s1-2 models/s1-5
```

使用方法

```
    C:/Python27/python ../query_location.py --help
    
    usage: query_location.py [-h] [--homography] [--fundamental] [--save]
                             [--reject REJECT] [--accept ACCEPT] [--output OUTPUT]
                             [--focals FOCALS] [--size SIZE]
                             QUERY IMAGES [IMAGES ...]
    
    根据参考图片，定位查询图片的位置和朝向
    
    positional arguments:
      QUERY            查询图片
      IMAGES           参考图片模型文件
    
    optional arguments:
      -h, --help       show this help message and exit
      --homography     是否使用 homography 过滤匹配结果
      --fundamental    是否使用 fundamental 过滤匹配结果
      --save           是否保存定位结果
      --reject REJECT  匹配失败阀值，小于该值认为是失败，默认是 6
      --accept ACCEPT  匹配成功阀值，大于该值认为匹配成功，默认是 100
      --output OUTPUT  输出文件的路径
      --focals FOCALS  相机内参（fx,fy)
      --size SIZE      查询照片大小（w,h)
    
```

### 汇总定位结果 ###

执行下面的命令，显示定位成功率

```
    gawk -f sum-location.awk results/location-h-models.test-orb-2000.test-star-input.txt
```

参考实验9 [TEST9.md](../src/verify/test9/TEST9.md)的测试报告，把输出的结果写入到 TEST11.md 的（**测试点的定位结果和误差**）下面


#### 转换坐标系 ####

把定位结果从相机坐标系转换成为大厅坐标系

相机坐标系参看针孔相机模型

大厅坐标系是向北为 X 轴正向，向西为 Y 轴正向

编写转换脚本 **transform-location.awk**，可以参考实验9 [transform-location.awk](../src/verify/test9/transform-location.awk)

执行下面的命令，转换定位结果，把输出结果存放到文件 **results/location-results.txt**

```
    gawk -f transform-location.awk results/location-h-models.test-orb-2000.test-star-input.txt > results/location-results.txt
```

#### 计算误差 ####

编写转换脚本 **location-errors.awk**，可以参考实验9 [location-errors.awk](../src/verify/test9/location-errors.awk)

这个文件需要根据测试点和参考点的相对位置关系，设置每一个测试点的期望位置

然后执行下面的命令，把定位误差存放到 **results/location-errors.txt**

```
    gawk -f location-errors.awk results/location-results.txt > results/location-errors.txt
```

参考实验9 [TEST9.md](../src/verify/test9/TEST9.md)的测试报告，把误差和定位结果写入到 TEST11.md 的（**测试点的定位结果和误差**）下面


## 提交实验结果 ##

创建一个 **build.sh**, 保存上面所有使用的命令，参考实验 9 [build.sh](../src/verify/test9/build.sh)

test11 下面的所有文件上传到 istar 库
test11\results 下面的所有文件上传到 istar 库

示例，如何提交一个文件到 istar 库
```
  git add TEST11.md
  git commit -m'Add test report' TEST1.md
  git push
```

test11\images 下面的所有文件，压缩成为 test-images.zip，然后上传到 istar 库的 Release 里面


# 附录 #

了解 Git 的基本使用方法

[Git入门命令](http://zhaojunde1976.blog.163.com/blog/static/121998668201182364243972/)

一个简单的多功能编辑器

[Notepad++](https://notepad-plus-plus.org/download)

如何创建 git 一个分支并在 github 创建一个 pull request

```
  # 查看当前分支
  git branch
  
  # 创建一个新分支，基于当前内容
  git checkout -B test1
  
  # 执行完命令之后，当前分支就切换到 test1
  # 修改文件
  # 提交修改的内容
  git commit -m'XXXX' -a
  
  # 把当前分支推送到服务器
  git push origin test1
  
  # 切换到原来的主分支
  git checkout master
  
  # 下面的操作在网页上进行
  1. 在 istar 库上点击按钮 New pull request
  2. 在新页面 compare 后面选中分支 test1
  3. 点击按钮 Create pull request
  
  等待 pull request 被接受，接受之后分支 test1 所做的修改就会合并到 master 分支
  
```
## 实验文档规范

test15 是正式的实验，里面的数据以后论文里面要用到，所以必须规范，每一次实验的文档的基本要求:

1. testxx.md 和 test-spots.jpg 这个文档应该在拍照之前完成并提交到服务器. 

2. 照片拍完之后的原始照片（没有改名之前的）拷贝到 testxx/images 下面，并打包成为一个 zip 文件   
   
    然后编写 renamse.sh ，重命名所有照片，在此之前先打个包 .zip 保存原始照片。
   
    test15 如果没有原始照片，也不必要重新从手机导入，把命名后的照片打包一个就可以了。
   
3. 所有的脚本（.awk 和 .sh）都存放在 testxx/ 根目录下面，所有执行的命令都存放在 build.sh 里面

    脚本要达到的要求，让其他人可以通过 build.sh ，重现实验数据处理过程，得到实验结果。
   
    不要放置实验无关的的脚本和辅助文件，例如 test15 里面不会用到建模和定位相关的所有脚本，这些就不要放上去
   
    脚本的名称和辅助文件的命名，例如 test-star-input.txt 等 可以根据需要修改，或者添加新的脚本，不是完全拷贝过去实验的脚本，要根据当前实验的要求，只要能通过 build.sh 记录的命令重现就可以。

    例如 test13 实验，我在我的电脑上更新下来之后，执行 rename.sh, 执行 build.sh 里面的 query-features, build-models, query-locations, 和 gawk 汇总命令，就得到实验的结果
   
    其他实验也是一样的，最终提交的文档都应该可以让他人把实验结果重现的，按照这个要求来检查脚本是否符合规范。
   
4. 实验的汇总结果都存放在 testxx/results 下面

    例如 test15，图片和匹配的图片可以存放在 test-1m 下面，但最后汇总的结果都放在实验根目录的 testxx/results 下面
   
    可以在 results/ 使用不同的文件名称来区别不同的距离，这需要把相关的脚本修改一下。
   
    这些实验汇总结果以后可能会用到，例如，我可能根据匹配结果文件，编写 gawk 脚本，来统计不同角度照片的匹配成功率
   

5. 开始设计实验 test16 ，实地勘察一下老教学楼的二楼，先不要拍照，把 test16.md 和 test-spot.jpg 画出来，上传到服务器上，我确认过之后明天开始拍照，按照规范开始实验。

    test16 你们要根据实验目的自己设计，可以参考前面的实验，但不是完全复制前面的实验，因为二楼是一个三条边的矩形，脚本可能需要修改。

    为了达到主要的实验目的，即平均定位误差小于50cm（结果略大也可以接受），你们要自己调整和选择关键点参数，匹配方法以及使用的定位算法，并且把这些参数都记录到实验报告里面。如果分析确认照片有问题，还需要补拍照片。


## 如何上传照片压缩包到 github 的 release 下面

* 创建一个 GITHUB TOKEN

    https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/   
   
* 下载工具 github-release

    https://github.com/aktau/github-release/releases/tag/v0.7.2

* 执行命令

```
    export GITHUB_TOKEN=XXXXXXX  # 这是第一步创建的TOKEN  
    github-release upload \
     --user jondy \
     --repo istar \
     --tag t01-16 \
     --name "images.zip" \
     --file images.zip

```
   
