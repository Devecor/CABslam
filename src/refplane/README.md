# 平面特征定位实验指导书

每一个实验会有一个对应的 [issues](https://github.com/jondy/istar/issues)，里面有实验编号，实验目的和要求

* 创建目录和初始文件

    按照本次试验的编号，例如创建 `test10`，实验文件的目录结构如下

```
    test10/
        README.md
        photo-records.txt
        photo-spots.jpg
        results/

        build.sh

        上面目录中的所有内容要上传到 github 服务器，其他目录下的文件不要上传到服务器

```

* 编写实验文档

    * README.md

        参考[template/README.md](template/README.md)

    * photo-records.txt

        照片拍摄记录，参考[template/photo-records.txt](template/photo-records.txt)

    * photo-spots.jpg

        参考[template/photo-spots.jpg](template/photo-spots.jpg)

* 拍摄照片

    * 上传照片

        将原始照片压缩成为 `images.zip`，上传到本次实验对应的 [issues](https://github.com/jondy/istar/issues)

    * 更新照片记录文件 `photo-records.txt`

        在最后面一列把对应的文件名称填充进去，**使用列块操作方式，不要一个一个的拷贝！**


* 编写 `build.sh`

    根据实验要求，编写脚本，要求所有的输出结果都有对应的生成脚本，参考 [template/build.sh](template/build.sh)

* 执行 `build.sh`

    生成的结果文件将存放在 `results`, 上传生成的结果文件

* 完成实验报告

    根据实验结果进行分析，将最终的实验结论填写到 `README.md`

## 文件命名规范

* 参考照片: `rN-dM.jpg`

    N 为编号，M 为距离，例如 `r1-d200.jpg`

* 正前方测试照片: `tN-dM.jpg`

    N 为编号，M 为距离，例如 `t1-d300.jpg`

* 左边测试照片: `tN-dM-lD.jpg`

    使用小写的 `L` 表示，D 表示偏移量，例如 `t2-d300-l320.jpg`

* 右边测试照片: `tN-dM-rD.jpg`

    使用 r 表示，D 表示偏移量，例如 `t3-d300-r100.jpg`

* 缩放比例的照片, `-xS`

    使用 x 表示，S 是缩放比例，测试照片都可以增加这个部分，例如 `t4-d300-x1.5.jpg`, `t5-d300-r15-x1.6.jpg`

* 特征关键点数据存放在 `features`, 命令规范： 照片名称-orb-特征参数

    例如，`r1-d100-orb-asift3-n800.npz` `t2-d200-r15-orb-n2000.npz`

* 三维坐标数据存放在 `models`, 命令规范： 照片名称-orb-特征参数

    例如，`r1-d100-orb-asift3-n800.npz`

* 实验最终需要提交的结果数据存放在 `results`，命令规范： 特征参数

    每一组实验结果存放在一个目录下面，例如参考照片使用 asift=3, n=800，最终的输出结果
    
```
    results/asift3-n800
        r1-d100.txt
        r2-d200.txt
        r3-d300.txt
```

* 调试数据存放在 `output`
