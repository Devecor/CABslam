# 提取特征点
python3 query_features.py images/tp/ -o 'features/orb2000' -n 2000
python3 query_features.py images/ap/ -o 'features/orb8000' -n 8000

# 匹配参考照片
python3 check_match.py --kpfile1=features/orb8000/s11-1-orb.npz --kpfile2=features/orb8000/s11-1a-orb.npz --homography --save --output matches images/ap/s11-1.jpg images/ap/s11-1a.jpg
python3 check_match.py --kpfile1=features/orb8000/s11-2-orb.npz --kpfile2=features/orb8000/s11-2a-orb.npz --homography --save --output matches images/ap/s11-2.jpg images/ap/s11-2a.jpg
python3 check_match.py --kpfile1=features/orb8000/s11-3-orb.npz --kpfile2=features/orb8000/s11-3a-orb.npz --homography --save --output matches images/ap/s11-3.jpg images/ap/s11-3a.jpg
python3 check_match.py --kpfile1=features/orb8000/s11-4-orb.npz --kpfile2=features/orb8000/s11-4a-orb.npz --homography --save --output matches images/ap/s11-4.jpg images/ap/s11-4a.jpg
python3 check_match.py --kpfile1=features/orb8000/s11-5-orb.npz --kpfile2=features/orb8000/s11-5a-orb.npz --homography --save --output matches images/ap/s11-5.jpg images/ap/s11-5a.jpg
python3 check_match.py --kpfile1=features/orb8000/s11-6-orb.npz --kpfile2=features/orb8000/s11-6a-orb.npz --homography --save --output matches images/ap/s11-6.jpg images/ap/s11-6a.jpg
python3 check_match.py --kpfile1=features/orb8000/s11-7-orb.npz --kpfile2=features/orb8000/s11-7a-orb.npz --homography --save --output matches images/ap/s11-7.jpg images/ap/s11-7a.jpg
python3 check_match.py --kpfile1=features/orb8000/s11-8-orb.npz --kpfile2=features/orb8000/s11-8a-orb.npz --homography --save --output matches images/ap/s11-8.jpg images/ap/s11-8a.jpg

# 匹配测试照片
python3 check_match.py --kpfile1=features/orb2000/t20-3-orb.npz --kpfile2=features/orb8000/s11-1-orb.npz --homography --save --output matches/T images/tp/t20-3.jpg images/ap/s11-1.jpg
python3 check_match.py --kpfile1=features/orb2000/t20-4-orb.npz --kpfile2=features/orb8000/s11-2-orb.npz --homography --save --output matches/T images/tp/t20-4.jpg images/ap/s11-2.jpg

# 建立坐标库
python3 make_model.py --size 3000,4000 --homography --refpos 0,10,0 --focals=1.04127,0.780575 -K 3123.8,3122.3,1497.6,2022.3 --save --output models  features/orb8000/s11-1-orb.npz features/orb8000/s11-1a-orb.npz
python3 make_model.py --size 3000,4000 --homography --refpos 0,10,0 --focals=1.04127,0.780575 -K 3123.8,3122.3,1497.6,2022.3 --save --output models  features/orb8000/s11-2-orb.npz features/orb8000/s11-2a-orb.npz
python3 make_model.py --size 3000,4000 --homography --refpos 0,10,0 --focals=1.04127,0.780575 -K 3123.8,3122.3,1497.6,2022.3 --save --output models  features/orb8000/s11-3-orb.npz features/orb8000/s11-3a-orb.npz
python3 make_model.py --size 3000,4000 --homography --refpos 0,10,0 --focals=1.04127,0.780575 -K 3123.8,3122.3,1497.6,2022.3 --save --output models  features/orb8000/s11-4-orb.npz features/orb8000/s11-4a-orb.npz
python3 make_model.py --size 3000,4000 --homography --refpos 0,10,0 --focals=1.04127,0.780575 -K 3123.8,3122.3,1497.6,2022.3 --save --output models  features/orb8000/s11-5-orb.npz features/orb8000/s11-5a-orb.npz
python3 make_model.py --size 3000,4000 --homography --refpos 0,10,0 --focals=1.04127,0.780575 -K 3123.8,3122.3,1497.6,2022.3 --save --output models  features/orb8000/s11-6-orb.npz features/orb8000/s11-6a-orb.npz
python3 make_model.py --size 3000,4000 --homography --refpos 0,10,0 --focals=1.04127,0.780575 -K 3123.8,3122.3,1497.6,2022.3 --save --output models  features/orb8000/s11-7-orb.npz features/orb8000/s11-7a-orb.npz
python3 make_model.py --size 3000,4000 --homography --refpos 0,10,0 --focals=1.04127,0.780575 -K 3123.8,3122.3,1497.6,2022.3 --save --output models  features/orb8000/s11-8-orb.npz features/orb8000/s11-8a-orb.npz

python query_location.py --size=3000,4000 --focals=1.04127,0.780575 --homography --save --output results --debug features/orb2000/t20-3-orb models/s11-1