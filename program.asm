// Turn on the screen updates
POT 1
DVW 0x12

POT 1
DVW 0x20


LOAD R1, #9
LOAD R2, #5
LOAD R3, #4
LOAD R4, 0xfff



// Draw something 
WCHR 0, R1, R2, R3, R4
HALT

