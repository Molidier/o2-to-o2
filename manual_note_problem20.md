##Differences

Key ones:
    1. Category: extra register allocation in pred -> mimicing x86 spill and fill 
    * Code: ; %bb.0:

    2. Category: Wrong ASCII values and WRONG comparison -> shuffled ->immid values
    * Code: ; %bb.1, from %bb.6 till  %bb.15:

    3. Castegory:  Inefficient Buffer Address Calculation -> logically correct -> bad performance
    * Description: pred does it in each iteration
    * Code: LBB0_26,

    4. Categoty: do not use temporary registers 
        Code: 
        ####GD:
        LBB0_3:
            ldrb w6, [x0, x5]     ; Load character
            orr w7, w6, #0x20     ; Convert to lowercase (set bit 5)
            cmp w7, #32           ; Compare with space
            b.eq LBB0_5           ; Branch if space/null
            strb w6, [x9, x5]     ; Store original character
            add x5, x5, #1        ; Increment counter
            b LBB0_3              ; Continue loop
        ####PRED:
        LBB0_3:
            ldrb w5, [x0, x4]     ; Load character
            orr w5, w5, #0x20     ; Convert to lowercase (set bit 5)
            cmp w5, #32           ; Compare with space
            b.eq LBB0_5           ; Branch if space/null
            strb w5, [x5, x4]     ; Store LOWERCASE character
            add x4, x4, #1        ; Increment counter
            b LBB0_3              ; Continue loop
    5. Category: Comparison Logis Difference OR usong wrong register
    * Code: LBB0_5:   

    6. Category: pred repeat some logic -> do extra job
    * Description: show that x0 is a return value again

