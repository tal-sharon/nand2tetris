// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// The program should swap between the max. and min. elements of an array.
// Assumptions:
// - The array's start address is stored in R14, and R15 contains its length
// - Each array value x is between -16384 < x < 16384
// - The address in R14 is at least >= 2048
// - R14 + R15 <= 16383
//
// Requirements:
// - Changing R14, R15 is not allowed.

	// set max and min address to first value of array
	@R14
	D=M
	@MaxAddress
	M=D
	@MinAddress
	M=D
	// set  i = 0
	@i
	M=0

(LOOP)
	// if (i = R15) -> reached end of array -> goto SWAP
	@R15
	D=M
	@i
	D=D-M
	@SWAP
	D;JEQ

	// update current value
	@R14
	D=M
	@i
	A=M+D
	D=M
	@curValue
	M=D

	// compare current value to max
	@MaxAddress
	A=M
	D=M
	@curValue
	D=D-M
	@UpdateMAX
	D;JLT // if max<current -> update max
	
(CompMIN) // compare current value to min
	@MinAddress
	A=M
	D=M
	@curValue
	D=D-M
	@UpdateMIN
	D;JGT // if min>current -> update min

(INC) // i = i + 1
	@i
	M=M+1
	@LOOP
	0;JMP

(UpdateMAX) // update max
	@R14
	D=M
	@i
	D=D+M
	@MaxAddress
	M=D
	@CompMIN
	0;JMP

(UpdateMIN) // update min
	@R14
	D=M
	@i
	D=D+M
	@MinAddress
	M=D
	@INC
	0;JMP

(SWAP) // swap max and min
	@MaxAddress
	A=M
	D=M
	@TEMP
	M=D
	@MinAddress
	A=M
	D=M
	@MaxAddress
	A=M
	M=D
	@TEMP
	D=M
	@MinAddress
	A=M
	M=D

(END)
	@END
	0;JMP
