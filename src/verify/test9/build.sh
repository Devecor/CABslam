ln -s ../test8/star-input.txt
ln -s ../test8/test-star-input.txt
ln -s ../test8/model-input.txt

# 获取 orb 关键点 8000
bash ../test5/query-feature.sh images/star features 8000
bash ../test5/query-feature.sh images/tp "features/test-" 2000

# 获取 asift 关键点: 800
# bash query-feature.sh images/star features 800 asift

# 匹配采集点的参考照片
bash ../test5/match-feature.sh star-input.txt "matches" features/orb-8000 features/orb-8000
bash ../test5/match-feature.sh star-input.txt "matches/f-" features/orb-8000 features/orb-8000 f

# 匹配测试点和采集点
bash ../test5/match-feature.sh test-star-input.txt "matches" features/test-orb-2000 features/orb-8000
bash ../test5/match-feature.sh test-star-input.txt "matches/f-" features/test-orb-2000 features/orb-8000 f

# 汇总匹配结果
gawk -f ../test3/sum-match.awk results/match-h-result-orb-8000.test-orb-2000.test-star-input.txt

# 生成星型采集关键点的三维坐标库
bash ../test5/build-model.sh model-input.txt "models" features/orb-8000
bash ../test5/build-model.sh model-input.txt "models/fund" features/orb-8000 f

# 查询定位
bash ../test5/query-location.sh test-star-input.txt locations features/test-orb-2000 models

# 汇总定位结果
gawk -f sum-location.awk results/location-h-models.test-orb-2000.test-star-input.txt
gawk -f sum-location.awk results/location-h-fund.test-orb-2000.test-star-input.txt

# 转换坐标系
gawk -f transform-location.awk results/location-h-fund.test-orb-2000.test-star-input.txt > results/location-results.txt

# 计算误差
gawk -f location-errors.awk results/location-results.txt > results/location-errors.txt

# 纠正选择错误的测试点
c:/Python27/python ../query_location.py --size=2448,3264 --focals=0.9722,0.7292 --homography features/test-orb-2000/t1-2-orb models/s1-1 --save

# 不使用 homography 的定位和误差
bash ../test5/query-location.sh test-star-input.txt locations/simple features/test-orb-2000 models/fund n
gawk -f transform-location.awk results/location-n-fund.test-orb-2000.test-star-input.txt > results/location-simple-results.txt
gawk -f location-errors.awk results/location-simple-results.txt > results/location-simple-errors.txt
gawk -f group-location.awk results/location-simple-errors.txt

# 分组统计

bash ../test5/query-location.sh test-star-input.txt locations/test features/test-orb-2000 models/test f
gawk -f transform-location.awk results/location-f-test.test-orb-2000.test-star-input.txt > results/location-f-test-10.1-results.txt
gawk -f location-errors.awk results/location-f-test-10.1-results.txt > t9-f.txt
gawk -f group-errors.awk t9-f.txt
gawk -f group-location.awk t9-f.txt

bash ../test5/query-location.sh test-star-input.txt locations/test features/test-orb-2000 models/test h
gawk -f transform-location.awk results/location-h-test.test-orb-2000.test-star-input.txt > results/location-h-test-10.1-results.txt
gawk -f location-errors.awk results/location-h-test-10.1-results.txt > t9-h.txt
gawk -f group-errors.awk t9-h.txt
gawk -f group-location.awk t9-h.txt

gawk -f group-failed results/location-n-test.test-orb-2000.test-star-input.txt
gawk -f group-failed results/location-h-test.test-orb-2000.test-star-input.txt
gawk -f group-failed results/location-f-test.test-orb-2000.test-star-input.txt

# 分组统计， TEST16

gawk -f ../test9/transform-location.awk results/Manual_Matching_All_Images_Location_Results/location-h-models.test-orb-3000.test-star-input.txt > results/location-h-models-10.0-results.txt
gawk -f location-errors2.awk results/location-h-models-10.0-results.txt > t16-h-manual.txt
gawk -f group-errors.awk t16-h-manual.txt
gawk -f ../test9/group-location.awk t16-h-manual.txt
gawk -f region-errors.awk t16-h-manual.txt

gawk -f ../test9/transform-location.awk results/location-f-models.test-orb-3000.test-star-input.txt > results/location-f-models-10.0-results.txt
gawk -f location-errors2.awk results/location-f-models-10.0-results.txt > t16-f.txt
gawk -f group-errors.awk t16-f.txt
gawk -f ../test9/group-location.awk t16-f.txt
gawk -f region-errors.awk t16-f.txt

gawk -f ../test9/transform-location.awk results/location-n-models.test-orb-3000.test-star-input.txt > results/location-n-models-10.0-results.txt
gawk -f location-errors2.awk results/location-n-models-10.0-results.txt > t16-n.txt
gawk -f group-errors.awk t16-n.txt
gawk -f ../test9/group-location.awk t16-n.txt
gawk -f region-errors.awk t16-n.txt

gawk -f ../test9/group-failed results/location-n-models.test-orb-3000.test-star-input.txt
gawk -f ../test9/group-failed results/Manual_Matching_All_Images_Location_Results/location-h-models.test-orb-3000.test-star-input.txt
gawk -f ../test9/group-failed results/location-f-models.test-orb-3000.test-star-input.txt

gawk -f ../test9/transform-location.awk results/All_Images_Location_Results/location-h-models.test-orb-3000.test-star-input.txt > results/location-h-models-10.0-results-2.txt
gawk -f location-errors2.awk results/location-h-models-10.0-results-2.txt > t16-h.txt
gawk -f group-errors.awk t16-h.txt
gawk -f ../test9/group-location.awk t16-h.txt
gawk -f region-errors.awk t16-h.txt
gawk -f ../test9/group-failed.awk results/All_Images_Location_Results/location-h-models.test-orb-3000.test-star-input.txt

gawk -f ../test9/transform-location.awk results/Remove_Partly_PIC_Location_Results/location-h-models.test-orb-3000.test-star-input.txt > results/location-h-models-10.0-results-r.txt
gawk -f location-errors2.awk results/location-h-models-10.0-results-r.txt > t16-h-r.txt
gawk -f group-errors.awk t16-h-r.txt
gawk -f ../test9/group-location.awk t16-h-r.txt
gawk -f region-errors.awk t16-h-r.txt
gawk -f ../test9/group-failed.awk results/Remove_Partly_PIC_Location_Results/location-h-models.test-orb-3000.test-star-input.txt


gawk -f ../test9/transform-location.awk results/Remove_Partly_PIC_Location_Results-n/location-n-models.test-orb-3000.test-star-input.txt > results/location-n-models-10.0-results-r.txt
gawk -f location-errors2.awk results/location-n-models-10.0-results-r.txt > t16-n-r.txt
gawk -f group-errors.awk t16-n-r.txt
gawk -f ../test9/group-location.awk t16-n-r.txt
gawk -f region-errors.awk t16-n-r.txt
gawk -f ../test9/group-failed.awk results/Remove_Partly_PIC_Location_Results-n/location-n-models.test-orb-3000.test-star-input.txt
