# 提取关键点，保存到 feature-orb-N 目录下面

NFEATURES="${1:-2000}"
FEATURE="${2:-orb}"
GRID="${3}"
QUERYCMD="C:/Python27/python ../check_feature.py"

OPT=""

if ! [[ "${GRID}" == "" ]] ; then
    CELL="g"
    OPT="${OPT} --grid"
else
    CELL=""
fi

if [[ "${FEATURE}" == "asift" ]] ; then    
    OPT="${OPT} --asift"
fi

OUTPUT="features/test-${FEATURE}-${CELL}${NFEATURES}"

echo Query test ${FEATURE} feature with --nFeature=${NFEATURES}

echo Make output dir: ${OUTPUT}
test -f ${OUTPUT} || mkdir -p ${OUTPUT}

for photo in $(find test2/ -name "*.jpg") ; do
  echo Query photo: ${photo} ...
  ${QUERYCMD} --nFeatures=${NFEATURES} ${OPT} --save --output=${OUTPUT} ${photo}
done
