#!/usr/bin/env python
import pytest
from pmxlang.lexer import Token, TokenType
from pmxlang.parser import (
    Parser, Binary, Literal, AstPrinter, Expr,
    Grouping, Unary, Variable, Assign
)

class TestParser:
    def test_ast_printer(self):
        # Test that our AST printer works correctly
        expr = Binary(
            Literal(1), 
            Token(TokenType.PLUS, "+", None, 1), 
            Binary(
                Literal(2), 
                Token(TokenType.STAR, "*", None, 1), 
                Literal(3)
            )
        )
        
        printer = AstPrinter()
        result = printer.print(expr)
        assert result == "(+ 1 (* 2 3))"
    
    def test_literal_expr(self):
        # Test literal expressions
        expr = Literal(42)
        printer = AstPrinter()
        result = printer.print(expr)
        assert result == "42"
        
        expr = Literal(None)
        result = printer.print(expr)
        assert result == "nil"
    
    def test_grouping_expr(self):
        # Test grouping expressions
        expr = Grouping(Literal(42))
        printer = AstPrinter()
        result = printer.print(expr)
        assert result == "(group 42)"
    
    def test_unary_expr(self):
        # Test unary expressions
        expr = Unary(
            Token(TokenType.MINUS, "-", None, 1),
            Literal(42)
        )
        printer = AstPrinter()
        result = printer.print(expr)
        assert result == "(- 42)"
    
    def test_variable_expr(self):
        # Test variable expressions
        expr = Variable(Token(TokenType.IDENTIFIER, "foo", None, 1))
        printer = AstPrinter()
        result = printer.print(expr)
        assert result == "foo"
    
    def test_assign_expr(self):
        # Test assignment expressions
        expr = Assign(
            Token(TokenType.IDENTIFIER, "foo", None, 1),
            Literal(42)
        )
        printer = AstPrinter()
        result = printer.print(expr)
        assert result == "(= foo 42)"

if __name__ == "__main__":
    pytest.main(["-v", __file__]) 