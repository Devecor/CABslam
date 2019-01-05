#
# Usage:
#
#   gawk -f make-test-star.awk test-ref-star.txt
BEGIN {
    tn = 9;
    sn = 5;
}
NF > 0 && ! /^#.*/ {
    for (i=1; i<tn+1; i++) {
        printf("images/tp/%s-%d", $1, i);
        for (j=1; j<sn+1; j++)
            printf(" images/star/%s-%d", $2, j) 
        printf("\n");
    }
}
