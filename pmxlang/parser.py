from dataclasses import dataclass
from re import X
from typing import Protocol, Any, List, Optional
from pmxlang.lexer import Token, TokenType


# Visitor protocols
class ExprVisitor(Protocol):
    def visit_binary_expr(self, expr: "Binary") -> Any: ...
    def visit_grouping_expr(self, expr: "Grouping") -> Any: ...
    def visit_literal_expr(self, expr: "Literal") -> Any: ...
    def visit_unary_expr(self, expr: "Unary") -> Any: ...
    def visit_variable_expr(self, expr: "Variable") -> Any: ...
    def visit_assign_expr(self, expr: "Assign") -> Any: ...
    def visit_function_expr(self, expr: "Function") -> Any: ...
    def visit_end_expr(self, expr: "End") -> Any: ...
    


class StmtVisitor(Protocol):
    def visit_expression_stmt(self, stmt: "Expression") -> Any: ...
    def visit_for_stmt(self, stmt: "For") -> Any: ...
    def visit_print_stmt(self, stmt: "Print") -> Any: ...
    def visit_screen_stmt(self, stmt: "Screen") -> Any: ...
    def visit_cls_stmt(self, stmt: "Cls") -> Any: ...
    def visit_line_stmt(self, stmt: "Line") -> Any: ...
    def visit_rect_stmt(self, stmt: "Rect") -> Any: ...
    def visit_circle_stmt(self, stmt: "Circle") -> Any: ...
    def visit_pixel_stmt(self, stmt: "Pixel") -> Any: ...
    def visit_rectfill_stmt(self, stmt: "RectFill") -> Any: ...
    def visit_sprint_stmt(self, stmt: "Sprint") -> Any: ...
    def visit_poke_stmt(self, stmt: "Poke") -> Any: ...
    def visit_poke2_stmt(self, stmt: "Poke2") -> Any: ...
    def visit_peek_stmt(self, stmt: "Peek") -> Any: ...
    def visit_peek2_stmt(self, stmt: "Peek2") -> Any: ...
    def visit_function_stmt(self, stmt: "Function") -> Any: ...

# Base classes
@dataclass
class Expr:
    def accept(self, visitor: ExprVisitor) -> Any:
        raise NotImplementedError


@dataclass
class Stmt:
    def accept(self, visitor: StmtVisitor) -> Any:
        raise NotImplementedError


# Different expression types
@dataclass
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_binary_expr(self)


@dataclass
class Function(Expr):
    name: Token
    params: List[Token]
    body: List[Stmt]

    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_function_expr(self)

@dataclass
class End(Expr):
    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_end_expr(self)

@dataclass
class Grouping(Expr):
    expression: Expr

    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_grouping_expr(self)


@dataclass
class Literal(Expr):
    value: Any

    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_literal_expr(self)


@dataclass
class Unary(Expr):
    operator: Token
    right: Expr

    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_unary_expr(self)


@dataclass
class Variable(Expr):
    name: Token

    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_variable_expr(self)


@dataclass
class Assign(Expr):
    name: Token
    value: Expr

    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_assign_expr(self)


# Statement types
@dataclass
class Expression(Stmt):
    expression: Expr

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_expression_stmt(self)


@dataclass
class For(Stmt):
    init: Expr
    condition: Expr
    action: Expr
    body: List[Stmt]

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_for_stmt(self)


@dataclass
class Print(Stmt):
    body: List[Stmt]

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_print_stmt(self)


@dataclass
class Screen(Stmt):
    body: List[Stmt]

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_screen_stmt(self)


@dataclass
class Cls(Stmt):
    body: List[Stmt]

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_cls_stmt(self)


@dataclass
class Line(Stmt):
    x1: Expr
    y1: Expr
    x2: Expr
    y2: Expr
    scale: Expr
    color: Expr

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_line_stmt(self)


@dataclass
class Rect(Stmt):
    x: Expr
    y: Expr
    w: Expr
    h: Expr
    scale: Expr
    color: Expr

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_rect_stmt(self)

@dataclass
class RectFill(Stmt):
    x: Expr
    y: Expr
    w: Expr
    h: Expr
    scale: Expr
    color: Expr

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_rectfill_stmt(self)

