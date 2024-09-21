//! Turn on the screen
POT 1
DVW 0x12

//! Draw something 
WCHR M, #9, #5, #4, 0xf00
WCHR A, #15, #5, #4, 0xf00
WCHR T, #21, #5, #4, 0xf00
POT 0
DVW 0x12
WCHR E, #27, #5, #4, 0xf00
WCHR U, #33, #5, #4, 0xf00
WCHR S, #40, #5, #4, 0xf00
WCHR Z, #46, #5, #4, 0xf00
POT 1
DVW 0x12



HALT
