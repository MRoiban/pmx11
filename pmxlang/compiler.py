from dataclasses import dataclass
from typing import List, Dict
from .parser import (
    Expr, ExprVisitor, Binary, Grouping, Literal, Unary, Variable, Assign,
    Stmt, StmtVisitor, Expression, For, Function, End
)
from .lexer import TokenType, Token

class PMXCompiler(ExprVisitor, StmtVisitor):
    def __init__(self):
        self.instructions = []
        self.var_address = 0x2000  # Start of variable section
        self.var_map = {}
        self.current_address = 0x0000  # Start of code section
        self.need_push = False  # Flag to track if we need to push result to stack
        self.label_counter = 0  # Counter for generating unique labels
        self.function_table = {}
        self.function_address = 0x3000
        
    def compile(self, statements: List[Stmt]) -> List[str]:
        """Compile a list of statements into PMX assembly instructions."""
        for stmt in statements:
            stmt.accept(self)
        self.emit(f'POT -1')
        self.emit(f'HALT')
        return self.instructions
        
    def get_next_label(self, prefix: str) -> str:
        """Generate a unique label for control flow."""
        label = f"{prefix}_{self.label_counter}"
        self.label_counter += 1
        return label
        

    def visit_function_stmt(self, stmt: Function) -> None:
        # Generate code for the function
        self.emit(f'LABEL @{stmt.name.lexeme}')
        for param in stmt.params:
            self.emit(f'PEEK {param.name.lexeme}')
            

    # Statement visitor methods
    def visit_expression_stmt(self, stmt: Expression) -> None:
        # Generate code for the expression
        self.need_push = False  # Result doesn't need to be on stack
        stmt.expression.accept(self)
    
    def visit_print_stmt(self, stmt):
        stmt.body.accept(self)
        self.emit(f'POKE2 0x06')
        self.emit(f'POT 1')
        self.emit(f'POKE2 0x02')
        self.emit(f'POT 0')
        self.emit(f'POKE2 0x02')
        
    def visit_screen_stmt(self, stmt):
        stmt.body.accept(self)
        self.emit(f'POKE2 0x10')

    def visit_cls_stmt(self, stmt):
        stmt.body.accept(self)
        self.emit(f'POKE2 0x12')
    
    def visit_line_stmt(self, stmt):
        stmt.x1.accept(self)
        self.emit(f'POKE 0x100')
        stmt.y1.accept(self)
        self.emit(f'POKE 0x101')
        stmt.x2.accept(self)
        self.emit(f'POKE 0x102')
        stmt.y2.accept(self)
        self.emit(f'POKE 0x103')
        stmt.scale.accept(self)
        self.emit(f'POKE 0x104')
        stmt.color.accept(self)
        self.emit(f'POKE 0x105')
        self.emit(f'POT 1')
        self.emit(f'POKE2 0x15')
    

    def visit_rect_stmt(self, stmt):
        stmt.x.accept(self)
        self.emit(f'POKE 0x100')
        stmt.y.accept(self)
        self.emit(f'POKE 0x101')
        stmt.w.accept(self)
        self.emit(f'POKE 0x102')
        stmt.h.accept(self)
        self.emit(f'POKE 0x103')
        stmt.scale.accept(self)
        self.emit(f'POKE 0x104')
        stmt.color.accept(self)
        self.emit(f'POKE 0x105')
        self.emit(f'POT 1')
        self.emit(f'POKE2 0x16')

    def visit_rectfill_stmt(self, stmt):
        stmt.x.accept(self)
        self.emit(f'POKE 0x100')
        stmt.y.accept(self)
        self.emit(f'POKE 0x101')
        stmt.w.accept(self)
        self.emit(f'POKE 0x102')
        stmt.h.accept(self)
        self.emit(f'POKE 0x103')
        stmt.scale.accept(self)
        self.emit(f'POKE 0x104')
        stmt.color.accept(self)
        self.emit(f'POKE 0x105')
        self.emit(f'POT 1')
        self.emit(f'POKE2 0x17')

    def visit_poke_stmt(self, stmt):
        stmt.value.accept(self)
        self.emit(f'POKE {stmt.addr.value}')
    
    def visit_function_expr(self, expr: Function) -> None:
        # Generate code for the function call
        self.emit(f'CALL {expr.name.lexeme}')

    def visit_end_expr(self, expr: End) -> None:
        # Generate code for the end statement
        self.emit(f'HALT')

    def visit_poke2_stmt(self, stmt):
        stmt.value.accept(self)
        self.emit(f'POKE {stmt.addr.value}')
    
    def visit_peek_stmt(self, stmt):
        self.emit(f'PEEK {stmt.addr.value}')

    def visit_peek2_stmt(self, stmt):
        self.emit(f'PEEK2 {stmt.addr.value}')

    def visit_sprint_stmt(self, stmt):
        stmt.string.accept(self)
        self.emit(f'POKE 0x100')
        stmt.x.accept(self)
        self.emit(f'POKE 0x101')
        stmt.y.accept(self)
        self.emit(f'POKE 0x102')
        stmt.scale.accept(self)
        self.emit(f'POKE 0x103')
        stmt.color.accept(self)
        self.emit(f'POKE 0x104')
        self.emit(f'POT 1')
        self.emit(f'POKE2 0x19')

    def visit_circle_stmt(self, stmt):
        stmt.body.accept(self)
        self.emit(f'POKE2 0x18')

    def visit_pixel_stmt(self, stmt):
        stmt.x.accept(self)
        self.emit(f'POKE 0x100')
        stmt.y.accept(self)
        self.emit(f'POKE 0x101')
        stmt.scale.accept(self)
        self.emit(f'POKE 0x102')
        stmt.color.accept(self)
        self.emit(f'POKE 0x103')
        self.emit(f'POT 1')
        self.emit(f'POKE2 0x14')

    def visit_for_stmt(self, stmt: For) -> None:
        # Generate labels for loop control
        start_label = self.get_next_label("@for_start")
        end_label = self.get_next_label("@for_end")
        
        # 1. Initialize loop variable
        self.need_push = False
        stmt.init.accept(self)
        
        # 2. Start of loop
        self.emit(f"LABEL {start_label}")
        
        # 3. Check condition
        self.need_push = False
        stmt.condition.accept(self)
        self.emit("JNZ {end_label}".format(end_label=end_label))  # Jump to end if condition false
        
        # 4. Execute loop body
        for body_stmt in stmt.body:
            body_stmt.accept(self)
        
        # 5. Execute increment/action
        self.need_push = False
        stmt.action.accept(self)
        
        # 6. Jump back to condition check
        self.emit(f"JMP {start_label}")
        
        # 7. End of loop
        self.emit(f"LABEL {end_label}")
        
    def visit_binary_expr(self, expr: Binary) -> None:
        # Generate code for left operand - will push to stack
        old_push = self.need_push  # Save current push state
        self.need_push = True      # Left operand result needs to be on stack
        expr.left.accept(self)     # Generate code for left operand
        
        # Generate code for right operand - will push to stack
        self.need_push = True      # Right operand result needs to be on stack 
        expr.right.accept(self)    # Generate code for right operand
        
        # Apply the stack operation (pops two values, pushes result)
        match expr.operator.type:
            case TokenType.PLUS: 
                self.emit("ADD")  # Stack: pop 2, push sum
            case TokenType.MINUS: 
                self.emit("SUB")  # Stack: pop 2, push difference
            case TokenType.STAR: 
                self.emit("MUL")  # Stack: pop 2, push product
            case TokenType.SLASH: 
                self.emit("DIV")  # Stack: pop 2, push quotient
            case TokenType.MODULO:
                self.emit("MOD")  # Stack: pop 2, push remainder
            case TokenType.GREATER:
                self.emit("GT")   # Stack: pop 2, push comparison result
            case TokenType.GREATER_EQUAL:
                self.emit("GTE")  # Stack: pop 2, push comparison result
            case TokenType.LESS:
                self.emit("LTH")
                self.emit("NOT")   # Stack: pop 2, push comparison result
            case TokenType.LESS_EQUAL:
                self.emit("LTE")  # Stack: pop 2, push comparison result
            case TokenType.EQUAL_EQUAL:
                self.emit("EQUAL")   # Stack: pop 2, push comparison result
            case TokenType.BANG_EQUAL:
                self.emit("EQUAL")  # Stack: pop 2, push comparison result
                self.emit("NOT")
        # Stack operations leave result on stack already
        # Restore previous push state
        self.need_push = old_push
    

    
    def visit_literal_expr(self, expr: Literal) -> None:
        # Load the literal value into R1
        if isinstance(expr.value, bool):
            value = 1 if expr.value else 0
        elif expr.value is None:
            value = 0
        else:
            value = expr.value
        self.emit(f"LOAD R1, {value}")
        self.need_push = True
        
        # If needed, push the value to the stack
        if self.need_push:
            self.emit("PUSH R1")
    
    def visit_grouping_expr(self, expr: Grouping) -> None:
        # Process the expression inside parentheses
        # Keep the same push state
        expr.expression.accept(self)
    
    def visit_unary_expr(self, expr: Unary) -> None:
        # We need the right operand but no push needed yet
        old_push = self.need_push     # Save current push state
        self.need_push = False        # Don't push right operand result yet
        expr.right.accept(self)       # Generate code for right operand
        
        # Apply unary operation
        if expr.operator.type == TokenType.MINUS:
            self.emit("NEG R1")
        elif expr.operator.type == TokenType.BANG:
            self.emit("NOT R1")
            
        # If needed, push the result
        if old_push:
            self.emit("PUSH R1")
            
        # Restore previous push state
        self.need_push = old_push
        
    def visit_variable_expr(self, expr: Variable) -> None:
        # Get variable name
        var_name = expr.name.lexeme
        
        # If variable doesn't exist, create it
        if var_name not in self.var_map:
            self.var_map[var_name] = self.var_address
            self.var_address += 1
            
        # Load variable value into R1
        self.emit(f"PEEK {self.var_map[var_name]}")
        self.need_push = False
        # If needed, push to stack
        if self.need_push:
            self.emit("PUSH R1")
            
    def visit_assign_expr(self, expr: Assign) -> None:
        # Generate code for the value
        old_push = self.need_push
        self.need_push = False
        expr.value.accept(self)  # Result in R1
        
        # Get variable name
        var_name = expr.name.lexeme
        
        # If variable doesn't exist, create it
        if var_name not in self.var_map:
            self.var_map[var_name] = self.var_address
            self.var_address += 1
            
        # Store value in variable
        self.emit(f"POKE {self.var_map[var_name]}")
        
        # If needed, push result to stack (value is already in R1)
        if old_push:
            self.emit("PUSH R1")
            
        # Restore previous push state
        self.need_push = old_push
            
    def emit(self, instruction: str) -> None:
        """Add an instruction to the output and increment the address counter."""
        # If it's a label, don't increment the address counter
        if instruction.endswith(':'):
            self.instructions.append(f"{instruction}")
        else:
            self.instructions.append(f"{instruction}")
            self.current_address += 1  # Each instruction takes 1 word
