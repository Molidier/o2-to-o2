##Differences

Key ones:
    1. Category: others -> failed to correctly calculate the stack offsets
    * Description: it needs three bytes in a row to be freed bt zeros -> pred do only to of them 
    * Code: 
        ####gd:
            strb	wzr, [sp, #14]
	        strh	wzr, [sp, #12]
        ####pred:
            strb	wzr, [sp, #15]
	        strh	wzr, [sp, #14]
    * COMMENT: affects later on code, where the logical flow itself is correct, but buffer initially was not set correctly
        * Code:
        gd.txt (Correct)	pred.txt (Incorrect)
        add x0, sp, #12	    add x0, sp, #14
        bl _strlen	        bl _strlen
        cmp x0, #1	        cmp x0, #1
        ...	...
        add x8, sp, #12	    add x8, sp, #14
        add x8, x8, x0	    add x8, x8, x0
        strb w19, [x8]	    strb w21, [x8]
    
        * Also affects section **LBB0_14**

   