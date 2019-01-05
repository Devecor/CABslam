#
# Usage:
#
#   gawk -f group-location.awk results/location-errors.txt

BEGIN {
    total_y = 0
    total_n = 0
    count = 0

    values[0] = 20.0
    values[1] = 40.0
    values[2] = 60.0
    values[3] = 80.0
    values[4] = 100.0

    for (i=0; i<5; i++)
      total[i] = 0

    total_errors = 0
}

NF > 0 && /^t.*/ {
    count ++;
	print count
    if ($2 == "NaN")
        total_n ++;
    else {
        total_y ++;
        total_errors += $8

        not_found = 1
        for (i=0; i<5; i++) {
            if ($8 < values[i]) 
            {
                total[i] ++
                not_found = 0
            }
        }
        if (not_found)
            total[i] ++;
    }
}

END {
    printf("总查询照片：   %d\n", count)
    printf("定位成功：     %d\n", total_y);
    printf("定位失败：     %d\n", total_n);
    printf("定位成功率：   %.2f%%\n", total_y / count * 100);
    printf("定位误差：     %.2fcm\n", total_errors / total_y);
    printf("\n")

    printf("%-10s ", "误差范围");
    for (i=0; i<5; i++)
        printf("%-4d ", values[i])
    printf(">%-4d NaN\n", values[i-1])

    printf("%-10s ", "照片数目");
    for (i=0; i<5; i++)
        printf("%-4d ", total[i])
    printf("%-5d %-4d\n", total[i], total_n)
}
