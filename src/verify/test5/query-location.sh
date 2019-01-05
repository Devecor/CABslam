#
# Usage:
#
#    bash query-location.sh INPUT OUTPUT QPATH TPATH [orb|asift] [f|h|n]
#
#    第一个参数 输入文件，每一行包含需要匹配的两个文件
#    第二个参数 是输出路径的前缀，如果以 "-" 结束则表示同一输出路径下面的不同输出
#    第三个参数 存放查询照片 关键点的路径
#    第四个参数 存放参考照片 关键点的路径
#    第五个参数是匹配模式：
#          f 使用 findFundamentalMat 进行匹配
#          h 使用 findHomography 进行匹配，这也是默认值
#          n 表示简单匹配
#
#    例如
#
#      bash query-location.sh test-star-input.txt locations features/orb-2000 models
#
INPUT="${1:-test-star-input.txt}"
OUTPREFIX="${2:-locations}"
QPATH="${3:-features/orb-2000}"
TPATH="${4:-models}"
HOMOGRAPHY="${5:-h}"

MNAME="$(basename $TPATH).$(basename $QPATH)"
if [[ "${OUTPREFIX}" == *- ]] ; then
    OUTPUT="${OUTPREFIX}${MNAME}"
else
    OUTPUT="${OUTPREFIX}/${MNAME}"
fi

QUERYCMD="c:/Python27/python ../query_location.py  --size=2448,3264 --focals=0.9722,0.7292"

echo "Make output path: ${OUTPUT}"
test -f "${OUTPUT}" || mkdir -p ${OUTPUT}

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
  split($1, a, "/");
  printf("QPATH/%s-orb", a[length(a)]);
  for (x = 2; x <= NF; x ++) {
     split($x, a, "/");
     printf(":TPATH/%s", a[length(a)]);
  }
  printf("\n");
}'
code=${code/QPATH/${QPATH}}
code=${code/TPATH/${TPATH}}
# for pairs in $(echo "images/t1-1 images/s1-1 images/s1-2 images/s1-3 images/s1-4 images/s1-5" | gawk "${code}") ; do
for pairs in $(gawk "${code}" ${INPUT}) ; do
    ${QUERYCMD} --save --output=${OUTPUT} ${EXTRAOPT} ${pairs//:/ }
done

result="results/location-${HOMOGRAPHY}-${MNAME}.$(basename ${INPUT})"
echo Write result: $result
echo "TP       Time(ms) REF.   Angle    X       Y" > $result
cat $(find ${OUTPUT} -name "*-pose.txt") | sed "s/\.jpg//gi" >> $result
