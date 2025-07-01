## Differences

1. **%bb.0 and LBB0_6::**
    - **Label**: 'preserve regs using stack'
    
    * **Ground Truth**:
        - Two extra registers -> safer intermediate calculations -> can be part of optimization by adding new regs -> better for complex operations.
        
    * **Prediction**:
        - Just 8 regs, as in x86 input -> not optimized -> later causes a problem in line `pred-%bb.4:` where a temporary value should've been stored.

2. **%bb.4:**
    - **Label**: 'temporary register is needed to store intermediate values'
    
    * **Ground Truth**:
        - [47] `add w25, w23, #1           ; w25 = count + 1`
        - [53] `str x8, [x0, w23, sxtw #3] ; array[count]`
        - [54] `mov x23, x25               ; count = w25 (update count)`
        
    * **Prediction**:
        - [44] `add w23, w23, #1           ; count = count + 1`
        - [50] `str x8, [x0, w23, sxtw #3] ; array[count + 1]`
