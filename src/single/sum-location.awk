#
# Usage:
#
#   gawk -f sum-location.awk results/location-h-models.test-orb-2000.test-star-input.txt

BEGIN {
    total_y = 0
    total_n = 0
    total_time = 0
    count = 0
}

NF > 0 && ! /^#.*/ {
    count ++;
    if ($3 == "NaN" || $4 > 60.0 || $4 < -60.0)
        total_n ++;
    else
        total_y ++;
    total_time += $2;
}

END {
    printf("总查询照片：   %d\n", count)
    printf("定位成功：     %d\n", total_y);
    printf("定位失败：     %d\n", total_n);
    printf("定位成功率：   %.2f%%\n", total_y / count * 100);
    printf("定位平均时间： %.2fms\n", total_time / count);
}
