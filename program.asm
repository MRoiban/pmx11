// Draw something -> to WSTR
; WCHR M, #9, #5, #4, 0xfff
; WCHR A, #15, #5, #4, 0xfff
; WCHR T, #21, #5, #4, 0xfff
; WCHR E, #27, #5, #4, 0xfff
; WCHR U, #33, #5, #4, 0xfff
; WCHR S, #40, #5, #4, 0xfff
; WCHR Z, #46, #5, #4, 0xfff

;POT #1
;LABEL loop 
;INC
;JMP $loop

POT #10
LOAD R1, #10
MOV R1, R2

POT #1
DVW 0x20
POT #1
DVW 0x10
POT #1
DVW 0x12
POT #1
DVW 0x13

WSTR BILAL12, #9, #5, #4, 0xfff

HALT