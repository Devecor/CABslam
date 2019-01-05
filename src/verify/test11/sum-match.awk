#
# Usage:
#
#   gawk -f sum-match.awk results/match-h-result-orb-8000.test-orb-2000.test-star-input.txt

function summary() {
    printf("%-10s %s\n", tp, count);
    if (count > threshold)
        total_m += 1;
    else {
        total_um += 1;
        if (count == 6 )
            total6 += 1;
        else if (count == 7)
            total7 += 1;
        else if (count == 8)
            total8 += 1;
    }
}

BEGIN {
    total6 = 0
    total7 = 0
    total8 = 0
    total_m = 0

    total_um = 0
    threshold = 9    

    tp = ""
    count = 0
}

NF > 0 && /^s.*/ {
    if (tp == $1) {
        n = int($3);
        if (n > count)
            count = n;
    }
    else {
        if (tp != "") {
            summary();
        }

        tp = $1;
        count = int($3);
    }
}

END {
    if (tp != "") {
        summary();
    }
    printf("\n总照片数目： %d\n", total_m + total_um)
    printf("匹配数目： %d\n", total_m);
    printf("未匹配数目(<%d)： %d\n", threshold, total_um);
    printf("其中\n");
    printf("匹配数目(=8)： %d\n", total8);
    printf("匹配数目(=7)： %d\n", total7);
    printf("匹配数目(=6)： %d\n", total6);
    printf("匹配数目(5-)： %d\n", total_um - total6 - total7 - total8);
}
