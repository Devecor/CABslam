# 获取 orb 关键点 8000
bash query-feature.sh images/star features 8000
bash query-feature.sh images/star-up6.2 features 8000
bash query-feature.sh images/star-up6 features 8000

# 获取 asift 关键点: 800
bash query-feature.sh images/star features/ 800 asift
bash query-feature.sh images/star-up6.2 features 800 asift

# 获取 asift 关键点: 800
bash query-feature.sh images/plane "features/plane-" 800 asift

# 获取测试点 orb 关键点 2000
bash query-feature.sh images/tp "features/test-" 2000
bash query-feature.sh images/tp "features/test-" 3000

# 匹配平面特征的参考照片
bash match-feature.sh plane-input.txt matches features/plane-asift-800 features/plane-asift-800

# 匹配星型采集点的参考照片
bash match-feature.sh star-input.txt matches features/orb-8000 features/orb-8000
bash match-feature.sh star-input2.txt matches features/orb-8000 features/orb-8000

# 生成平面特征关键点的三维坐标库
bash build-model.sh plane-input.txt models features/plane-asift-800 "6,0,0"

# 生成星型采集关键点的三维坐标库
bash build-model.sh star-input.txt models features/orb-8000 "0,6.2,0"
bash build-model.sh star-input2.txt models features/orb-8000 "0,6,0"

# 匹配测试点和平面特征
gawk -f make-test-plane.awk test-input.txt plane-input.txt test-ref-plane.txt > test-plane-input.txt
bash match-feature.sh test-plane-input.txt matches features/test-orb-2000 features/plane-asift-800
bash match-feature.sh test-plane-input.txt matches features/test-orb-3000 features/plane-asift-800

# 匹配测试点和星型采集点
gawk -f make-test-star.awk test-input.txt star-input.txt test-ref-star.txt > test-star-input.txt
bash match-feature.sh test-star-input.txt matches features/test-orb-2000 features/orb-8000
bash match-feature.sh test-star-input.txt matches features/test-orb-3000 features/orb-8000
bash match-feature.sh test-star-input.txt matches features/test-orb-2000 features/asift-800

# 替换匹配结果文件中图片名称为 tM-N 的格式
bash rename-tp.sh results/match-h-result-plane-asift-800.test-orb-2000.test-plane-input.txt
bash rename-tp.sh results/match-h-result-plane-asift-800.test-orb-3000.test-plane-input.txt
bash rename-tp.sh results/match-h-result-orb-8000.test-orb-2000.test-star-input.txt
bash rename-tp.sh results/match-h-result-orb-8000.test-orb-3000.test-star-input.txt
bash rename-tp.sh results/match-h-result-asift-800.test-orb-2000.test-star-input.txt

# 汇总匹配结果
gawk -f sum-match.awk results/match-h-result-plane-asift-800.test-orb-2000.test-plane-input.txt
gawk -f sum-match.awk results/match-h-result-plane-asift-800.test-orb-3000.test-plane-input.txt
gawk -f sum-match.awk results/match-h-result-orb-8000.test-orb-2000.test-star-input.txt
gawk -f sum-match.awk results/match-h-result-orb-8000.test-orb-3000.test-star-input.txt
gawk -f sum-match.awk results/match-h-result-asift-800.test-orb-2000.test-star-input.txt
