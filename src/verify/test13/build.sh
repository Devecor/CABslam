
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
bash query-location.sh test-star-input.txt locations features/test-orb-2000 models

# 汇总定位结果
gawk -f sum-location.awk results/location-h-models.test-orb-2000.test-star-input.txt

# 转换坐标系
gawk -f transform-location.awk results/location-h-models.test-orb-2000.test-star-input.txt > results/location-results.txt

# 计算误差
gawk -f location-errors.awk results/location-results.txt > results/location-errors.txt

