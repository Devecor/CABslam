#
# Usage:
#
#   gawk -f make-test-plane.awk test-input.txt plane-input.txt test-ref-plane.txt
BEGIN {
    t_count = 1;
    count = 0;
    p_count = 0;
    t_total = 16;
}

BEGINFILE {    
    if (FILENAME == "test-input.txt") 
        action = 1;
    else if (FILENAME == "plane-input.txt")
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
        refplanes[p_count] = $1;
        p_count ++;
    }

    else {
        i = int($1);
        for (j=0; j<t_total; j++) {
            printf("%s", testpoints[i][j])
            for (k=2; k<NF; k++)
                printf(" %s", refplanes[int(substr($k, 2))-1]);
            printf("\n");
        }                    
    }
}

