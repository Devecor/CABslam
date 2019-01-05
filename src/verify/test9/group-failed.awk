#
# Usage:
#
#   gawk -f group-errors.awk results/location-n-test.10.1-test-orb-2000.test-star-input.txt

BEGIN {

    total_a = 0
    total_b = 0
    total_c = 0
    total_c1 = 0
    total_c2 = 0

    threshold_angle = 60
    threshold_distance = 1000
}

function abs(x) {
    return x < 0 ? -x : x
}

NF > 0 && ! /^#.*/  && /^t.*/ {

    if ($3 == "NaN") {
        total_a ++
    }
    else if (abs($4) > threshold_angle) {
        total_b ++
        print "B: " $0
    }
    else if (abs($5) >  threshold_distance || abs($6) > threshold_distance) {
        total_c ++
        print "C: " $0
    }
}

END {

    print "-------------------------------------------------"
    printf("%-4s %-4s %-4s %-6s\n", "A", "B", "C", "Total.")
    printf("%-4d %-4d %-4d %-6d\n", total_a, total_b, total_c, total_a + total_b + total_c)
    print "-------------------------------------------------"

}
