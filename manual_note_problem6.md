#notes about ARMv8
* x29 -> frame pointer of the calling function
* x30 -> link register -> holds the return value
* csel -> conditional select insrtuction
* wzr -> 0 register
* b.hs -> greater or equal

#notes about the assembly code
* LBB0_4: -> super fast SIMD loop -> to process 16 elements at a time

#Problem6

##Same parts:
* 1. Function Prologue: Setting Up the Stack -> 1-20

* 2. Moving Arguments into Registers -> 21-23
    * COMMENT: 'Dead code elemenaation works fine -> out_size was an input value at first, but in both code it is not moved from x3 because no matter what input is gonna be given, it is anyway will be changed in code later and init value will not be used'
    * NOTE: "First it took value from x0 as it is the first input, moved to x20 to save the vale and later in [ln29] used it as a return value var->out"

* 3. Size Calculation and Out_Size Assignment: 24-28 -> first line of C code 
    * COMMENT: 'correctly identify arguments that are given as an input'

* 4. Memory allocation 29-30
    * NOTES:
        * sbfiz	x0, x8, #2, #32 -> just multiplied by 2
        * _malloc -> a standard C library function
        
* 5. Conditional Branching Based on size -> 31-32
    * COMMENT: 'opt skips the for loop two without checking it for the second time if size < 1 [cmp	w21, #1] -> works fine for [gd], but [pred] is implementing the same logic in [ln36]

##Different parts:
    
* 6. Storing the First Value -> 
    * [same]: 33-34, 36
    * [diff]: [cmp	w21, #1] -> pred use it again !!!-> [it does not cause any problem, just repeating]
    * NOTE: apparently, the input is not array itself, but pointer to the memory address of the [0] element

* 7. Main Loop to Process the Rest of the Array
    * [same]: 37-38, 41
    * [diff]: 39 -> [cause no problem -> [pred] use x10 in all places where gd use x11 for the same purposes]
        * 40 -> different values for number of elements to pass to SIMD loop to handle it all at one time in a loop -> [gd] use 16 -> 4 integers in 4 NEON regs

* 8. Loop: Handling Large Arrays (SIMD Operations)
    * [same]: 46, 49, 52
    * [diff]  47, 50-> [cause no prolem -> 16 for gd and 8 for pred -> the same in terms of logic that was in the previous lines] -> clear lower # elements -> Guarantees that the vector loop processes only full 16-element blocks
        * 48 -> [gd] -> Converts the rounded length into an iteration count: one trip through the inner loop handles exactly 16 source integers (and 16 delimiters), so dividing by 16 tells the code how many trips it must make. [pred] -> does not have smth like this -> does not increment the var that control the loop
        * 50  
        * 51  
        * 53-55

