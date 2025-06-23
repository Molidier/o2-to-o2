##Differences

Key ones:
    * label_1: 'numbering of the functions are different"
        [gd]:   LBB0_5 and LBB0_6
        [pred]: LBB06 and LBB0_7

    * label_2: 'ordering is different for loop setup' -> logically the same -> does not affect the program itself -> [%bb.3:]
    
    * label_3: 'additional ; %bb.5 is added in pred" -> ruins all the logical flow
        [pred]: -> returns maximum values itself -> return out=max
            ; %bb.5:
            mov	x0, x8
            b	LBB0_7
        COMMENTS:
            Impact: The function returns an integer (max value) cast as a pointer, which will likely cause:
            * Segmentation faults when caller tries to access the "array"
            * Memory leaks (allocated array is never free)
            * Completely wrong behavior
        WHY IT CAN HAPPEN:
            LLM can stick to the %rax as a return value, which is x0 in ARMv8 -> it can cause misunderstanding that return value should be maximum -> because %rax used for computations in [input] file ->  used for array indexing and storing results 