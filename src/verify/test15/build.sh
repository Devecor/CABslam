# 获取 orb 关键点 8000/asift 800
bash query-feature.sh images/star features 800 asift
bash query-feature.sh images/star features 8000
bash query-feature.sh images/tp "features/test-" 1000
bash query-feature.sh images/tp "features/test-" 2000
bash query-feature.sh images/tp "features/test-" 3000
bash query-feature.sh images/tp "features/test-" 1000
bash query-feature.sh images/tp "features/test-" 2000
bash query-feature.sh images/tp "features/test-" 3000

# 匹配测试点和采集点
bash match-feature.sh test-star-input-1m.txt "matches/orb-8000-orb-1000-1m" features/test-orb-1000 features/orb-8000
bash match-feature.sh test-star-input-1m.txt "matches/orb-8000-orb-1000-2m" features/test-orb-1000 features/orb-8000
bash match-feature.sh test-star-input-1m.txt "matches/orb-8000-orb-1000-3m" features/test-orb-1000 features/orb-8000

bash match-feature.sh test-star-input-1m.txt "matches/orb-8000-orb-1000-1m" features/test-orb-2000 features/orb-8000
bash match-feature.sh test-star-input-1m.txt "matches/orb-8000-orb-1000-2m" features/test-orb-2000 features/orb-8000
bash match-feature.sh test-star-input-1m.txt "matches/orb-8000-orb-1000-3m" features/test-orb-2000 features/orb-8000

bash match-feature.sh test-star-input-1m.txt "matches/orb-8000-orb-1000-1m" features/test-orb-3000 features/orb-8000
bash match-feature.sh test-star-input-1m.txt "matches/orb-8000-orb-1000-2m" features/test-orb-3000 features/orb-8000
bash match-feature.sh test-star-input-1m.txt "matches/orb-8000-orb-1000-3m" features/test-orb-3000 features/orb-8000


bash match-feature.sh test-star-input-1m.txt "matches/asif-800-orb-1000-1m" features/test-orb-1000 features/asift-800
bash match-feature.sh test-star-input-2m.txt "matches/asif-800-orb-1000-2m" features/test-orb-1000 features/asift-800
bash match-feature.sh test-star-input-3m.txt "matches/asif-800-orb-1000-3m" features/test-orb-1000 features/asift-800

bash match-feature.sh test-star-input-1m.txt "matches/asif-800-orb-2000-1m" features/test-orb-2000 features/asift-800
bash match-feature.sh test-star-input-2m.txt "matches/asif-800-orb-2000-2m" features/test-orb-2000 features/asift-800
bash match-feature.sh test-star-input-3m.txt "matches/asif-800-orb-2000-3m" features/test-orb-2000 features/asift-800

bash match-feature.sh test-star-input-1m.txt "matches/asif-800-orb-3000-1m" features/test-orb-3000 features/asift-800
bash match-feature.sh test-star-input-2m.txt "matches/asif-800-orb-3000-2m" features/test-orb-3000 features/asift-800
bash match-feature.sh test-star-input-3m.txt "matches/asif-800-orb-3000-3m" features/test-orb-3000 features/asift-800

# 汇总匹配结果
gawk -f sum-match.awk results/match-h-result-orb-8000.test-orb-1000.test-star-input-1m.txt
gawk -f sum-match.awk results/match-h-result-orb-8000.test-orb-1000.test-star-input-2m.txt
gawk -f sum-match.awk results/match-h-result-orb-8000.test-orb-1000.test-star-input-3m.txt

gawk -f sum-match.awk results/match-h-result-orb-8000.test-orb-2000.test-star-input-1m.txt
gawk -f sum-match.awk results/match-h-result-orb-8000.test-orb-2000.test-star-input-2m.txt
gawk -f sum-match.awk results/match-h-result-orb-8000.test-orb-2000.test-star-input-3m.txt

gawk -f sum-match.awk results/match-h-result-orb-8000.test-orb-3000.test-star-input-1m.txt
gawk -f sum-match.awk results/match-h-result-orb-8000.test-orb-3000.test-star-input-2m.txt
gawk -f sum-match.awk results/match-h-result-orb-8000.test-orb-3000.test-star-input-3m.txt

gawk -f sum-match.awk results/match-h-result-asift-800.test-orb-1000.test-star-input-1m.txt
gawk -f sum-match.awk results/match-h-result-asift-800.test-orb-1000.test-star-input-2m.txt
gawk -f sum-match.awk results/match-h-result-asift-800.test-orb-1000.test-star-input-3m.txt

gawk -f sum-match.awk results/match-h-result-asift-800.test-orb-2000.test-star-input-1m.txt
gawk -f sum-match.awk results/match-h-result-asift-800.test-orb-2000.test-star-input-2m.txt
gawk -f sum-match.awk results/match-h-result-asift-800.test-orb-2000.test-star-input-3m.txt

gawk -f sum-match.awk results/match-h-result-asift-800.test-orb-3000.test-star-input-1m.txt
gawk -f sum-match.awk results/match-h-result-asift-800.test-orb-3000.test-star-input-2m.txt
gawk -f sum-match.awk results/match-h-result-asift-800.test-orb-3000.test-star-input-3m.txt
