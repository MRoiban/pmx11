from dataclasses import dataclass
from typing import Any, List
from pmxlang.lexer import Token
from pmxlang.parser.visitor import StmtVisitor
from pmxlang.parser.expr import Expr


@dataclass
class Stmt:
    def accept(self, visitor: StmtVisitor) -> Any:
        raise NotImplementedError


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
class Import(Stmt):
    path: Token

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_import_stmt(self)


@dataclass
class Screen(Stmt):
    power: int
    width: int
    height: int
    background: int
    borderless: int
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
class If(Stmt):
    condition: Expr
    body: List[Stmt]
    else_body: List[Stmt] = None

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_if_stmt(self)


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


@dataclass
class Function(Stmt):
    name: Token
    params: List[Token]
    body: List[Stmt]

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_function_stmt(self)

@dataclass
class Mouse(Stmt):
    body: List[Stmt]

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_mouse_stmt(self)

@dataclass
class While(Stmt):
    condition: Expr
    body: List[Stmt]

    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_while_stmt(self)

@dataclass
class Break(Stmt):
    def accept(self, visitor: StmtVisitor) -> Any:
        return visitor.visit_break_stmt(self)

