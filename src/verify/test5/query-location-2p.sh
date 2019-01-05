#
# Usage:
#
#    bash query-location-2p.sh INPUT OUTPUT QPATH TPATH [orb|asift] [f|h|n]
#
#    第一个参数 输入文件，每一行开始是查询图片名称，后面是参考图片名称
#    第二个参数 是输出文件的名称，定位结果会追加到这个文件里面
#    第三个参数 存放查询照片 关键点的路径
#    第四个参数 存放参考照片 关键点的路径
#    第五个参数是匹配模式：
#          f 使用 findFundamentalMat 进行匹配
#          h 使用 findHomography 进行匹配，这也是默认值
#          n 表示简单匹配
#
#    例如
#
#      bash query-location-2p.sh test-star-input.txt results/location-2p-results.txt features/orb-2000 features/orb-8000
#
INPUT="${1:-test-star-input.txt}"
OUTPUT="${2:-results/location-2p-results.txt}"
QPATH="${3:-features/orb-2000}"
TPATH="${4:-features/orb-8000}"
HOMOGRAPHY="${5:-h}"

QUERYCMD="c:/Python27/python ../query_location_2p.py  --size=2448,3264 --focals=0.9722,0.7292 --refpos=-6.8,0"

echo "Remove output ${OUTPUT}"
[[ -f ${OUTPUT} ]] && rm ${OUTPUT}

echo "Read input images from ${INPUT}"
if ! test -f "${INPUT}" ; then
  echo "No input file ${INPUT} found"
  exit 1
fi

EXTRAOPT=
if [[ "${HOMOGRAPHY}" == "h" ]] ; then
  EXTRAOPT="${EXTRAOPT} --homography"
fi

if [[ "${HOMOGRAPHY}" == "f" ]] ; then
  EXTRAOPT="${EXTRAOPT} --fundamental"
fi

#
# T1-1 2-1 5-1
code='NF > 0 && ! /^#.*/ {
  printf("%s.jpg", $1);
  for (i = 2; i <= NF; i ++) {
     printf(":%s.jpg", $i)
  }
  printf("\n");
}'
# for pairs in $(echo "images/t2-1 images/s1-1 images/s1-2 images/s1-3 images/s1-4 images/s1-5" | gawk "${code}") ; do
for pairs in $(gawk "${code}" ${INPUT}) ; do
    ${QUERYCMD} --save --output=${OUTPUT} --train=${TPATH} --query=${QPATH} ${EXTRAOPT} ${pairs//:/ }
done
