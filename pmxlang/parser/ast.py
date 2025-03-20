from pmxlang.parser.expr import Expr, Binary, Grouping, Literal, Unary, Variable, Assign, Function, End, Peek, Peek2, Poke, Poke2

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

    def visit_variable_expr(self, expr: Variable) -> str:
        return expr.name.lexeme

    def visit_assign_expr(self, expr: Assign) -> str:
        return f"(= {expr.name.lexeme} {expr.value.accept(self)})"
        
    def visit_function_expr(self, expr: Function) -> str:
        # Implementation for function expression printing
        param_str = ", ".join(param.lexeme for param in expr.params)
        return f"(def {expr.name.lexeme}({param_str}) ...)"
        
    def visit_end_expr(self, expr: End) -> str:
        return "(end)"
        
    def visit_peek_expr(self, expr: Peek) -> str:
        return f"(peek {expr.addr.accept(self)})"
        
    def visit_peek2_expr(self, expr: Peek2) -> str:
        return f"(peek2 {expr.addr.accept(self)})"
        
    def visit_poke_expr(self, expr: Poke) -> str:
        return f"(poke {expr.addr.accept(self)} {expr.value.accept(self)})"
        
    def visit_poke2_expr(self, expr: Poke2) -> str:
        return f"(poke2 {expr.addr.accept(self)} {expr.value.accept(self)})"

    def parenthesize(self, name: str, *exprs: Expr) -> str:
        return f"({name} {' '.join(expr.accept(self) for expr in exprs)})" 