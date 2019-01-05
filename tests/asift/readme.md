# ASIFT-SIFT 算法比较结果说明 #

原始图片存放在 [coffee-images](coffee-images) ，分别使用 [coffee-images/IMG_1968.JPG](coffee-images/IMG_1968.JPG) 和其他图片进行比较

## SIFT 参数 ##

* nfeatures = 2000

    The number of best features to retain. The features are ranked by their scores (measured in SIFT algorithm as the local contrast)

* nOctaveLayers = 3

    The number of layers in each octave. 3 is the value used in D. Lowe paper. The number of octaves is computed automatically from the image resolution.

* contrastThreshold = 0.04,

    The contrast threshold used to filter out weak features in semi-uniform (low-contrast) regions. The larger the threshold, the less features are produced by the detector.

* edgeThreshold = 10

    The threshold used to filter out edge-like features. Note that the its meaning is different from the contrastThreshold, i.e. the larger the edgeThreshold, the less features are filtered out (more features are retained).

* sigma = 1.6

    The sigma of the Gaussian applied to the input image at the octave #0. If your image is captured with a weak camera with soft lenses, you might want to reduce the number.


## ASIFT 参数 ##

ASIFT 同样使用 SIFT 来描述关键点，共取样 43 个，其数值 (tilt, phi) 分别为

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

匹配的图片结果存放在 [match](match) 下面，例如

- [match/sift_IMG_1970.JPG](match/sift_IMG_1970.JPG)
- [match/asift_IMG_1970.JPG](match/asift_IMG_1970.JPG)
    
分别表示使用两种算法匹配 IMG_1968.JPG 和 IMG_1970.JPG 的结果。

因为 ASIFT 算法特别慢，为了加快速度，对图片进行缩放，例如缩放为原图 35% 的匹配结果图片命名为

- asift_s35_IMG_1970.JPG
    
匹配的详细信息分别存放在文件

- [match/sift_result.txt](match/sift_result.txt)
- [match/asift_result.txt](match/asift_result.txt)
    
    
# 参考链接 #

<http://www.ipol.im/pub/art/2011/my-asift/article_lr.pdf>
