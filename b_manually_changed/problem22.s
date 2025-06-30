# problem22/code.c
	.section	__TEXT,__text,regular,pure_instructions
	.build_version macos, 13, 0	sdk_version 13, 3
	.globl	_func0                          ; -- Begin function func0
	.p2align	2
_func0:                                 ; @func0
	.cfi_startproc
; %bb.0:
	ldr	s2, [x0]
	mov	w8, w1
	fmov	s0, s2
	fmov	s1, s2
	cmp	w1, #1
	b.le	LBB0_3
; %bb.1:
	add	x9, x0, #4
	sub	x10, x8, #1
	fmov	s3, s2
	fmov	s4, s2
LBB0_2:                                 ; =>This Inner Loop Header: Depth=1
	ldr	s1, [x9], #4
	fcmp	s1, s4
	fcsel	s4, s1, s4, mi
	fcmp	s1, s3
	fcsel	s3, s1, s3, gt
	subs	x10, x10, #1
	b.ne	LBB0_2
LBB0_3:
	cmp	w1, #1
	b.lt	LBB0_12
; %bb.4:
	fsub	s1, s3, s4         ;-> CHAMGED -> range=max_value-min_value
	fsub	s2, s2, s0
	fdiv	s2, s2, s1
	str	s2, [x0]
	cmp	w1, #1
	b.eq	LBB0_12
; %bb.5:
	sub	x10, x8, #1
	cmp	x10, #16
	b.hs	LBB0_7
; %bb.6:
	mov	w9, #1
	b	LBB0_10
LBB0_7:
	and	x11, x10, #0xfffffffffffffff0
	orr	x9, x11, #0x1
	dup.4s	v2, v0[0]
	dup.4s	v3, v1[0]
	add	x12, x0, #36
	mov	x13, x11
LBB0_8:                                 ; =>This Inner Loop Header: Depth=1
	ldp	q4, q5, [x12, #-32]
	ldp	q6, q7, [x12]
	fsub.4s	v4, v4, v2
	fsub.4s	v5, v5, v2
	fsub.4s	v6, v6, v2
	fsub.4s	v7, v7, v2
	fdiv.4s	v4, v4, v3
	fdiv.4s	v5, v5, v3
	fdiv.4s	v6, v6, v3
	fdiv.4s	v7, v7, v3
	stp	q4, q5, [x12, #-32]
	stp	q6, q7, [x12], #64
	subs	x13, x13, #16
	b.ne	LBB0_8
; %bb.9:
	cmp	x10, x11
	b.eq	LBB0_12
LBB0_10:
	add	x10, x0, x9, lsl #2
	sub	x8, x8, x9
LBB0_11:                                ; =>This Inner Loop Header: Depth=1
	ldr	s2, [x10]
	fsub	s2, s2, s4                  ; => CHANGED => s0 to s4 => min_val
	fdiv	s2, s2, s1
	str	s2, [x10], #4
	subs	x8, x8, #1
	b.ne	LBB0_11
LBB0_12:
	ret
	.cfi_endproc
                                        ; -- End function
.subsections_via_symbols

