# 获取 orb 关键点 8000
bash ../test5/query-feature.sh images/star features 8000
bash ../test5/query-feature.sh images/tp "features/test-" 2000

# 获取 asift 关键点: 800
# bash query-feature.sh images/star features 800 asift

# 匹配采集点的参考照片
bash ../test5/match-feature.sh star-input.txt "matches" features/orb-8000 features/orb-8000
bash ../test5/match-feature.sh star-input.txt "matches/f-" features/orb-8000 features/orb-8000 f

# 匹配测试点和采集点
gawk -f make-test-star.awk test-ref-star.txt > test-star-input.txt
bash ../test5/match-feature.sh test-star-input.txt "matches" features/test-orb-2000 features/orb-8000
bash ../test5/match-feature.sh test-star-input.txt "matches/f-" features/test-orb-2000 features/orb-8000 f

# 汇总匹配结果
gawk -f ../test3/sum-match.awk results/match-h-result-orb-8000.test-orb-2000.test-star-input.txt

# 生成星型采集关键点的三维坐标库
bash ../test5/build-model.sh model-input.txt "models" features/orb-8000

# 查询定位
bash ../test5/query-location.sh test-star-input.txt locations features/test-orb-2000 models

# 汇总定位结果
gawk -f ../test3/sum-location.awk results/location-h-models.test-orb-2000.test-star-input.txt

# 转换坐标系
gawk -f ../test6/transform-location.awk results/location-origin-results.txt > results/location-results.txt

# 计算误差
gawk -f location-errors.awk results/location-results.txt

# 纠正选择错误的测试点
c:/Python27/python ../query_location.py --size=2448,3264 --focals=0.9722,0.7292 --homography features/test-orb-2000/t1-2-orb models/s1-1 --save
