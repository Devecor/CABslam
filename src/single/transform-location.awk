#
# Usage:
#
#   gawk -f transform-location.awk results/location-origin-results.txt

BEGIN {
    pi = 3.1415926
}

NF > 0 && ! /^#.*/ {

    if ($3 == "NaN" || $4 > 90.0 || $4 < -90.0 || $5 > 1000.0 || $5 < -1000.0 || $6 > 1000.0 || $6 < -1000.0)
        printf("%-8s %-8s\n", $1, "NaN")
    else {
        split($3, a, "-")
        refindex = int(a[3])
        rot = -(refindex - 1) * pi / 4;
        x = int($5)
        y = int($6)
        x1 = x * cos(rot) - y * sin(rot)
        y1 = x * sin(rot) + y * cos(rot)
        a1 = (refindex - 1) * 45 - $4
        printf("%-8s %-8s %8.2f %8.2f %8.2f\n", $1, $3, x1, y1, a1)
    }
}
