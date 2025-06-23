##Differences

1. LBB0_3
    * label: 'stp amd ret immidiately instead of jumpimg to the function LBB0_9:'

    [gd]:
        [23] b	LBB0_9          ; jump to store results
        COMMENT: pottentianlly better branch prediction
    [pred]:
        [23-24]:
            stp	w10, w11, [x2]  ; store immediately: [product, sum]
	        ret                 ; return immediately
2. LBB0_4: -> Critical differences
    * label_1: 'order of operations are different' -> should not affect the logical flow
    * label_2: 'initialize init product vectors' -> pred does not do 3/4 of initialization
    * label_3: 'use different regs' -> not critical -> does not preserve the naming order as [gd] does 
    [gd]:
        [30-35]:
            movi.4s	v1, #1
            movi.4s	v2, #1
            movi.4s	v3, #1
            movi.2d	v5, #0000000000000000
            movi.2d	v6, #0000000000000000
            movi.2d	v7, #0000000000000000
    [pred]:
        [28-33]:
            movi.2d	v0, #0000000000000000
            movi.4s	v1, #1
            mov	x11, x9
            movi.2d	v2, #0000000000000000
            movi.2d	v3, #0000000000000000
            movi.2d	v4, #0000000000000000

3. LBB0_5:  -> Critical differences
    * label: 'missuse of the vectors because of the lack of the initialized registers'
    [pred]:
        ; PRODUCT ACCUMULATION - OVERWRITES SUM DATA!
            mul.4s	v1, v5, v1               ; v1 *= elements[0-3] (OK - v1 not used for sum)
            mul.4s	v0, v6, v0               ; v0 *= elements[4-7] (BUG! destroys sum in v0)
            mul.4s	v2, v7, v2               ; v2 *= elements[8-11] (BUG! destroys sum in v2)
            mul.4s	v3, v16, v3              ; v3 *= elements[12-15] (BUG! destroys sum in v3)

4. %bb.6: -> Critical differences
    * label_1: 'work with corrupted data' -> but the pattern is right
    * label_2: 'missing multiplication part' -> to mulpitly 4 elements to each other and get the result product -> SIMD for the line  'product *= numbers[i]'
    [gd]:
        [55-57]:
        ; PRODUCT REDUCTION - Combine all product vectors
        mul.4s	v0, v1, v0               ; v0 = v0 * v1 (multiply first two product vectors)
        mul.4s	v0, v2, v0               ; v0 = v0 * v2 (multiply with third product vector)
        mul.4s	v0, v3, v0               ; v0 = v0 * v3 (multiply with fourth product vector)
    [pred]:
        [53]: mul.4s	v0, v1, v0       ; v0 = v1 * v0 (v0 contains corrupted sum/product mix)

