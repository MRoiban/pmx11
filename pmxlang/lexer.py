from dataclasses import dataclass
from enum import Enum

class TokenType(Enum):
    EOF = 0
    COMMA = 1
    COLON = 2
    DOT = 3
    LEFT_PAREN = 4
    RIGHT_PAREN = 5
    PLUS = 6
    MINUS = 7
    STAR = 8
    SLASH = 9
    MODULO = 10
    BANG = 27
    BANG_EQUAL = 28
    EQUAL = 11
    EQUAL_EQUAL = 29
    GREATER = 12
    LESS = 13
    GREATER_EQUAL = 14
    LESS_EQUAL = 15
    IDENTIFIER = 16
    NUMBER = 17
    STRING = 18
    IF = 19
    ELSE = 20
    ELIF = 21
    TRUE = 22
    FALSE = 23
    NONE = 24
    AND = 25
    OR = 26
    FOR = 30
    WHILE = 31
    RETURN = 32
    PRINT = 33
    SCREEN = 34
    CLS = 35
    LINE = 36
    RECT = 37
    CIRCLE = 38
    PIXEL = 39
    RECTFILL = 40
    SPRINT = 41
    HEX = 42
    POKE = 43
    PEEK = 44
    POKE2 = 45
    PEEK2 = 46
    DEF = 47
    END = 48
    MOUSE = 49
    BREAK = 50
    IMPORT = 51
    MEMCPY = 52
    MEMMOV = 53
    BUTTON = 54
    LABEL = 55
    CHANGE_LABEL_TEXT = 56
    STR = 57
    
    

    def __add__(a, b):
        return f"{a}{b}"

@dataclass
class Token:
    type: TokenType
    lexeme: str
    literal: str
    line: int
    # column: int

    def to_string(self):
        return self.type + " " + self.lexeme + " " + self.literal

