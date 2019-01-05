#
# Usage:
#
#   gawk -f region-errors.awk results/location-n-test-errors.txt

BEGIN {

    total = 0
    total_n = 0

    total_dt = 0
    total_da = 0
   
    for (i=1; i<3; i++) {
        total_m[i] = 0
        total_m_n[i] = 0

        total_m_dt[i] = 0
        total_m_da[i] = 0
    }

    tp1ms = " t1 t2 t3 t4 t5 t6 t7 t8 t9 t10 t11 t12 t13 t14 t15 t16 t17 t18 t19 t20 t21 t22 t23 t24 t28 t29 t30 t31 t32 t33 "
    tp2ms = ""

    tpnames[1] = "走廊"
    tpnames[2] = "休息"
}

NF > 0 && ! /^#.*/  && /^t.*/ {

    total ++

    split($1, a, "-")
    tp = " " a[1] " "

    st = index(tp1ms, tp) > 0 ? 1 : 2;
    total_m[st] ++

    if ($2 == "NaN") {
        total_n ++        
        total_m_n[st] ++
    }
    else {
        da = $11 < 0 ? -$11 : $11
        total_dt += $8
        total_da += da
        
        total_m_dt[st] += $8
        total_m_da[st] += da
    }
}

END {

    tn = total - total_n
    print "* 总有效测试照片: " total
    print "* 定位成功数目： "  tn
    print "* 定位失败数目： "  total_n
    printf("* 定位成功率：%8.2f%%\n", tn / total * 100)
    printf("* 平均位置误差： %8.2fcm\n", total_dt / tn)
    printf("* 平均角度误差： %8.2fdeg.\n", total_da / tn)

    
    printf("%4s %4s %4s %4s %8s %8s %8s\n", "Reg.", "To.", "OK.", "Fail", "Ratio", "Error(cm)", "Deg.")
    print "-----------------------------------"
    for (i=1; i<length(total_m)+1; i++) {
        tn = total_m[i] - total_m_n[i]
        printf("%-4s %-4d %-4d %-4d %6.2f%% %8.2f %8.2f\n", tpnames[i], total_m[i], tn, total_m_n[i], tn / total_m[i] * 100, total_m_dt[i] / tn, total_m_da[i] / tn);
    }
}
