# Detect lear's gist feature

this document is an introduction of the learGistDescriptor's usage. 
it's implemented using MATLAB.

### Minisize the use of MATLAB through the commond line ###

**According to the startup parameters of MATLAB, we can,**  

Use MATLAB in the current terminal for commands. __more details__: `matlab -h`

```matlab
matlab -nosplash -nodesktop
```

Start MATLAB and execute the MATLAB_commond:

```matlab
matlab -r
```

Minisize the start of MATLAB and execute commonds:

```
matlab -nosplash -nodesktop -r MATLAB_commond
```

### learGistDescriptor's usage:

#### the function:

```matlab
function [gist, param] = LMgist(D, HOMEIMGS,
    param, HOMEGIST);
```
**usage:**
```python
'''
parameters:
-----------
    D: {cell, numenic, or matlab_struct}
        the data of image, it can be a cell, a struct, or a numenic array.
    HOMEGIST: {string}
        the path to input image
    param: {matlab_struct}
        for nargin < 3, it's default value:
            param.imageSize = 128;
            param.orientationsPerScale = [8 8 8 8];
            param.numberBlocks = 4;
            param.fc_prefilt = 4;
            param.G = createGabor(param.orientationsPerScale, param.imageSize+2
                *param.boundaryExtension);
        for nargin = 4, required param's key-value are as follows:
            param.orientationsPerScale = [8 8 8 8];
            param.numberBlocks = 4;
            param.fc_prefilt = 4;
    HOMEGIST: {string}
        it's gist's path that you want to save
returns:
--------
    gist: {numenic} the gist features
    param: {matlab_struct} some important attributes. it's useful to debug
'''
```

you can call this function in these ways:

```matlab
[gist, param] = LMgist(D, HOMEIMAGES, param);

[gist, param] = LMgist(filename, HOMEIMAGES, param);

[gist, param] = LMgist(filename, HOMEIMAGES, 
    param, HOMEGIST);
```

**NOTICE:**  
_When calling LMgist with a fourth argument it will store the gists in a new folder structure mirroring the folder structure of the images. Then,when called again, if the gist files already exist, it will just readthem without recomputing them:_

#### for a set of images:

```matlab
gist = LMgist(img, [], param);
```

#### Run this code in a shell to figure it out:

```bash
cd gistDescriptor_matlab
matlab -nosplash -nodesktop -r demoGist
matlab -nosplash -nodesktop -r 'gist = LMgist(demo1.jpg, [], param)'
```

**NOTICE:**  
the param in LMgist() is a MATLAB struct:

```matlab
param.imageSize = [row col];
param.orientationsPerScale = [8 8 8 8];
param.numberBlocks = 4;
param.fc_prefilt = 4;
```
## some matlab syntax:

**示例 1 -** 单个字段名称语法
给定以下 MATLAB® 结构体，

```matlab
patient.name = 'John Doe';
patient.billing = 127.00;
patient.test = [79 75 73; 180 178 177.5; 220 210 205];
```

isfield 确定 billing 为该结构体的字段。

```matlab
isfield(patient,'billing')
ans = 1
```
多字段名称语法  
在结构体 S 中检查任意四个可能的字段名称。仅找到第一个，因此返回值的第一个元素设置为 true：

```matlab
S = struct('one', 1, 'two', 2);

fields = isfield(S, {'two', 'pi', 'One', 3.14})
fields = 1     0     0     0
```
*tips:*`~`is logical not in matlab

**示例 2 -** size()函数,

* `sz = size(A)` 返回一个行向量，其元素包含 A 的相应维度的长度。
    1. 如果 A 是一个 3×4 矩阵，则 `size(A)` 返回向量 `[3 4]`。sz 的长度为 `ndims(A)`
    2. 如果 A 是表或时间表，则 `size(A)` 返回由表中的行数和变量数组成的二元素行向量。
* 示例`szdim = size(A,dim)` 返回维度 dim 的长度。

* 示例 当 A 是矩阵时，`[m,n] = size(A)` 返回行数和列数。

* 示例`[sz1,...,szN] = size(A)` 分别返回 A 的每个维度的长度。

**示例 3 -** 在 UNIX 上创建完整文件路径:

fullfile 返回包含文件完整路径的字符向量。在 UNIX® 平台上，文件分隔符为正斜杠 (/)。
```matlab
f = fullfile('myfolder','mysubfolder','myfile.m')
f = 
'myfolder/mysubfolder/myfile.m'
```

在 Windows 上创建多个文件的路径
fullfile 返回一个元胞数组，其中包含文件 myfile1.m 和 myfile2.m 的路径。
```matlab
f = fullfile('c:\','myfiles','matlab',{'myfile1.m';'myfile2.m'})
f =

  2×1 cell array

    'c:\myfiles\matlab\myfile1.m'
    'c:\myfiles\matlab\myfile2.m'
```


*more details:* [link to mathwork!](https://ww2.mathworks.cn/help/matlab/index.html)