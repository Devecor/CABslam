#
# Usage:
#
#    bash match-feature.sh INPUT OUTPUT QPATH TPATH [orb|asift] [f|h|n]
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
#      bash match-feature.sh plane-input.txt matches features/plane-asift-800 features/plane-asift-800
#      bash match-feature.sh test-star-input.txt "matches/test-" features/test-orb-g200 features/plane-asift-800
#
INPUT="${1:-star-input.txt}"
OUTPREFIX="${2:-matches}"
QPATH="${3:-features/test-orb-2000}"
TPATH="${4:-features/orb-8000}"
HOMOGRAPHY="${5:-h}"

MNAME="$(basename $TPATH).$(basename $QPATH)"
if [[ "${OUTPREFIX}" == *- ]] ; then
    OUTPUT="${OUTPREFIX}${MNAME}"
else
    OUTPUT="${OUTPREFIX}/${MNAME}"
fi

MATCHCMD="python ../check_match.py"

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

if [[ "${QPATH}" == *asift-* ]] ; then
    ASIFT1="asift."
else
    ASIFT1=""
fi

if [[ "${TPATH}" == *asift-* ]] ; then
    ASIFT2="asift."
else
    ASIFT2=""
fi

function match()
{
    img1=$1.jpg
    img2=$2.jpg
    name1=${QPATH}/$(basename $1)-${ASIFT1}orb.npz
    name2=${TPATH}/$(basename $2)-${ASIFT2}orb.npz
    echo Match: $img1 $img2
    ${MATCHCMD} --save --output=${OUTPUT} --kpfile1=${name1} --kpfile2=${name2} ${EXTRAOPT} $img1 $img2
}

# 
# 1-1 2-1 5-1
code='NF > 0 && ! /^#.*/ {
  for (x = 2; x <= NF; x ++) {
     printf("%s:%s\n", $1, $x);
  }
}'

# for pairs in $(echo "t5-2 6-1 6-2 6-3 2-3 3-3 5-3 7-3" | gawk "${code}") ; do
for pairs in $(gawk "${code}" ${INPUT}) ; do
    match ${pairs/:/ }
done

result="results/match-${HOMOGRAPHY}-result-${MNAME}.${INPUT}"
echo Write result: $result
echo "IMG-1  IMG-2  unique     inlier     outlier" > $result
cat $(find ${OUTPUT} -name "*.match.txt") | sed "s/\.jpg//gi" >> $result
