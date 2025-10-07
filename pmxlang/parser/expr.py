from dataclasses import dataclass
from typing import Any, List
from pmxlang.lexer import Token
from pmxlang.parser.visitor import ExprVisitor

# Forward reference for circular imports
Stmt = Any  # This will be imported from stmt.py by users of this module

@dataclass
class Expr:
    def accept(self, visitor: ExprVisitor) -> Any:
        raise NotImplementedError


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


@dataclass
class Peek(Expr):
    addr: Expr

    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_peek_expr(self)

@dataclass
class Peek2(Expr):
    addr: Expr

    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_peek2_expr(self)


@dataclass
class Poke(Expr):
    addr: Expr
    value: Expr

    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_poke_expr(self)


@dataclass
class Poke2(Expr):
    addr: Expr
    value: Expr

    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_poke2_expr(self)

@dataclass
class Str(Expr):
    text: Expr

    def accept(self, visitor: ExprVisitor) -> Any:
        return visitor.visit_str_expr(self)