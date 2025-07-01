## Differences

### Key Ones:

1. **Category: Others -> Failed to Correctly Calculate the Stack Offsets**
    - **Description**: It needs three bytes in a row to be freed by zeros -> pred does only two of them.
    - **Code**:

        #### Ground Truth:
        ```asm
        strb wzr, [sp, #14]
        strh wzr, [sp, #12]
        ```

        #### Prediction:
        ```asm
        strb wzr, [sp, #15]
        strh wzr, [sp, #14]
        ```

    - **Comment**: Affects later on the code, where the logical flow itself is correct, but the buffer was not set correctly initially.
    - **Code**:
        - **gd.txt (Correct)**: `add x0, sp, #12`
        - **pred.txt (Incorrect)**: `add x0, sp, #14`
        - `bl _strlen`
        - `cmp x0, #1`
        - ...
        - `add x8, sp, #12`
        - `add x8, x8, x0`
        - `strb w19, [x8]`
        - `strb w21, [x8]`

    - **Also affects section**: **LBB0_14**

2. **Category: Handling Loop Differently**
    - **Description**: Fine -> no logical error -> Stylistic difference
    - **Parts/Sections of Code**: **LBB0_9**

3. **Category: Handling Buffer Accessing Differently**
    - **Description**: Pred ones can be less effective.
    - **Code**:
        - **gd.txt (Correct)**: 
            ```asm
            add x20, x20, #1
            subs x22, x22, #1
            b.eq LBB0_20
            ldrb w19, [x20]
            ```
        - **pred.txt (Correct)**:
            ```asm
            add x23, x23, #1
            cmp x22, x23
            b.eq LBB0_21
            ldrb w21, [x20, x23]
            ```

4. **Category: Storing Incorrect Value + Taking it from Register, Instead of Using Immediate Value**
    - **Description**: This suggests GD is handling the ".|" note case (which should store value 1), while PRED is incorrectly storing value 4 (which should be for "o" notes).
    - **Same with LBB0_14 part**.
    - **Code**:
        - **GD.txt**:
            ```asm
            LBB0_4:                                 ;   in Loop: Header=BB0_5 Depth=1
            add x20, x20, #1
            subs x22, x22, #1
            b.eq LBB0_20
            ```
        - **PRED.txt**:
            ```asm
            LBB0_4:                                 ;   in Loop: Header=BB0_5 Depth=1
            add x23, x23, #1
            cmp x22, x23
            b.eq LBB0_21
            ```

5. **Category: Different Comparison Logic -> No Logical Error**
    - **Code**: **LBB0_10**

6. **Category: Doesn't Update the Array Pointer After Realloc, Leading to Potential Use of Freed Memory**
    - **Description**: Missing `mov` instructions.
    - **Code**: ; `%bb.8 -> last lines -> no code in pred`
        - **GD**:
            ```asm
            mov x0, x21
            bl _realloc
            mov x21, x0
            ```
        - **Prediction** (missing instructions):
            ```asm
            bl _realloc
            mov x25, x25
            ```

7. **Category: Branching to an Incorrect Function + Not Correct Cleanup Function**
    - **Description**: `b.hi LBB0_19` vs `b.hi LBB0_20`
        - **GD**: Proper error handling - sets output to safe values (NULL pointer, 0 count)
        - **PRED**: MAJOR BUG - branches to a loop continuation instead of error handling.
    - **Code**:
        - **GD**: **LBB0_19** (Error Path):
            ```asm
            LBB0_19:
            mov w23, #0          ; Set count to 0
            mov x21, #0          ; Set result array to NULL
            ```
        - **PRED**: **LBB0_20** (Error Path):
            ```asm
            LBB0_20:                                ; => This    Inner Loop Header: Depth=1
            strb wzr, [sp, #14]              ; Clear string buffer
            ```

8. **Category: Misusing x0 -> Using it in Computations AGAIN**
    - **Description**: Accessing freed memory. It's doing it because it misses an instruction (`mov`) that will store the new pointer to the array.
    - **Code**: -> **LBB0_13**
        - **GD**:
            ```asm
            str w8, [x21, w23, sxtw #2]    ; Uses x21 (array pointer) - CORRECT!
            ```
        - **PRED**:
            ```asm
            str w28, [x0, w24, sxtw #2]    ; Uses x0 (realloc return) - WRONG!
            ```
