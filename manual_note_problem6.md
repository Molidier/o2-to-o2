# Notes about ARMv8
* x29 -> frame pointer of the calling function
* x30 -> link register -> holds the return value
* csel -> conditional select instruction
* wzr -> 0 register
* b.hs -> greater or equal

# Notes about the Assembly Code
* LBB0_4: -> super fast SIMD loop -> to process 16 elements at a time

# Problem 6

## Same Parts:
1. **Function Prologue: Setting Up the Stack** -> 1-20
2. **Moving Arguments into Registers** -> 21-23
    * COMMENT: 'Dead code elimination works fine -> out_size was an input value at first, but in both codes it is not moved from x3 because no matter what input is given, it is anyway changed later in the code, and the initial value is not used.'
    * NOTE: "First, it took value from x0 as it is the first input, moved to x20 to save the value and later in [ln29] used it as a return value variable -> out."

3. **Size Calculation and Out_Size Assignment**: 24-28 -> first line of C code 
    * COMMENT: 'Correctly identify arguments that are given as an input.'

4. **Memory Allocation** 29-30
    * NOTES:
        * sbfiz x0, x8, #2, #32 -> just multiplied by 2
        * _malloc -> a standard C library function
        
5. **Conditional Branching Based on Size** -> 31-32
    * COMMENT: 'Optimization skips the for loop twice without checking it the second time if size < 1 [cmp w21, #1] -> works fine for [gd], but [pred] is implementing the same logic in [ln36].'

## Different Parts:

6. **Storing the First Value** 
    * [same]: 33-34, 36
    * [diff]: [cmp w21, #1] -> pred uses it again !!! -> [It does not cause any problem, just repeating.]
    * NOTE: Apparently, the input is not the array itself, but the pointer to the memory address of the [0] element.

7. **Main Loop to Process the Rest of the Array**
    * [same]: 37-38, 41
    * [diff]: 39 -> [No problem caused -> pred uses x10 in all places where gd uses x11 for the same purposes.]
    * 40 -> Different values for the number of elements to pass to SIMD loop to handle them all at one time in a loop -> [gd] uses 16 -> 4 integers in 4 NEON regs.

8. **Loop: Handling Large Arrays (SIMD Operations)**
    * [same]: 46, 49, 52
    * [diff]: 47, 50 -> [No problem caused -> 16 for gd and 8 for pred -> the same in terms of logic as in the previous lines] -> clear lower # elements -> Guarantees that the vector loop processes only full 16-element blocks.
        * 48 -> [gd] -> Converts the rounded length into an iteration count: one trip through the inner loop handles exactly 16 source integers (and 16 delimiters), so dividing by 16 tells the code how many trips it must make. [pred] -> does not have something like this -> does not increment the variable that controls the loop.
        * 50  
        * 51  
        * 53-55
