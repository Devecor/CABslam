#
# Usage:
#
#    bash match-feature.sh TPATH FPATH [orb|asift] [f|h|n]
#
#    第一个参数 存放查询照片 关键点的路径
#    第二 个参数 存放参考照片 关键点的路径
#    第三个参数是参考照片获取关键点使用的方法, orb 或者 asift
#    第四个参数是匹配模式：
#          f 使用 findFundamentalMat 进行匹配
#          h 使用 findHomography 进行匹配，这也是默认值
#          n 表示简单匹配
#
#    例如
#
#      test-match-feature.sh features/test-orb-2000 features/orb-8000
#      test-match-feature.sh features/test-orb-g200 features/orb-8000 asift
#
TPATH="${1:-features/test-orb-2000}"
FPATH="${2:-features/orb-8000}"
FEATURE="${3:-orb}"
HOMOGRAPHY="${4:-h}"

MNAME="$(basename $TPATH).$(basename $FPATH)"

MATCHCMD="C:/Python27/python ../check_match.py"

# INPUT="test-match-input.txt"
# OUTPUT="matches/${MNAME}"
# prefix1=test2/
# prefix2=data2/c
# oprefix=test-match
INPUT="test-match-input2.txt"
OUTPUT="matches/11-28/${MNAME}"
prefix1=test2/
prefix2=data3/
oprefix=test-match2

echo "Make output path: ${OUTPUT}"
test -f "${OUTPUT}" || mkdir -p ${OUTPUT}

echo "Read input images from ${INPUT}"
if ! test -f "${INPUT}" ; then
  echo "No input file ${INPUT}"
  exit 1
fi

EXTRAOPT=
if [[ "${HOMOGRAPHY}" == "h" ]] ; then
  EXTRAOPT="${EXTRAOPT} --homography"
fi

if [[ "${HOMOGRAPHY}" == "f" ]] ; then
  EXTRAOPT="${EXTRAOPT} --fundamental"
fi

if [[ "${FEATURE}" == "asift" ]] ; then
    ASIFT="asift."
else
    ASIFT=""
fi

function match()
{
    img1=${prefix1}$1.jpg
    img2=${prefix2}$2.JPG
    name1=${TPATH}/$(basename $1)-orb.npz
    name2=${FPATH}/$(basename $2)-${ASIFT}orb.npz
    echo Match: $img1 $img2
    ${MATCHCMD} --save --output=${OUTPUT} --kpfile1=${name1} --kpfile2=${name2} ${EXTRAOPT} $img1 $img2
}

# 
# 1-1 2-1 5-1
code='NF > 0 && ! /^#.*/ {
  for (x = 2; x <= NF; x ++) {
     split($1, a, "-");
     split($x, b, "-");
     printf("%s/%s:%s/%s\n", a[1], $1, b[1], $x);
  }
}'

# for pairs in $(echo "t5-2 6-1 6-2 6-3 2-3 3-3 5-3 7-3" | gawk "${code}") ; do
for pairs in $(gawk "${code}" ${INPUT}) ; do
    match ${pairs/:/ }
done

result="results/${oprefix}-${HOMOGRAPHY}-result-${MNAME}.txt"
echo Write result: $result
echo "IMG-1  IMG-2  unique     inlier     outlier" > $result
cat $(find ${OUTPUT} -name "*.match.txt") | sed "s/\.JPG//gi" >> $result
