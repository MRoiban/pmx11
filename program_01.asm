// Turn on the screen updates
POT 1
DVW 0x12

// Draw something 
WCHR M, #9, #5, #4, 0xfff
WCHR A, #15, #5, #4, 0xfff
WCHR T, #21, #5, #4, 0xfff
WCHR E, #27, #5, #4, 0xfff
WCHR U, #33, #5, #4, 0xfff
WCHR S, #40, #5, #4, 0xfff
WCHR Z, #46, #5, #4, 0xfff

// Turn off screen updates
POT 0
DVW 0x12
WCHR E, #27, #5, #4, 0x000
WCHR E, #27, #11, #4, 0xfff
// Turn on screen updates
POT 1
DVW 0x12

// Turn off screen updates
POT 0
DVW 0x12
WCHR E, #27, #11, #4, 0x000
WCHR E, #27, #16, #4, 0xfff
// Turn on screen updates
POT 1
DVW 0x12

// Turn off screen updates
POT 0
DVW 0x12
WCHR E, #27, #16, #4, 0x000
WCHR E, #27, #21, #4, 0xfff
// Turn on screen updates
POT 1
DVW 0x12

// Turn off screen updates
POT 0
DVW 0x12
WCHR E, #27, #21, #4, 0x000
WCHR E, #27, #26, #4, 0xfff
// Turn on screen updates
POT 1
DVW 0x12

HALT
