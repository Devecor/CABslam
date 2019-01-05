#
# Usage:
#
#    bash build-model.sh INPUT OUTPUT FPATH [f|h|n]
#
#    第一个参数 输入文件，每一行包含需要匹配的两个文件
#    第二个参数 是输出路径
#    第三个参数 存放关键点的路径
#    第四个参数是匹配模式：
#          f 使用 findFundamentalMat 进行匹配
#          h 使用 findHomography 进行匹配，这也是默认值
#          n 表示简单匹配
#
#    例如
#
#        bash build-model.sh star-input.txt "models" features/orb-8000
#
INPUT="${1:-model-input.txt}"
OUTPUT="${2:-models}"
FPATH="${3:-features/orb-8000}"
HOMOGRAPHY="${4:-h}"

BUILDCMD="D:/Python27/python ../make_model.py --size=3120,4208 --focals=0.9722,0.7292"

echo "Make output path: ${OUTPUT}"
test -f "${OUTPUT}" || mkdir -p ${OUTPUT}

echo "Read input images from ${INPUT}"
if ! test -f "${INPUT}" ; then
  echo "No input file ${INPUT} found"
  exit 1
fi

EXTRAOPT=""
if [[ "${HOMOGRAPHY}" == "h" ]] ; then
  EXTRAOPT="${EXTRAOPT} --homography"
fi

if [[ "${HOMOGRAPHY}" == "f" ]] ; then
  EXTRAOPT="${EXTRAOPT} --fundamental"
fi

if [[ "${FPATH}" == *asift-* ]] ; then
    ASIFT="asift."
else
    ASIFT=""
fi

function build_model()
{
    name1=${FPATH}/$(basename $1)-${ASIFT}orb.npz
    name2=${FPATH}/$(basename $2)-${ASIFT}orb.npz
    echo Build model $(basename $1) by $(basename $2)
    ${BUILDCMD} --save --output="${OUTPUT}" ${EXTRAOPT} --refpos="$3" $name1 $name2
}

#
# 1-1 2-1 5-1
code='NF > 0 && ! /^#.*/ {
  printf("%s:%s:%s\n", $1, $2, $3);
}'

# for pairs in $(echo "t5-2 6-1 6-2 6-3 2-3 3-3 5-3 7-3" | gawk "${code}") ; do
for pairs in $(gawk "${code}" ${INPUT}) ; do
    build_model ${pairs//:/ }
done

result="results/model-${HOMOGRAPHY}-${INPUT}"
echo Write result: $result
echo "IMG              REFIMG           COUNT" > $result
cat $(find ${OUTPUT} -name "model-*.txt") | sed "s/\.jpg//gi" >> $result
find ${OUTPUT} -name "model-*.txt" -delete
