# 获取 orb 关键点： 2000, 5000, 8000
bash query-feature.sh 2000
bash query-feature.sh 5000
bash query-feature.sh 8000

# 获取九宫格 orb 关键点: 200, 400, 600, 800
bash query-feature.sh 200 orb grid
bash query-feature.sh 400 orb grid
bash query-feature.sh 600 orb grid
bash query-feature.sh 800 orb grid

# 获取 asift 关键点: 600, 800
bash query-feature.sh 600 asift
bash query-feature.sh 800 asift

# 获取九宫格 asift 关键点: 100, 200
bash query-feature.sh 100 asift grid
bash query-feature.sh 200 asift grid

# 获取测试点 orb 关键点: 1000, 2000, 3000
bash test-query-feature.sh 1000
bash test-query-feature.sh 2000
bash test-query-feature.sh 3000

# 获取测试点九宫格 orb 关键点: 200, 300, 400, 500
bash test-query-feature.sh 200 orb grid
bash test-query-feature.sh 300 orb grid
bash test-query-feature.sh 400 orb grid
bash test-query-feature.sh 500 orb grid

# 匹配相邻照片，简单过滤
bash match-feature.sh features/orb-2000 orb n
bash match-feature.sh features/orb-5000 orb n
bash match-feature.sh features/orb-8000 orb n
bash match-feature.sh features/orb-g200 orb n
bash match-feature.sh features/orb-g400 orb n
bash match-feature.sh features/asift-600 asift n
bash match-feature.sh features/asift-800 asift n
bash match-feature.sh features/asift-g100 asift n

# 匹配相邻照片，使用 fundamental 方法过滤
bash match-feature.sh features/orb-2000 orb f
bash match-feature.sh features/orb-5000 orb f
bash match-feature.sh features/orb-8000 orb f
bash match-feature.sh features/orb-g200 orb f
bash match-feature.sh features/orb-g400 orb f
bash match-feature.sh features/asift-600 asift f
bash match-feature.sh features/asift-800 asift f
bash match-feature.sh features/asift-g100 asift f

# 匹配相邻照片，使用 homography 方法过滤
bash match-feature.sh features/orb-2000 orb h
bash match-feature.sh features/orb-5000 orb h
bash match-feature.sh features/orb-8000 orb h
bash match-feature.sh features/orb-g200 orb h
bash match-feature.sh features/orb-g400 orb h
bash match-feature.sh features/asift-600 asift h
bash match-feature.sh features/asift-800 asift h
bash match-feature.sh features/asift-g100 asift h

# 查询照片匹配，使用 homography 方式过滤（默认）
bash test-match-feature.sh features/test-orb-2000 features/orb-8000
bash test-match-feature.sh features/test-orb-3000 features/orb-5000
bash test-match-feature.sh features/test-orb-g200 features/orb-g800

# 查询照片匹配，参考照片使用 asift，使用  方式过滤（默认）
bash test-match-feature.sh features/test-orb-2000 features/asift-800 asift f
bash test-match-feature.sh features/test-orb-2000 features/asift-g100 asift f
bash test-match-feature.sh features/test-orb-g200 features/asift-800 asift f
bash test-match-feature.sh features/test-orb-g200 features/asift-g100 asift f

# asift-100  asift-g100  orb-8000  orb-g800       test-orb-g200
# asift-200  asift-g200  orb-g200  test-orb-1000  test-orb-g300
# asift-600  orb-2000    orb-g400  test-orb-2000  test-orb-g400
# asift-800  orb-5000    orb-g600  test-orb-3000  test-orb-g500
