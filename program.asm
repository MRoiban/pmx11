// NOT WORKING
// VAR X, #10              
// MOV X, R1         
     
; Turn on the screen updates
POT 1
DVW 0x12 ; screen drawing from memory

; Draw something 
WCHR M, #9, #5, #4, 0xfff
HALT