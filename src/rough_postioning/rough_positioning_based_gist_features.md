# rough postioning based gist features

## 一、概述

本文旨在基于图像Gist特征的检索与匹配技术，实现室内场景的粗定位。  
  
**定位原理：**  
对于一定的室内场景，建立一张合适粒度的Gist地图，该地图由每一个坐标点所拍摄图像的Gist特征构成。Gist特征本质上是一个512维的列（行）向量，本文称之为Gist特征向量，简称Gist特征，以`VecG`表示。  
地图（MapG）由若干个参考点组成，参考点形如`[x, y, VecG]`。则地图可用nx3维矩阵表示:  

<!-- $$
MapG=
\left\{
    \begin{matrix}
    \left[
        x_1, y_1,\ VecG_1
    \right]\\ \\
    \left[
        x_2,\ y_2,\ VecG_2
    \right]\\

       \ \ldots,\ \ldots,\ \  \ldots \ \ 
    \\
    \left[
        x_n,\ y_n,\ VecG_n
    \right]
    \end{matrix}
\right\}
$$ -->

<img src="http://chart.googleapis.com/chart?cht=tx&chl= $$MapG=\left\{\begin{matrix}\left[x_1,y_1,VecG_1\right]\\ \\ \left[x_2,y_2,VecG_2\right] \\ \ldots \\ \left[x_n,y_n,VecG_n\right]\end{matrix}\right\}$$" style="border:none;" align="middle"/>  

利用用户的提供照片的Gist特征，在MapG中进行检索匹配，本文认为匹配度最大的点**周围的四个点**所形成的菱形区域是最可能的用户位置

**检索算法:**

为了更加快速的找到匹配的最大的目标参考点，需要选用合适的查找算法，为简单起见，本次实验使用**顺序查找**的办法实现。

**匹配算法:**

此算法旨在解决如何计算Gist特征的相似程度的问题，这对能否正确进行粗定位至关重要。本文使用图像距离来表示相似程度，例如：
```matlab
D = sum((gist1-gist2).^2)
```

## 二、实验目的

1. 明确业务逻辑，初步实现整体框架

2. 验证基于Gist特征检索匹配技术的粗定位解决方案的可行性

## 三、实验内容

1. 利用实验场地的平面图建立适当的坐标系，确定布点方案,将坐标系、参考点及测试点标出，存于Spots.jpg中便于后期分析验证

2. 各参考点和测试点每隔45$\degree$拍摄一次(使用极角，正东为0，逆时针为正)，共八张，命名规范：**A-x-y-N.jpg T-x-y-N.jpg**，其中，A为参考点标志，T为测试点标志，N为角度标志，取值范围1-8

3. 批量提取Gist特征，检索匹配，将定位结果保存于gist_res.csv

4. 误差计算,
