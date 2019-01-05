#
# Usage:
#
#    bash match-feature.sh PATH [orb|asift] [f|h|n]
#
#    第一个参数 存放关键点的路径
#    第二个参数是获取关键点使用的方法 orb 或者 asift
#    第三个参数是匹配模式：
#          f 使用 findFundamentalMat 进行匹配，这也是默认值
#          h 使用 findHomography 进行匹配
#          n 表示简单匹配
#
#    例如
#
#      match-feature.sh features/orb-8000 orb
#      match-feature.sh features/asift-800 asift
#

FPATH="${1:-features/orb-8000}"
FEATURE="${2:-orb}"
HOMOGRAPHY="${3:-f}"

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

MATCHCMD="C:/Python27/python ../check_match.py"
OUTPUT="matches/$(basename ${FPATH})"
INPUT="match-input.txt"

echo "Make output path: ${OUTPUT}"
test -f "${OUTPUT}" || mkdir -p ${OUTPUT}

echo "Read input images from ${INPUT}"
if ! test -f "${INPUT}" ; then
  echo "No input file ${INPUT}"
  exit 1
fi

function match()
{
    prefix=data2/c
    img1=${prefix}$1.JPG
    img2=${prefix}$2.JPG
    name1="${FPATH}/$(basename $1)-${ASIFT}orb.npz"
    name2="${FPATH}/$(basename $2)-${ASIFT}orb.npz"
    echo Match: $img1 $img2
    # ${MATCHCMD} --save --output=${OUTPUT} --path=${FPATH} --suffix="${FEATURE},${FEATURE}" ${EXTRAOPT} $img1 $img2
    ${MATCHCMD} --save --output=${OUTPUT} --kpfile1=${name1} --kpfile2=${name2} ${EXTRAOPT} $img1 $img2
}

# 
# 1-1 2-1 5-1
code='NF > 0 {  
  for (x = 2; x <= NF; x ++) {
     split($1, a, "-");
     split($x, b, "-");
     printf("%s/%s:%s/%s\n", a[1], $1, b[1], $x);
  }
}'

#
# 1 5 2 
code='NF > 0 {  
  for (x = 2; x <= NF; x ++) {
    for (i = 1; i < 5; i ++)
     printf("%s/%s-%s:%s/%s-%s\n", $1, $1, i, $x, $x, i);
  }
}'
for pairs in $(gawk "${code}" ${INPUT}) ; do
    match ${pairs/:/ }
done

result="results/match-${HOMOGRAPHY}-result-$(basename ${FPATH}).txt"
echo Write result: $result
echo "IMG-1  IMG-2  unique     inlier     outlier" > $result
cat $(find ${OUTPUT} -name "*.match.txt") | sed "s/\.JPG//gi" >> $result
