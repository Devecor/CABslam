# 建筑物数据目录结构

```
   BUILDING-NAME/
       index.json
       refimages/
           config.json
           IMG-INDEX-原始图片文件名称
       refplanes/
            config.json
            参考平面数据文件.npz
       r0.json
       r1.json
       ...

```

# JSON 配置文件

每一栋建筑物都有一个 index.json 文件，存放在建筑物目录下面，用于保存区
域列表和Wifi列表的索引数据。

每一个区域都有一个对应的子目录 rN, 存放在建筑物目录下面，其中 N 是对应
的区域索引号，从 0 开始。

每一个建筑物都有一个

## 建筑物配置文件: index.json

每个建筑物都有一个 index.json 来记录其中的 wifi 和 区域索引。例如

```
{
  "title": "西北大学物信大楼",

  "location": [ x0, y0, z0 ],

  "wifis": [
             {
                "bssid": "xxxx",
                "ssid": "yyyy",
                "frequency": 2.5
             },
             ...
           ],

  "bssids": [ "aa-bb-cc-dd", "aa-cc-ff-ak" ],

  "regions": [
               {
                  "title": "xxxx",
                  "height": [ h1, h2 ],
                  "polygon": [ [x0, y0], [x1, y1], ... ],
               },
               ...
             ]
}

```

### title

建筑物标题

### location

建筑物的原点坐标，使用 EPSG:4326 表示的建筑物地球空间坐标，单位为 米。

### wifis

所有的 wifi 列表。

#### bssid

wifi 对应的 BSSID。

#### ssid

wifi 对应的 SSID。

#### frequency

wifi 对应的频道，数值，单位为 GHZ。

### bssids

wifi 对应的 BSSID 的列表，用于根据 BSSID 快速定位索引。

### regions

所有的区域定义列表。

#### title

区域标题

#### height

区域的高度范围，以建筑物原点高度为 0 的相对值，单位为 米。

#### polygon

区域对应的多边形坐标坐标，以建筑物原点为参考，单位为 米。

## 区域参考图片配置文件: images.json

每一个区域目录下面有一个 images.json ，格式如下

```
[
  {
    "name": "xxxxx",
    "position": [ x0, y0, z0 ],
    "azimuth": 0,
    "camera": [ fx, fy, cx, cy ]
  },
  ...
]
```
### name

照片名称，格式一般为 img-YYYYMMDD-HHMMSS

### position

照片拍摄的位置，相对于建筑物原点的坐标，单位为 米

### azimuth

拍摄角度，以正北方向为 0 度，向东为正，向西为负，范围 正负 180 度，其中
正负180度都是正南方向。

### camera

参考相机参数，一般为 fx, fy, cx, cy.

## 区域配置文件: cofig.json

每一个区域有其配置文件

### refimages

列表，存放所有的关联图片文件名称，例如 img-20171020-123829

### refplanes

列表，存放所有关联的参考平面数据文件，这是包含数据的文件

## 图片配置文件：config.json

例如

```
  { "id": 102,
    "name": "img-20171020-123829",
    "filename": "house-plan.jpg",
    "position": [ x0, y0, z0 ],
    "azimuth": 0,
    "camera": [ fx, fy, cx, cy ]
    "refplanes": [ "name1", "name2", "name3"]
  }
```

## 参考平面配置文件：config.json

```
  {
    "mode0" : {
      "title": "asift匹配算法',
      "asift": false,
      "feature": "orb",
      ...
    },
    ...
    }
```

## 参考平面数据文件： xxx.npz

是 numpy 压缩格式的数据，包括

### camera

相机参数 fx, fy, cx, cy

### pose

拍摄位置 x, y, z 和 方位角 a

方位角正北为0，向东为正，向西为负，正负180之间

### feature

特征名称，例如 orb, sift 等

### keypoints

关键点

### descriptors

描述符
