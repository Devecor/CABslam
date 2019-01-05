#
# Usage:
#
#   gawk -f transform-location.awk results/location-2p-h-results.txt

BEGIN {
    pi = 3.1415926
}

NF > 0 && ! /^#.*/ {

    if ($2 == "NaN")
        printf("%-8s %-8s\n", $1, $2)
    else {
        split($2, a, "-")
        refindex = int(a[2])
        rot = (refindex - 1) * pi / 4;
        x = int($3)
        y = int($4)
        x1 = x * cos(rot) - y * sin(rot)
        y1 = x * sin(rot) + y * cos(rot)
        printf("%-8s %-8s %8.2f %8.2f\n", $1, $2, x1, y1)
    }
}

