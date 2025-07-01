## Differences

### Key Ones:

1. **Category: Extra Register Allocation in PRED -> Mimicking x86 Spill and Fill**
    - **Code**: ; **%bb.0**

2. **Category: Wrong ASCII Values and WRONG Comparison -> Shuffled -> Immediate Values**
    - **Code**: ; **%bb.1**, from **%bb.6** till **%bb.15**

3. **Category: Inefficient Buffer Address Calculation -> Logically Correct -> Bad Performance**
    - **Description**: PRED does it in each iteration.
    - **Code**: **LBB0_26**

4. **Category: Do Not Use Temporary Registers**
    - **Code**:

        #### GD:
        ```asm
        LBB0_3:
            ldrb w6, [x0, x5]     ; Load character
            orr w7, w6, #0x20     ; Convert to lowercase (set bit 5)
            cmp w7, #32           ; Compare with space
            b.eq LBB0_5           ; Branch if space/null
            strb w6, [x9, x5]     ; Store original character
            add x5, x5, #1        ; Increment counter
            b LBB0_3              ; Continue loop
        ```

        #### PRED:
        ```asm
        LBB0_3:
            ldrb w5, [x0, x4]     ; Load character
            orr w5, w5, #0x20     ; Convert to lowercase (set bit 5)
            cmp w5, #32           ; Compare with space
            b.eq LBB0_5           ; Branch if space/null
            strb w5, [x5, x4]     ; Store LOWERCASE character
            add x4, x4, #1        ; Increment counter
            b LBB0_3              ; Continue loop
        ```

5. **Category: Comparison Logic Difference OR Using Wrong Register**
    - **Code**: **LBB0_5**

6. **Category: PRED Repeats Some Logic -> Does Extra Work**
    - **Description**: Shows that `x0` is a return value again.
