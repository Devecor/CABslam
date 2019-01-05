# 提取关键点，保存到 feature-orb-N 目录下面

IMGPATH="${1:-images}"
OUTPREFIX="${2:-features}"
NFEATURES="${3:-8000}"
FEATURE="${4:-orb}"

if [[ "${OUTPREFIX}" == *- ]] ; then
    OUTPUT="${OUTPREFIX}${FEATURE}-${NFEATURES}"
else
    OUTPUT="${OUTPREFIX}/${FEATURE}-${NFEATURES}"
fi

QUERYCMD="python ../check_feature.py"
OPT=""

if [[ "${FEATURE}" == "asift" ]] ; then    
    OPT="${OPT} --asift"
fi

echo Query ${FEATURE} feature with --nFeature=${NFEATURES}

echo Make output dir: ${OUTPUT}
test -f ${OUTPUT} || mkdir -p ${OUTPUT}

for photo in $(find ${IMGPATH}/ -name "*.jpg") ; do
  echo Query photo: ${photo} ...
  ${QUERYCMD} --nFeatures=${NFEATURES} ${OPT} --save --output=${OUTPUT} ${photo}
done
