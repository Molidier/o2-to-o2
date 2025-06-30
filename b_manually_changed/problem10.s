# problem10/code.c
	.section	__TEXT,__text,regular,pure_instructions
	.build_version macos, 13, 0	sdk_version 13, 3
	.globl	_func0                          ; -- Begin function func0
	.p2align	2
_func0:                                 ; @func0
	.cfi_startproc
; %bb.0:
	stp	x22, x21, [sp, #-48]!           ; 16-byte Folded Spill
	.cfi_def_cfa_offset 48
	stp	x20, x19, [sp, #16]             ; 16-byte Folded Spill
	stp	x29, x30, [sp, #32]             ; 16-byte Folded Spill
	add	x29, sp, #32
	.cfi_def_cfa w29, 16
	.cfi_offset w30, -8
	.cfi_offset w29, -16
	.cfi_offset w19, -24
	.cfi_offset w20, -32
	.cfi_offset w21, -40
	.cfi_offset w22, -48
	cmp	w1, #1
	b.lt	LBB0_5
; %bb.1:
	mov	x20, x1
	mov	x19, x0
	mov	w21, w1
	lsl	x0, x21, #2
	bl	_malloc
	cbz	x0, LBB0_7
; %bb.2:
	ldr	w8, [x19]
	str	w8, [x0]
	cmp	w20, #1
	b.eq	LBB0_7
; %bb.3:
	add	x9, x0, #4
	add	x10, x19, #4
	sub	x11, x21, #1
LBB0_4:                                 ; =>This Inner Loop Header: Depth=1
	ldr	w12, [x10], #4
	cmp	w12, w8
	csel	w8, w12, w8, gt
	str	w8, [x9], #4
	subs	x11, x11, #1
	b.ne	LBB0_4
LBB0_5:
	mov	x0, #0
LBB0_6:
	ldp	x29, x30, [sp, #32]             ; 16-byte Folded Reload
	ldp	x20, x19, [sp, #16]             ; 16-byte Folded Reload
	ldp	x22, x21, [sp], #48             ; 16-byte Folded Reload
	ret
	.cfi_endproc
                                        ; -- End function
.subsections_via_symbols

