#
# 使用两张参考照片的方式，计算测试点的位置
#
FPATH="${1:-features/orb-8000}"
TPATH="${2:-features/test-orb-2000}"
FEATURE="${3:-orb}"
HOMOGRAPHY="${4:-h}"

MNAME="$(basename $TPATH).$(basename $FPATH)"

QUERYCMD="C:/Python27/python ../check_3p_locate.py"
OUTPUT="locations/${MNAME}"
FOCALS="1.167,0.875"

EXTRAOPT="--focals=${FOCALS}"
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

echo "Make output path: ${OUTPUT}"
test -f "${OUTPUT}" || mkdir -p ${OUTPUT}

# 查询照片，参考照片，辅助照片，辅助照片(x,y), 期望结果坐标(x,y)
#
# 参考坐标系：
#
#    以参考照片为原点，向前为 Y 轴，向右为 X 轴的坐标系来计算
#
INPUT="testpoints.txt"

echo Locate test points by 2 photoes

function locate()
{
    prefix1=test2/
    prefix2=data2/c
    img1=${prefix1}$1.jpg
    img2=${prefix2}$2.JPG
    img3=${prefix2}$2.JPG
    name1=${TPATH}/$(basename $1)-orb.npz
    name2=${FPATH}/$(basename $2)-${ASIFT}orb.npz
    echo Match: $img1 $img2
    ${MATCHCMD} --save --output=${OUTPUT} --kpfile1=${name1} --kpfile2=${name2} ${EXTRAOPT} $img1 $img2
    ${QUERYCMD} --save --output ${OUTPUT} \
        --train=${FPATH}/${train}-${ASIFT}orb.npz \
        --ref=${FPATH}/${refimg}-${ASIFT}orb.npz \
        --query=${TPATH}/${qryimg}-orb.npz \
        --refpos=" ${pos}" \
        --expected=" ${expected}" \
        test-11-20/data2/c2/2-3.jpg test-11-20/data2/c3/3-3.jpg test-11-20/data2/c6/6-3.jpg
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

for line in $(gawk "${code}" ${INPUT}) ; do
    locate ${line/:/ }
done

