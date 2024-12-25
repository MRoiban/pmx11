    POT #10
    POT #2
    DIV     ; testing new division opcode
    POT #10
    MUL     ; testing new multiplication opcode
    POT #3
    POW
    POT #1
    DVW 0x10 ; Turn on the screen
    POT #1
    DVW 0x12 ; Draw char from mem
    WCHR M, #9, #5, #4, 0xfff 
    HALT