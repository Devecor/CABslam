#
# Usage:
#
#   gawk -f location-errors.awk results/location-results.txt

BEGIN {
    pi = 3.1415926

    expected["t1"][0] = -60
    expected["t1"][1] = 0

    expected["t2"][0] = 120
    expected["t2"][1] = 0

    expected["t3"][0] = -120
    expected["t3"][1] = 0

    expected["t4"][0] = 60
    expected["t4"][1] = 0

    expected["t5"][0] = -60
    expected["t5"][1] = 60

    expected["t6"][0] = -120
    expected["t6"][1] = 0

    expected["t7"][0] = -60
    expected["t7"][1] = -60

    expected["t8"][0] = 60
    expected["t8"][1] = 0

    expected["t9"][0] = 0
    expected["t9"][1] = 120

    expected["t10"][0] = 60
    expected["t10"][1] = -60

    expected["t11"][0] = 0
    expected["t11"][1] = -60

    expected["t12"][0] = 0
    expected["t12"][1] = 120

    expected["t13"][0] = 60
    expected["t13"][1] = 0

    expected["t14"][0] = 0
    expected["t14"][1] = -60

    expected["t15"][0] = 0
    expected["t15"][1] = 120

    expected["t16"][0] = 60
    expected["t16"][1] = 60

    expected["t17"][0] = 60
    expected["t17"][1] = 0

    expected["t18"][0] = 0
    expected["t18"][1] = -60

    expected["t19"][0] = 60
    expected["t19"][1] = 60

    expected["t20"][0] = 60
    expected["t20"][1] = -60

    expected["t21"][0] = -60
    expected["t21"][1] = -60

    expected["t22"][0] = -60
    expected["t22"][1] = 60

    expected["t23"][0] = 60
    expected["t23"][1] = -60

    expected["t24"][0] = -60
    expected["t24"][1] = 0

    expected["t25"][0] = 0
    expected["t25"][1] = 60

    expected["t26"][0] = 60
    expected["t26"][1] = -60

    expected["t27"][0] = 60
    expected["t27"][1] = 0

    expected["t28"][0] = 120
    expected["t28"][1] = 0

    expected["t29"][0] = 60
    expected["t29"][1] = 0

    expected["t30"][0] = -60
    expected["t30"][1] = 60

    expected["t31"][0] = 60
    expected["t31"][1] = 60

    expected["t32"][0] = 60
    expected["t32"][1] = 0

    printf("%-6s %-8s %-8s %-8s %-8s %-8s %-8s %-s\n",
           "TP", "x", "y", "X", "Y", "dx", "dy", "Error.")

    total = 0
    no_locate = 0
    total_error = 0
}

NF > 0 && ! /^#.*/ {

    total ++
    if ($2 == "NaN") {
        printf("%-4s %-8s\n", $1, $2)
        no_locate ++
    }
    else {
        split($1, a, "-")
        tp = a[1]
   
        dx = expected[tp][0] - $3
        dy = expected[tp][1] - $4

        dt = sqrt(dx * dx + dy * dy)
        total_error += dt

        printf("%-6s %-8.2f %-8.2f %-8.2f %-8.2f %-8.2f %-8.2f %-8.2f\n",
               $1, $3, $4, expected[tp][0], expected[tp][1], dx, dy, dt)

    }
}

END {

    n = total - no_locate
    print "* 总有效测试照片: " total
    print "* 定位成功数目： "  n
    print "* 定位失败数目： "  no_locate
    printf("* 定位成功率：%8.2f%%\n", n / total * 100)
    printf("* 平均误差： %8.2fcm\n", total_error / n)

}
