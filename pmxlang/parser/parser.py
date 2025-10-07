from dataclasses import dataclass
from typing import List
from pmxlang.lexer import Token, TokenType
from pmxlang.parser.expr import (
    Expr, Binary, End, Grouping, 
    Literal, Unary, Variable, Assign, Poke, Peek, Poke2, Peek2, Str
)
from pmxlang.parser.stmt import (
    Stmt, Expression, For, Print, Screen, Cls, Line, 
    Rect, Circle, Pixel, RectFill, Sprint,
    Function, If, Mouse, While, Break, Import, Memcpy, Memmov, Button, #"""Peek2"""       
    Label, ChangeLabelText
)


@dataclass
class Parser:
    tokens: List[Token]
    current: int = 0

    def __post_init__(self):
        if not self.tokens:
            raise ValueError("Cannot initialize Parser with empty token list")

    # Statements
    def statement(self) -> Stmt:
        print("here in statement")
        if self.match(TokenType.FOR):
            return self.for_statement()
        elif self.match(TokenType.IF):
            return self.if_statement()
        elif self.match(TokenType.PRINT):
            return self.print_statement()
        elif self.match(TokenType.SCREEN):
            return self.screen_statement()
        elif self.match(TokenType.CLS):
            return self.cls_statement()
        elif self.match(TokenType.LINE):
            return self.line_statement()
        elif self.match(TokenType.RECT):
            return self.rect_statement()
        elif self.match(TokenType.CIRCLE):
            return self.circle_statement()
        elif self.match(TokenType.PIXEL):
            return self.pixel_statement()
        elif self.match(TokenType.RECTFILL):
            return self.rectfill_statement()
        elif self.match(TokenType.SPRINT):
            return self.sprint_statement()
        elif self.match(TokenType.POKE):
            return self.poke_statement()
        # elif self.match(TokenType.PEEK2):
        #     print("here in peek2")
        #     return self.peek2_statement()
        elif self.match(TokenType.POKE2):
            return self.poke2_statement()
        elif self.match(TokenType.DEF):
            return self.function_statement()
        elif self.match(TokenType.END):
            return self.end_statement()
        elif self.match(TokenType.MOUSE):
            return self.mouse_statement()
        elif self.match(TokenType.WHILE):
            return self.while_statement()
        elif self.match(TokenType.BREAK):
            return self.break_statement()
        elif self.match(TokenType.IMPORT):
            return self.import_statement()
        elif self.match(TokenType.MEMCPY):
            return self.memcpy_statement()
        elif self.match(TokenType.MEMMOV):
            return self.memmov_statement()
        elif self.match(TokenType.BUTTON):
            return self.button_statement()
        elif self.match(TokenType.LABEL):
            return self.label_statement()
        elif self.match(TokenType.CHANGE_LABEL_TEXT):
            return self.change_label_text_statement()
        return self.expression_statement()

    def change_label_text_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after change label text call")
        id = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after change label text id")
        text = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after change label text body")
        return ChangeLabelText(id, text)

    def label_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after label call")
        text = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after label text")
        x = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after label x")
        y = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after label y")
        scale = self.expression()   
        self.consume(TokenType.COMMA, "Expect ',' after label scale")
        color = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after label color")
        id = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after label body")
        type = 1
        return Label(type, text, x, y, scale, color, id)

    def peek2_statement(self) -> Stmt:
        print("here in peek2")
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after peek2 call")
        addr = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after peek2 addr")
        return Peek2(addr)

    def button_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after button call")
        type = 0
        x = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after button x")
        y = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after button y")
        w = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after button width")
        h = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after button height")
        function_addr = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after button function address")
        id = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after button id")
        text = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after button text")
        return Button(type, x, y, w, h, function_addr, id, text)

    def memcpy_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after memcpy call")
        src = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after memcpy src")
        dst = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after memcpy dst")
        size = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after memcpy body")
        return Memcpy(src, dst, size)

    def memmov_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after memmov call")
        src = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after memmov src")
        dst = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after memmov dst")
        size = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after memmov body")
        return Memmov(src, dst, size)
        

    def function_statement(self) -> Stmt:
        name = self.consume(TokenType.IDENTIFIER, "Expect function name after 'def'")
        params = []
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after function name")
        if not self.check(TokenType.RIGHT_PAREN):
            params.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name"))
            while self.match(TokenType.COMMA):
                params.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name"))
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters")
        self.consume(TokenType.COLON, "Expect ':' after parameters")
        body = self.expression()
        return Function(name, params, body)

    def end_statement(self) -> Stmt:
        return Expression(End())

    def poke_statement(self) -> Stmt:   
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after poke call")
        addr = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after poke addr")
        value = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after poke value")
        from pmxlang.parser.expr import Poke as PokeExpr
        return Expression(PokeExpr(addr, value))

    def peek_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after peek call")
        addr = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after peek addr")
        from pmxlang.parser.expr import Peek as PeekExpr
        return Expression(PeekExpr(addr))

    def poke2_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after poke2 call")
        addr = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after poke2 addr")
        value = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after poke2 value")
        from pmxlang.parser.expr import Poke2 as Poke2Expr
        return Expression(Poke2Expr(addr, value))

    def print_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after print call")
        body = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after print body")
        return Print(body)

    def screen_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after screen call")
        power = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after screen power")
        width = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after screen width")
        height = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after screen height")
        background = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after screen background")
        borderless = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after screen body")
        return Screen(power, width, height, background, borderless)

    def cls_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after cls call")
        body = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after cls body")
        return Cls(body)

    def import_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after import call")
        path = self.consume(TokenType.STRING, "Expect string after import call")
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after import body")
        return Import(path)

    def line_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after line call")
        x1 = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after line x1")
        y1 = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after line y1")
        x2 = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after line x2")
        y2 = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after line y2")
        scale = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after line scale")
        color = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after line body")
        return Line(x1, y1, x2, y2, scale, color)

    def rect_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after rect call")
        x = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after rect x")
        y = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after rect y")
        w = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after rect w")
        h = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after rect h")
        scale = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after rect scale")
        color = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after rect body")
        return Rect(x, y, w, h, scale, color)

    def rectfill_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after rectfill call")
        x = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after rectfill x")
        y = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after rectfill y")
        w = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after rectfill w")
        h = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after rectfill h")
        scale = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after rectfill scale")
        color = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after rectfill body")
        return RectFill(x, y, w, h, scale, color)

    def circle_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after circle call")
        body = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after circle body")
        return Circle(body)

    def pixel_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after pixel call")
        x = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after pixel x")
        y = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after pixel y")
        scale = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after pixel scale")
        color = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after pixel body")
        return Pixel(x, y, scale, color)

    def mouse_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after mouse call")
        body = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after mouse body")
        return Mouse(body)

    def sprint_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after sprint call")
        string = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after sprint x")
        x = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after sprint y")
        y = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after sprint scale")
        scale = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after sprint color")
        color = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after sprint body")
        return Sprint(string, x, y, scale, color)

    def break_statement(self) -> Stmt:
        return Break()

    def while_statement(self) -> Stmt:
        condition = self.expression()
        self.consume(TokenType.COLON, "Expect ':' after while condition")
        
        body = []
        while not (self.check(TokenType.END) or self.check(TokenType.EOF)):
            body.append(self.statement())
        
        # Consume the END token if present
        if self.check(TokenType.END):
            self.consume(TokenType.END, "Expect 'end' to close while loop")
        return While(condition, body)


    def for_statement(self) -> Stmt:
        # Parse 'for init, condition, action:'
        init = self.expression()

        self.consume(TokenType.COMMA, "Expect ',' after for loop initialization")
        condition = self.expression()

        self.consume(TokenType.COMMA, "Expect ',' after for loop condition")
        action = self.expression()

        self.consume(TokenType.COLON, "Expect ':' after for loop clauses")

        # Parse body statements until END statement
        body = []
        while not (self.check(TokenType.END) or self.check(TokenType.EOF)):
            body.append(self.statement())
        
        # Consume the END token if present
        if self.check(TokenType.END):
            self.consume(TokenType.END, "Expect 'end' to close for loop")

        return For(init, condition, action, body)
        
    def if_statement(self) -> Stmt:
        # Parse condition
        condition = self.expression()
        
        self.consume(TokenType.COLON, "Expect ':' after if condition")
        
        # Parse body statements until END statement or ELSE token
        body = []
        while not (self.check(TokenType.END) or self.check(TokenType.ELSE) or self.check(TokenType.EOF)):
            body.append(self.statement())
        
        # Check for else clause
        else_body = None
        if self.match(TokenType.ELSE):
            self.consume(TokenType.COLON, "Expect ':' after else")
            
            # Parse else body statements until END statement
            else_body = []
            while not (self.check(TokenType.END) or self.check(TokenType.EOF)):
                else_body.append(self.statement())
        
        # Consume the END token if present
        if self.check(TokenType.END):
            self.consume(TokenType.END, "Expect 'end' to close if statement")
            
        return If(condition, body, else_body)

    def expression_statement(self) -> Stmt:
        expr = self.expression()
        return Expression(expr)

    # Expressions
    def expression(self) -> Expr:
        return self.assignment()

    def assignment(self) -> Expr:
        expr = self.equality()
        if self.match(TokenType.EQUAL):
            value = self.assignment()

            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)

            self.error(self.previous(), "Invalid assignment target.")

        return expr

    def equality(self) -> Expr:
        expr = self.comparison()
        while self.match(TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)
        return expr

    def match(self, *types: TokenType) -> bool:
        for t in types:
            if self.check(t):
                self.advance()
                return True
        return False

    def check(self, type: TokenType) -> bool:
        if self.isAtEnd():
            return False
        return self.peek().type == type

    def isAtEnd(self) -> bool:
        return self.peek().type == TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def advance(self) -> Token:
        if not self.isAtEnd():
            self.current += 1
        return self.previous()

    def comparison(self) -> Expr:
        expr = self.term()
        while self.match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)
        return expr

    def term(self) -> Expr:
        expr = self.factor()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)
        return expr

    def factor(self) -> Expr:
        expr = self.unary()
        while self.match(TokenType.STAR, TokenType.SLASH, TokenType.MODULO):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)
        return expr

    def unary(self) -> Expr:
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)
        return self.primary()

    def primary(self) -> Expr:
        if self.match(TokenType.FALSE):
            return Literal(False)
        if self.match(TokenType.TRUE):
            return Literal(True)
        if self.match(TokenType.NONE):
            return Literal(None)
        if self.match(TokenType.NUMBER):
            return Literal(int(self.previous().lexeme))
        if self.match(TokenType.HEX):
            return Literal(self.previous().lexeme)
        if self.match(TokenType.STRING):
            return Literal(self.previous().lexeme)
        if self.match(TokenType.PEEK):
            self.consume(TokenType.LEFT_PAREN, "Expect '(' after peek call")
            addr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after peek addr")
            return Peek(addr)
        if self.match(TokenType.POKE):
            self.consume(TokenType.LEFT_PAREN, "Expect '(' after poke call")
            addr = self.expression()
            self.consume(TokenType.COMMA, "Expect ',' after poke addr")
            value = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after poke value")
            return Poke(addr, value)
        if self.match(TokenType.POKE2):
            self.consume(TokenType.LEFT_PAREN, "Expect '(' after poke2 call")
            addr = self.expression()
            self.consume(TokenType.COMMA, "Expect ',' after poke2 addr")
            value = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after poke2 value")
            return Poke2(addr, value)
        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())
        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect closing ')'")
            return Grouping(expr)
        if self.match(TokenType.PEEK2):
            self.consume(TokenType.LEFT_PAREN, "Expect '(' after peek2 call")
            addr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after peek2 addr")
            return Peek2(addr)
        if self.match(TokenType.STR):
            self.consume(TokenType.LEFT_PAREN, "Expect '(' after str call")
            text = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after str text")
            return Str(text)
        raise SyntaxError(f"Unexpected token {self.peek().lexeme}")

    def consume(self, type: TokenType, message: str) -> Token:
        if self.check(type):
            return self.advance()
        self.error(self.peek(), message)

    def error(self, token: Token, message: str) -> None:
        if token.type == TokenType.EOF:
            message += " at end"
        else:
            message += f" at {token.lexeme}"
        raise SyntaxError(message)

    def synchronize(self):
        self.advance()
        while not self.isAtEnd():
            match self.peek().type:
                case TokenType.IF:
                    return
                case TokenType.RETURN:
                    return
                case TokenType.FOR:
                    return
                case TokenType.PRINT:
                    return
                case TokenType.SCREEN:
                    return
                case TokenType.CLS:
                    return
                case TokenType.LINE:
                    return
                case TokenType.RECT:
                    return
                case TokenType.CIRCLE:
                    return
                case TokenType.PIXEL:
                    return
                case TokenType.RECTFILL:
                    return
                case TokenType.SPRINT:
                    return
                case TokenType.POKE:
                    return
                case TokenType.PEEK:
                    return
                case TokenType.POKE2:
                    return
                case TokenType.PEEK2:
                    return
            self.advance()

    def parse(self) -> List[Stmt]:
        statements = []
        try:
            while not self.isAtEnd():
                statements.append(self.statement())
            return statements
        except SyntaxError as e:
            print(f"Syntax Error: {e}")
            self.synchronize()
            raise  # Re-raise to show the full error 