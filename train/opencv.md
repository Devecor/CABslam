# OpenCV 基本使用方法

## 培训目的

* 能够运行 OpenCV 自带的例子
* 了解计算机视觉的两个基本概念：特征和匹配

## 环境安装

### OpenCV

* Windows 版本下载地址 [https://sourceforge.net/projects/opencvlibrary/files/opencv-win/3.4.0/opencv-3.4.0-vc14_vc15.exe/download](https://sourceforge.net/projects/opencvlibrary/files/opencv-win/3.4.0/opencv-3.4.0-vc14_vc15.exe/download)

* 双击安装包，按照提示进行安装即可。本教程中下面的例子都假设安装路径为 C:/opencv

### Python

用来运行 OpenCV 里面的例子的工具

* Windows 版本下载地址（64位） [https://www.python.org/ftp/python/2.7.14/python-2.7.14.amd64.msi](https://www.python.org/ftp/python/2.7.14/python-2.7.14.amd64.msi)
  其他下载参考 [https://www.python.org/ftp/python/2.7.14](https://www.python.org/ftp/python/2.7.14)

* 双击安装包，按照提示进行安装即可。本教程中下面的例子都假设安装路径为 C:/Python27

### NumPy

是运行 OpenCV 必须的 Python 库，主要功能是高性能的数学计算（矩阵、数组等）。

* 打开命令行窗口
* 输入下面的命令安装

```
  C:/Python27/python -m pip install --user numpy scipy matplotlib ipython

```

### Cygwin（可选）

支持在Windows下运行 Linux Shell 命令的模拟器。

* Windows 版本下载地址 [https://cygwin.com/setup-x86_64.exe](https://cygwin.com/setup-x86_64.exe)
* 下载之后双击运行，按照提示进行安装
    * 选择安装路径，本教程默认为 c:/cygwin
    * 选择本地下载缓存的路径，本教程默认为 c:/cygwin-cache
    * 选择下载源，安装需要从网上下载组件
    * 选择需要安装的组件，使用默认设置即可
* 点击安装，根据网络连接速度不同等待提示安装完成。

## 运行 OpenCV 的例子

* 打开命令行窗口

* 切换到路径 C:/opencv/sources/samples/python

```
  C:
  cd opencv/sources/samples/python
```

* 拷贝 cv2.pyd 到运行路径，这是通过 Python 运行 OpenCV 的桥梁

```
  copy C:/opencv/build/python/2.7/x64/cv2.pyd C:/Python27/lib/site-packages/cv2.pyd
```

* 所有例子的说明和运行方式

```
  C:/Python27/python demo.py
```

选择一个例子 **edge.pyy**，点击 Run 可以运行该示例，计算机眼里的边界

输入参数运行 **flood_fill.py** ，在文件名后面输入相关参数 **../data/apple.jpg**，点击 Run

在后面的控制台上会打印执行的信息

大部分例子中都可以使用 Esc 键关闭窗口

部分例子可能运行不了，请注意控制台上显示的信息

* 在命令行直接运行 **distrans.py**

```
  C:/Python27/python contours.py ../data/apple.jpg

```

* 查看每一个例子的操作说明 **plane_tracker.py**

    如何选中跟踪物体
    如何清除跟踪物体
    如何退出

* 特征匹配 find_obj.py

```
  C:/Python27/python find_obj.py --feature=orb-flann ../data/box_in_scene.png ../data/box.png
```

使用 sift 描述符: --feature=sift-flann
使用 surf 描述符: --feature=surf-flann
使用 akaze 描述符: --feature=akaze-flann

修改其他参数，需要在代码中直接设置，例如 最多 orb 特征数目从 400 调整到 800

```
    detector = cv2.ORB_create(400) -> detector = cv2.ORB_create(800)
```

* asift.py

和 find_obj 类似，只是增加了取样算法

```
  C:/Python27/python asift.py --feature=orb-flann ../data/box_in_scene.png ../data/box.png
```

* 其他例子

   * 人脸识别 facedetect.py

## 参考文档


* OpenCV 2d特征教程 [https://docs.opencv.org/master/d9/d97/tutorial_table_of_content_features2d.html](https://docs.opencv.org/master/d9/d97/tutorial_table_of_content_features2d.html)

