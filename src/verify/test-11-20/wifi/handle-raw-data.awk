BEGIN {
    printf("%-04s %-32s %-04s\n", "POS.", "AP", "AVG.");
    rcount = -1;
}

BEGINFILE {

    rcount ++;
    split(FILENAME, names, "/");
    name = names[length(names)]
    r = substr(name, 1, index(name, ".txt") - 1);
    regions[rcount] = r;
    delete rdata;
    delete counter;
}

NF > 0 {
    value = $NF + 100;
    ap = $2;
    i = 3;
    while (i < NF) {
        ap = ap " " $i;
        i ++;
    }

    if ( ! ( ap in counter ) ) {
        counter[ap] = 0;
        regions[rcount, ap] = .0;
    }    
    rdata[ap] = (rdata[ap] * counter[ap] + value) / (counter[ap] + 1);
    counter[ap] ++;
}

ENDFILE {    

    for ( ap in rdata )
        printf("%-04s %-32s %-04d\n", r, ap, rdata[ap]);

}

END {
}
