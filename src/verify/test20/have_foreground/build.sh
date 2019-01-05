# 获取 orb 关键点 8000
bash query-feature.sh images/star features 8000
bash query-feature.sh images/tp "features/test-" 2000

# 匹配采集点的参考照片
bash match-feature.sh star-input.txt "matches" features/orb-8000 features/orb-8000 

# 匹配测试点和采集点
bash match-feature.sh test-star-input.txt "matches" features/test-orb-2000 features/orb-8000

# 汇总匹配结果
gawk -f sum-match.awk results/match-h-result-orb-8000.test-orb-2000.test-star-input.txt

# 生成星型采集关键点的三维坐标库
bash build-model.sh model-input.txt "models" features/orb-8000 f

# 查询定位
bash query-location.sh test-star-input.txt locations features/test-orb-2000 models h
bash query-location.sh test-star-input.txt locations features/test-orb-2000 models n
bash query-location.sh test-star-input.txt locations features/test-orb-2000 models f

# 汇总定位结果
gawk -f sum-location.awk results/location-h-models.test-orb-2000.test-star-input.txt
gawk -f sum-location.awk results/location-n-models.test-orb-2000.test-star-input.txt
gawk -f sum-location.awk results/location-f-models.test-orb-2000.test-star-input.txt

# 转换坐标系
gawk -f transform-location.awk results/location-h-models.test-orb-2000.test-star-input.txt > results/location-results-h.txt
gawk -f transform-location.awk results/location-n-models.test-orb-2000.test-star-input.txt > results/location-results-n.txt
gawk -f transform-location.awk results/location-f-models.test-orb-2000.test-star-input.txt > results/location-results-f.txt

# 计算误差
gawk -f location-errors.awk results/location-results-h.txt > results/location-errors-h.txt
gawk -f location-errors.awk results/location-results-n.txt > results/location-errors-n.txt
gawk -f location-errors.awk results/location-results-f.txt > results/location-errors-f.txt

# 统计结果
gawk -f group-errors.awk results/location-errors-n.txt > results/group-errors-n.txt
gawk -f group-errors.awk results/location-errors-f.txt > results/group-errors-f.txt
gawk -f group-errors.awk results/location-errors-h.txt > results/group-errors-h.txt

gawk -f group-location.awk results/location-errors-n.txt > results/group-location-n.txt
gawk -f group-location.awk results/location-errors-f.txt > results/group-location-f.txt
gawk -f group-location.awk results/location-errors-h.txt > results/group-location-h.txt

gawk -f group-failed.awk results/location-errors-n.txt > results/group-failed-n.txt
gawk -f group-failed.awk results/location-errors-f.txt > results/group-failed-f.txt
gawk -f group-failed.awk results/location-errors-h.txt > results/group-failed-h.txt


