##Differences

1. %bb.0 and LBB0_6:: 
    * label: 'preserve regs using stack'
    [gd]:
        two extra registers -> safer intermediate calculations -> can be a part of optimization adding new regs -> better for complex operations
    [pred]: 
        just 8 regs as in x86 input -> not optimized -> later cause a problem in line pred-%bb.4: -> where temporary value should've been stored

2. %bb.4: 
    * label: 'temporary register is needed to store inter. values'
    [gd]:
        [47] add	w25, w23, #1           ; w25 = count + 1
        [53] str	x8, [x0, w23, sxtw #3] ; array[count]
	    [54] mov	x23, x25               ; count = w25 (update count)
    [pred]:
        [44] add	w23, w23, #1           ; count = count + 1 
        [50] str	x8, [x0, w23, sxtw #3] ;array[count + 1]
 