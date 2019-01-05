# github 基本使用方法


## 初始化库

```
    cd /home/myname/workspace
    git clone https://github.com/jondy/istar.git
```

## 初始化实验文档

每一次实验开始之前，先把 test15.md 提交到服务器

```
    # 确保当前在 master 分支
    git checkout master

    cd src/verify
    mkdir test15

    # 添加文件 test15.md, test-spots.jpg ...
    git add test15.md
    git commit -m'Add test doc' test15.md
    git push
```

## 提交工作文档

因为 test15 不是共同使用的文档，所以一般可以直接在 master 分支下面修改
和提交所有文档。

```
    cp ../test9/*.sh ./
    cp ../test9/*.awk ./
    git commit -m'Add scripts' *.sh *.awk
    git push

    # 修改之后
    git commit -m'XXXX' files
    git push

```

### 提交更新后的文件

文档一般修改之后，及时 push 一下到服务器。譬如 测试报告中的 匹配结果出
来了，也可以先提交上去

```
    git add results/match-h-result-orb-8000.test-orb-2000.test-star-input.txt
    # 添加内容到 test15.md
    git commit -m'Add match results' test15.md results/match-h-result-orb-8000.test-orb-2000.test-star-input.txt
    git push
```

不要等最后完成之后再一次性提交。

## 创建 pull request

对于公共使用的文档，则需要创建分支，并提交 pull request，例如修改 verify 下面的 query_location.py

```
    git checkout -B new-feature
    # 现在是在新分支 new-feature 下面，这时候可以修改，调试代码

    # 增加了第一个新功能
    git commit -m'Add print match keypoints' query_location.py

    # 继续修改调试，解决了一个问题
    git commit -m'Fix bug' query_location.py

    # 修改好之后，push 新分支到服务器
    git push origin new-feature

    # 最后到 github 创建一个 pull request

    # 切换回主分支
    git checkout master
```

## 更新主分支

主分支是大家共同工作的分支，要经常更新一下，

```
    git pull

```

执行 pull 之前要确认没有修改过公共文件，否则可能产生冲突。

## 创建工作分支

可以创建自己的工作分支，这个分支一般不要 push 到服务器，仅在本地使用

```
    git checkout -B mywork
```

### 工作分支的内容提交到主分支

一般不要直接 merge 到主分支上去，现在暂时采用这样的方式，假设工作分支有
两个文件 a.md results/b.txt ，提交到服务器 master 分支

```
    # 切换到主分支
    git checkout master

    # 把工作分支的文件内容更新到主分支
    git checkout mywork a.md results/b.txt

    git commit -m'Do something' a.md results/b.txt
    git push

```

## 上传大文件到 release

```
curl -H "Authorization: token <yours>" \
     -H "Accept: application/vnd.github.jean-grey-preview+json" \
     -H "Content-Type: application/zip" \
     --data-binary @build/mac/package.zip \
     "https://api.github.com/repos/jondy/istar/releases/t01-16/assets?name=images.zip"
```

Refer to https://github.com/blog/1645-releases-api-preview
Refer to https://developer.github.com/v3/repos/releases/
