// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

// Put your code here.
//sum=0
@2	//GO TO FINAL ANSWER BOX
M=0

@0
D=A
@R2
D=M

//RAM[0]=R0
@R0
D=M

//RAM[1]=R1
@R1
D=M

(LOOP)
// if R0<0 goto END
@20
D;JLE
//R1-1
@R1
M=M-1
//load R1
@R0
D=M
//add R1 to R2 who is the summer
@R2
M=D+M
@R1
D=M
// if R0>=0 goto END
@10
D;JGT
(END) // infinite loop
@END
0;JMP