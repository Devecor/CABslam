# 获取 orb 关键点 8000
bash ../test5/query-feature.sh images features 8000
bash ../test5/query-feature.sh images "features/test-" 2000

bash ../test5/query-feature.sh images/star features 20000


# 获取 asift 关键点: 800
# bash query-feature.sh images features 800 asift

# 匹配采集点的参考照片
bash ../test5/match-feature.sh ../test5/star-input.txt "matches" features/orb-8000 features/orb-8000

bash ../test5/match-feature.sh star-input.txt "matches" features/orb-20000 features/orb-20000

bash ../test5/match-feature.sh star-input.txt "matches/f-" features/orb-8000 features/orb-8000 f
bash ../test5/match-feature.sh star-input.txt "matches/n-" features/orb-8000 features/orb-8000 n

# 匹配测试点和采集点
bash ../test5/match-feature.sh ../test5/test-star-input.txt matches features/test-orb-2000 features/orb-8000

bash ../test5/match-feature.sh test-star-input.txt "matches/f-" features/test-orb-2000 features/orb-8000 f
bash ../test5/match-feature.sh test-star-input.txt "matches/n-" features/test-orb-2000 features/orb-8000 n

# 使用辅助照片进行匹配
bash match-feature.sh test-star-input2.txt matches features/orb-2000 features/orb-8000

# 汇总匹配结果
gawk -f ../test3/sum-match.awk results/match-h-result-orb-8000.test-orb-2000.test-star-input.txt
gawk -f ../test3/sum-match.awk results/match-h-result-orb-8000.test-orb-2000.test-star-input2.txt

# 生成星型采集关键点的三维坐标库
bash ../test5/build-model.sh model-input.txt "models" features/orb-8000
bash ../test5/build-model.sh model-input.txt "models" features/orb-20000

# 查询定位
bash ../test5/query-location.sh test-star-input.txt locations features/test-orb-2000 models

# 汇总定位结果
gawk -f ../test3/sum-location.awk results/location-h-models.test-orb-2000.test-star-input.txt

# 查看三维点坐标计算结果和查看定位结果（调试）
# cd ../
# c:/Python27/python check_point3d.py --offset=-10,0,0 --yaw=0 --focal=0.9722,0.7292 test5/images/s1-1.jpg test5/images/s1-1a.jpg
C:/Python27/python ../make_model.py --size=2448,3264 --focals=0.9722,0.7292 --show --homography --refpos=-10,0,0 features/orb-8000/s1-1-orb.npz features/orb-8000/s1-1a-orb.npz

# c:/Python27/python ../query_location.py --size=2448,3264 --focals=0.9722,0.7292 --save --output=locations/models.orb-2000 --homography features/orb-2000/t1-1-orb models/s1-1 models/s1-2 models/s1-3 models/s1-4 models/s1-5
c:/Python27/python ../query_location.py --size=2448,3264 --focals=0.9722,0.7292 --homography features/test-orb-2000/t1-3-orb models/s1-2


# 转换坐标系
gawk -f transform-location.awk results/location-origin-results.txt > results/location-results.txt

# 计算误差
gawk -f location-errors.awk results/location-results.txt