@dataclass
class Circle(Stmt):
    body: List[Stmt]

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_circle_stmt(self)

@dataclass
class Poke(Stmt):
    addr: int
    value: Expr

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_poke_stmt(self)

@dataclass
class Peek(Stmt):
    addr: int

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_peek_stmt(self)

@dataclass
class Poke2(Stmt):
    addr: int
    value: Expr

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_poke2_stmt(self)

@dataclass
class Peek2(Stmt):
    addr: int

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_peek2_stmt(self)

@dataclass
class Pixel(Stmt):
    x: Expr
    y: Expr
    scale: Expr
    color: Expr

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_pixel_stmt(self)

@dataclass
class Sprint(Stmt):
    string: Expr
    x: Expr
    y: Expr
    scale: Expr
    color: Expr

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_sprint_stmt(self)

class AstPrinter:
    def print(self, expr: Expr) -> str:
        return expr.accept(self)

    def visit_binary_expr(self, expr: Binary) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self, expr: Grouping) -> str:
        return self.parenthesize("group", expr.expression)

    def visit_literal_expr(self, expr: Literal) -> str:
        return "nil" if expr.value is None else str(expr.value)

    def visit_unary_expr(self, expr: Unary) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.right)

    def visit_variable_expr(self, expr: "Variable") -> str:
        return expr.name.lexeme

    def visit_assign_expr(self, expr: "Assign") -> str:
        return f"(= {expr.name.lexeme} {expr.value.accept(self)})"

    def parenthesize(self, name: str, *exprs: Expr) -> str:
        return f"({name} {' '.join(expr.accept(self) for expr in exprs)})"


# # example usage
# expr = Binary(Literal(1), "+", Binary(Literal(2), "*", Literal(3)))
# printer = AstPrinter()
# print(printer.print(expr))  # prints "(+ 1 (* 2 3))"


@dataclass
class Parser:
    tokens: List[Token]
    current: int = 0

    def __post_init__(self):
        if not self.tokens:
            raise ValueError("Cannot initialize Parser with empty token list")

    # Statements
    def statement(self) -> Stmt:
        if self.match(TokenType.FOR):
            return self.for_statement()
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
        elif self.match(TokenType.PEEK):
            return self.peek_statement()
        elif self.match(TokenType.POKE2):
            return self.poke2_statement()
        elif self.match(TokenType.PEEK2):
            return self.peek2_statement()
        elif self.match(TokenType.DEF):
            return self.function_statement()
        elif self.match(TokenType.END):
            return self.end_statement()

        return self.expression_statement()

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
        return End()

    def poke_statement(self) -> Stmt:   
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after poke call")
        addr = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after poke addr")
        value = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after poke value")
        return Poke(addr, value)

    def peek_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after peek call")
        addr = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after peek addr")
        return Peek(addr)

    def poke2_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after poke2 call")
        addr = self.expression()
        self.consume(TokenType.COMMA, "Expect ',' after poke2 addr")
        value = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after poke2 value")
        return Poke2(addr, value)

    def peek2_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after peek2 call")
        addr = self.expression()    
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after peek2 addr")
        return PEEK2(addr)

    def print_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after print call")
        body = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after print body")
        return Print(body)

    def screen_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after screen call")
        body = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after screen body")
        return Screen(body)

    def cls_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after cls call")
        body = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after cls body")
        return Cls(body)

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

    def for_statement(self) -> Stmt:
        # Parse 'for init, condition, action:'
        init = self.expression()

        self.consume(TokenType.COMMA, "Expect ',' after for loop initialization")
        condition = self.expression()

        self.consume(TokenType.COMMA, "Expect ',' after for loop condition")
        action = self.expression()

        self.consume(TokenType.COLON, "Expect ':' after for loop clauses")

        # Parse body statements
        body = [self.statement()]

        return For(init, condition, action, body)

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
        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())
        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect closing ')'")
            return Grouping(expr)
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
            # if self.peek().type == TokenType.SEMICOLON:
            #     return
            match self.peek().type:
                case TokenType.IF:
                    pass
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


# Test the parser with a simple expression: 1 + 2 * 3


# parser = Parser(test_tokens)
# ast = parser.parse()
# printer = AstPrinter()
# print("AST:", printer.print(ast))
