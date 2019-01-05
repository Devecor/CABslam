#
# Usage:
#
#   gawk -f rename-tp.awk test-input.txt
BEGIN {
    t_count = 1;
    count = 0;
    t_total = 16;
}

NF > 0 && ! /^#.*/ {

    split($1, a, ".");
    testpoints[t_count][count] = a[1];
    count ++;
    if (count == t_total) {
        t_count ++;
        count = 0;
    }
}

END {
    printf("sed -i \\\n");
    for (i=1; i<t_count; i++)
        for (j=0; j<t_total; j++)
            printf(" -e \"s/%s/t%d-%d/g\" \\\n", testpoints[i][j], i, j+1);
    printf(" $*\n");
}
