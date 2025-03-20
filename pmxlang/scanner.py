from dataclasses import dataclass, field
from typing import List
from pmxlang.lexer import Token, TokenType

@dataclass
class Scanner:
    source:str
    start:int = 0
    current:int = 0
    line:int = 1
    tokens:List[Token] = field(default_factory=list)
    keywords = {
        "and":TokenType.AND,
        "if":TokenType.IF,
        "else":TokenType.ELSE,
        "elif":TokenType.ELIF,
        "true":TokenType.TRUE,
        "false":TokenType.FALSE,
        "or":TokenType.OR,
        "for":TokenType.FOR,
        "while":TokenType.WHILE,
        "return":TokenType.RETURN,
        "none":TokenType.NONE,
        "print":TokenType.PRINT,
        "screen":TokenType.SCREEN,
        "cls":TokenType.CLS,
        "line":TokenType.LINE,
        "rect":TokenType.RECT,
        "circle":TokenType.CIRCLE,
        "pixel":TokenType.PIXEL,
        "rectfill":TokenType.RECTFILL,
        "sprint":TokenType.SPRINT,
        "poke":TokenType.POKE,
        "peek":TokenType.PEEK,
        "poke2":TokenType.POKE2,
        "peek2":TokenType.PEEK2,
        "def":TokenType.DEF,
        "end":TokenType.END,
        "mouse":TokenType.MOUSE,
        "break":TokenType.BREAK,
        "import":TokenType.IMPORT,
    }

    def scanTokens(self):
        while not self.isAtEnd():
            self.start = self.current
            self.start = self.current
            self.scanToken()
        self.tokens.append(Token(TokenType.EOF, "", "", self.line))
        return self.tokens
    
    def isAtEnd(self):
        return self.current >= len(self.source)

    def advance(self):
        out = self.source[self.current]
        self.current += 1
        return out
    
    def match(self, expected):
        if self.isAtEnd():
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        return True
    
    def peek(self):
        if self.isAtEnd():
            return '\0'
        return self.source[self.current]

    def string(self):
        while self.peek() != '"' and (not self.isAtEnd()):
            if self.peek() == '\n': line += 1
            self.advance()

        if self.isAtEnd():
            print(f'Unterminated String at line {self.line}')
            return
        self.advance()
        text = self.source[self.start+1:self.current-1]
        self.addToken(TokenType.STRING, text)

    def isDigit(self, c):
        return c >= '0' and c <= '9'
    
    def isAlpha(self, c):
        return (c>='a' and c <= 'z') or (c>='A' and c <= 'Z') or (c == '_')

    def isAlphanumeric(self,c):
        return self.isAlpha(c) or self.isDigit(c)

    def identifier(self):
        while self.isAlphanumeric(self.peek()):
            self.advance()
        text = self.source[self.start:self.current]
        type = self.keywords[text] if text in self.keywords else TokenType.IDENTIFIER
        self.addToken(type)

    def number(self):
        while self.isDigit(self.peek()): self.advance()
        self.addToken(TokenType.NUMBER, int(self.source[self.start:self.current]))
    
    def hex(self):
        # Skip the "0x" prefix that we already confirmed
        self.advance()  # Skip 'x'
        
        # Make sure we have at least one hex digit
        if not self.isHex(self.peek()):
            print(f"Invalid hex number at line {self.line}")
            return
            
        while self.isHex(self.peek()): self.advance()
        self.addToken(TokenType.HEX, int(self.source[self.start:self.current], 16))
    
    def isHex(self, c):
        return (c >= '0' and c <= '9') or (c >= 'a' and c <= 'f') or (c >= 'A' and c <= 'F')

    def addToken(self, type:TokenType, literal=None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(type, text, literal, self.line))


    def scanToken(self):
        char = self.advance()
        match char:
            case "(": self.addToken(TokenType.LEFT_PAREN)
            case ")": self.addToken(TokenType.RIGHT_PAREN)
            case ":": self.addToken(TokenType.COLON)
            case "/": self.addToken(TokenType.SLASH)
            case "+": self.addToken(TokenType.PLUS)
            case "-": self.addToken(TokenType.MINUS)
            case ".": self.addToken(TokenType.DOT)
            case "*": self.addToken(TokenType.STAR)
            case ",": self.addToken(TokenType.COMMA)
            case "=": 
                self.addToken(TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL)
            case "!":
                self.addToken(TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG)
            case ">":
                self.addToken(TokenType.GREATER_EQUAL if self.match('=') else TokenType.GREATER)
            case "<":
                self.addToken(TokenType.LESS_EQUAL if self.match('=') else TokenType.LESS)
            case "#":
                # Comment - skip until the end of line
                while self.peek() != '\n' and not self.isAtEnd():
                    self.advance()
            case "\r":
                pass
            case "\t":
                pass
            case "\n":
                self.line += 1
            case " ":
                pass
            case '"':
                self.string()
            case "0":
                # Check for hex number (0x...)
                if self.peek() == 'x' or self.peek() == 'X':
                    self.hex()
                else:
                    # It's a regular number
                    self.current -= 1  # Go back to process as a normal digit
                    self.number()
            case _: 
                if self.isDigit(char):
                    self.number()
                elif self.isAlpha(char):
                    self.identifier()
                else:
                    print(f"Unexpected Token at {self.current}:'{char}' at line {self.line}")
          
  
# with open('pmxlang/examples/test.pmx', 'r') as file:
#     source = file.readlines()
#     src = ''
#     for e in source:
#         src += str(e)
#     print(src)
#     scanner = Scanner(src)
#     scanner.scanTokens()
#     print(scanner.tokens)
