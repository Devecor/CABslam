#
# Usage:
#
#   gawk -f make-test-star.awk test-input.txt star-input.txt test-ref-star.txt
BEGIN {
    t_count = 1;
    count = 0;
    t_total = 16;
    p_count = 0;
    p_total = 8;
    count2 = 0;
}

BEGINFILE {    
    if (FILENAME == "test-input.txt") 
        action = 1;
    else if (FILENAME == "star-input.txt")
        action = 2;
    else if (FILENAME == "star-input2.txt")
        action = 2;
    else        
        action = 0;
}

NF > 0 && ! /^#.*/ {

    if (action == 1) {
        split($1, a, ".");
        testpoints[t_count][count] = "images/tp/" a[1];
        count ++;
        if (count == t_total) {
            t_count ++;
            count = 0;
        }        
    }

    else if (action == 2) {
        refstars[p_count][count2] = $2;
        count2 ++;
        if (count2 == p_total) {
            p_count ++;
            count2 = 0;
        }
    }

    else {
        i = int($1);
        s = int(substr($2, 2)) - 1;
        for (j=0; j<t_total; j++) {
            printf("%s", testpoints[i][j])
            for (k=0; k<p_total; k++)
                printf(" %s", refstars[s][k]);
            printf("\n");
        }                    
    }
}

END {    
}
