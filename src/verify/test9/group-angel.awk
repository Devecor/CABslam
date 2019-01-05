#
# Usage:
#
#   gawk -f group-angel.awk t9.txt

BEGIN {
    total_y = 0
    total_n = 0
    count = 0

    values[0] = 1.0
    values[1] = 2.0
    values[2] = 3.0
    values[3] = 6.0
    values[4] = 9.0
    values[5] = 12.0
    values[6] = 15.0

    for (i=0; i<7; i++)
      total[i] = 0

    total_errors = 0
}

NF > 0 && /^t.*/ {
    if ($11 < 0)
    {
	angel_error = -$11
    } else
    {
	angel_error = $11
    }
    count ++;
    if ($2 == "NaN")
        total_n ++;
    else {
        total_y ++;
        total_errors += angel_error

        not_found = 1
        for (i=0; i<7; i++) {
	    
            if (angel_error < values[i]) 
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
    printf("定位误差：     %.2fdeg.\n", total_errors / total_y);
    printf("\n")

    printf("%-10s ", "误差范围");
    for (i=0; i<7; i++)
        printf("%-4d ", values[i])
    printf(">%-4d NaN\n", values[i-1])

    printf("%-10s ", "照片数目");
    for (i=0; i<7; i++)
        printf("%-4d ", total[i])
    printf("%-5d %-4d\n", total[i], total_n)
}
