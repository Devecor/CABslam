# 获取 orb 关键点 8000
bash query-feature.sh images features 8000
bash query-feature.sh images features 2000


# 获取 asift 关键点: 800
# bash query-feature.sh images features 800 asift

# 匹配采集点的参考照片
bash match-feature.sh star-input.txt "matches" features/orb-8000 features/orb-8000

# 匹配测试点和采集点
gawk -f make-test-star.awk test-ref-star.txt > test-star-input.txt
bash match-feature.sh test-star-input.txt matches features/orb-2000 features/orb-8000

bash match-feature.sh test-star-input.txt matches features/orb-2000 features/orb-8000 f

# 修改一下 make-test-star.awk 在参考照片的后面都增加一个 a，使用辅助照片进行匹配
gawk -f make-test-star.awk test-ref-star.txt > test-star-input2.txt
bash match-feature.sh test-star-input2.txt matches features/orb-2000 features/orb-8000

# 汇总匹配结果
gawk -f ../test3/sum-match.awk results/match-h-result-orb-8000.orb-2000.test-star-input.txt
gawk -f ../test3/sum-match.awk results/match-h-result-orb-8000.orb-2000.test-star-input2.txt

# 生成星型采集关键点的三维坐标库
bash build-model.sh model-input.txt "models" features/orb-8000

# 查询定位
bash query-location.sh test-star-input.txt locations features/orb-2000 models

# 汇总定位结果
gawk -f ../test3/sum-location.awk results/location-h-models.orb-2000.test-star-input.txt

# 使用两张照片进行定位
C:/Python27/python ../check_3p_locate.py --train=features/orb-8000/s1-1-orb.npz --ref=features/orb-8000/s1-1a-orb.npz \
    --query=features/orb-2000/t1-1-orb.npz --focals=0.9722,0.7292 --homography --refpos="-6.8,0" \
    images/s1-1.jpg images/s1-1a.jpg images/t1-1.jpg

C:/Python27/python ../check_3p_locate.py --train=features/orb-8000/s1-4-orb.npz --ref=features/orb-8000/s1-4a-orb.npz \
    --query=features/orb-2000/t2-6-orb.npz --focals=0.9722,0.7292 --homography --refpos="-6.8,0" \
    images/s1-4.jpg images/s1-4a.jpg images/t2-6.jpg

bash query-location-2p.sh test-star-input.txt results/location-2p-results2.txt features/orb-2000 features/orb-8000

# 查看三维点坐标计算结果和查看定位结果（调试）
# cd ../
# c:/Python27/python check_point3d.py --offset=-6.8,0,0 --yaw=0 --focal=0.9722,0.7292 test5/images/s1-1.jpg test5/images/s1-1a.jpg
C:/Python27/python ../make_model.py --size=2448,3264 --focals=0.9722,0.7292 --show --homography --refpos=-6.8,0,0 features/orb-8000/s1-1-orb.npz features/orb-8000/s1-1a-orb.npz --save --output=models

# c:/Python27/python ../query_location.py --size=2448,3264 --focals=0.9722,0.7292 --save --output=locations/models.orb-2000 --homography features/orb-2000/t1-1-orb models/s1-1 models/s1-2 models/s1-3 models/s1-4 models/s1-5
c:/Python27/python ../query_location.py --size=2448,3264 --focals=0.9722,0.7292 --save --output=locations/models.orb-2000 --homography features/orb-2000/t1-1-orb models/s1-1 

# 生成特征平面
C:/Python27/python ../make_refplane.py --focals=0.9722,0.7292 --mask=1760,1460,2028,1522 --distance=512 --show --save --output=models images/s1-1.jpg
