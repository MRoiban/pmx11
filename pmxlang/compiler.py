from dataclasses import dataclass
from typing import List, Dict
from .parser.parser import Parser
from .parser.expr import (
    Expr,
    ExprVisitor,
    Binary,
    Grouping,
    Literal,
    Unary,
    Variable,
    Assign,
    End,
    Poke,
    Peek,
    Poke2,
    Peek2
)
from .parser.stmt import (
    Stmt,
    StmtVisitor,
    Expression,
    For,
    If,
    While,
    Break,
    Print,
    Screen,
    Cls,
    Line,
    Rect,
    Circle,
    Pixel,
    RectFill,
    Sprint,
    Mouse,
    Function,
    If,
    While,
    Break,
    Memcpy,
    Memmov,
    Button
)
from .lexer import TokenType, Token
from .scanner import Scanner
from .parser.utils import string_to_hex_list

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
        self.loop_end_labels = []  # Stack of loop end labels for break statements

    def compile(self, statements: List[Stmt]) -> List[str]:
        """Compile a list of statements into PMX assembly instructions."""
        for stmt in statements:
            stmt.accept(self)
        return self.instructions

    def compile_file(self, path: str) -> List[str]:
        with open(path, "r") as f:
            # scan then parse
            tokens = Scanner(f.read()).scanTokens()
            statements = Parser(tokens).parse()
        return self.compile(statements)

    def get_next_label(self, prefix: str) -> str:
        """Generate a unique label for control flow."""
        label = f"{prefix}_{self.label_counter}"
        self.label_counter += 1
        return label

    def visit_button_stmt(self, stmt: Button) -> None:
        self.emit(f"POT {stmt.type}")
        self.emit(f"POKE2 0x100")
        x = stmt.x.accept(self)
        self.emit(f"POKE2 0x101")
        y = stmt.y.accept(self)
        self.emit(f"POKE2 0x102")
        w = stmt.w.accept(self)
        self.emit(f"POKE2 0x103")
        h = stmt.h.accept(self)
        self.emit(f"POKE2 0x104")
        function_addr = stmt.function_addr.accept(self)
        self.emit(f"POKE2 0x105")
        id = stmt.id.accept(self)
        self.emit(f"POKE2 0x106")
        order = 0x107
        hex_list = string_to_hex_list(stmt.text.value)
        size = len(hex_list)
        self.emit(f"POT {size}")
        self.emit(f"POKE2 0x{order:x}")
        order += 1
        for hex in hex_list:
            self.emit(f"POT {hex}")
            self.emit(f"POKE2 0x{order:x}")
            order += 1
        self.emit(f"POT 1")
        self.emit(f"POKE2 0x50")

    def visit_memcpy_stmt(self, stmt: Memcpy) -> None:
        src = stmt.src.value
        dest = stmt.dst.value
        size = stmt.size.value
        self.emit(f"CPY {src}, {dest}, {size}")

    def visit_memmov_stmt(self, stmt: Memmov) -> None:
        src = stmt.src.value
        dest = stmt.dst.value
        size = stmt.size.value
        self.emit(f"MOV {src}, {dest}, {size}")

    def visit_break_stmt(self, stmt: Break) -> None:
        # Generate code for the break statement to exit the current loop
        if not self.loop_end_labels:
            raise SyntaxError("Break statement outside of loop")

        # Jump to the end of the current loop
        end_label = self.loop_end_labels[-1]  # Get the most recent loop end label
        self.emit(f"JMP {end_label}")

    def visit_while_stmt(self, stmt: While) -> None:
        # Generate code for the while statement
        start_label = self.get_next_label("@while_start")
        end_label = self.get_next_label("@while_end")

        # Push the end label onto the stack for break statements
        self.loop_end_labels.append(end_label)

        # Emit start label
        self.emit(f"LABEL {start_label}")

        # Evaluate condition
        self.need_push = False  # Result doesn't need to be on stack
        stmt.condition.accept(self)
        self.emit(f"NOT")

        # Jump to end if condition is false (JNZ = Jump if Not Zero)
        self.emit(f"JNZ {end_label}")

        # Execute body if condition is true
        for body_stmt in stmt.body:
            body_stmt.accept(self)

        # Jump back to condition check
        self.emit(f"JMP {start_label}")

        # End of while block
        self.emit(f"LABEL {end_label}")

        # Pop the label when we're done with this loop
        self.loop_end_labels.pop()

    def visit_function_stmt(self, stmt: Function) -> None:
        # Generate code for the function
        self.emit(f"LABEL @{stmt.name.lexeme}")
        for param in stmt.params:
            self.emit(f"PEEK {param.name.lexeme}")

    # Statement visitor methods
    def visit_expression_stmt(self, stmt: Expression) -> None:
        # Generate code for the expression
        self.need_push = False  # Result doesn't need to be on stack
        stmt.expression.accept(self)

    def visit_if_stmt(self, stmt: If) -> None:
        # Generate code for the if statement
        end_label = self.get_next_label("@if_end")
        else_label = self.get_next_label("@else") if stmt.else_body else end_label

        # Evaluate condition
        self.need_push = False  # Result doesn't need to be on stack
        stmt.condition.accept(self)
        # self.emit(f"NOT")

        # Jump to else (or end if no else) if condition is false (JNZ = Jump if Not Zero)
        self.emit(f"JNZ {else_label}")

        # Execute body if condition is true
        for body_stmt in stmt.body:
            body_stmt.accept(self)
            
        # If we have an else clause, jump to end after executing the if body
        if stmt.else_body:
            self.emit(f"JMP {end_label}")
            self.emit(f"LABEL {else_label}")
            
            # Execute else body
            for else_stmt in stmt.else_body:
                else_stmt.accept(self)

        # End of if-else block
        self.emit(f"LABEL {end_label}")

    def visit_print_stmt(self, stmt):
        stmt.body.accept(self)
        self.emit(f"POKE2 0x06")
        self.emit(f"POT 1")
        self.emit(f"POKE2 0x02")
        self.emit(f"POT 0")
        self.emit(f"POKE2 0x02")

    def visit_import_stmt(self, stmt):
        # merge the file into the current file
        # the other file should also be compiled first
        self.compile_file(stmt.path.lexeme.replace('"', ''))

    def visit_screen_stmt(self, stmt):
        stmt.width.accept(self)
        self.emit(f"POKE2 0x1B")
        stmt.height.accept(self)
        self.emit(f"POKE2 0x1C")
        stmt.background.accept(self)
        self.emit(f"POKE2 0x1D")
        stmt.borderless.accept(self)
        self.emit(f"POKE2 0x1E")
        stmt.power.accept(self)
        self.emit(f"POKE2 0x10")

    def visit_cls_stmt(self, stmt):
        stmt.body.accept(self)
        self.emit(f"POKE2 0x11")

    def visit_line_stmt(self, stmt):
        stmt.x1.accept(self)
        self.emit(f"POKE2 0x100")
        stmt.y1.accept(self)
        self.emit(f"POKE2 0x101")
        stmt.x2.accept(self)
        self.emit(f"POKE2 0x102")
        stmt.y2.accept(self)
        self.emit(f"POKE2 0x103")
        stmt.scale.accept(self)
        self.emit(f"POKE2 0x104")
        stmt.color.accept(self)
        self.emit(f"POKE2 0x105")
        self.emit(f"POT 1")
        self.emit(f"POKE2 0x15")

    def visit_rect_stmt(self, stmt):
        stmt.x.accept(self)
        self.emit(f"POKE2 0x100")
        stmt.y.accept(self)
        self.emit(f"POKE2 0x101")
        stmt.w.accept(self)
        self.emit(f"POKE2 0x102")
        stmt.h.accept(self)
        self.emit(f"POKE2 0x103")
        stmt.scale.accept(self)
        self.emit(f"POKE2 0x104")
        stmt.color.accept(self)
        self.emit(f"POKE2 0x105")
        self.emit(f"POT 1")
        self.emit(f"POKE2 0x16")

    def visit_rectfill_stmt(self, stmt):
        stmt.x.accept(self)
        self.emit(f"POKE2 0x100")
        stmt.y.accept(self)
        self.emit(f"POKE2 0x101")
        stmt.w.accept(self)
        self.emit(f"POKE2 0x102")
        stmt.h.accept(self)
        self.emit(f"POKE2 0x103")
        stmt.scale.accept(self)
        self.emit(f"POKE2 0x104")
        stmt.color.accept(self)
        self.emit(f"POKE2 0x105")
        self.emit(f"POT 1")
        self.emit(f"POKE2 0x17")

    def visit_poke_stmt(self, stmt):
        self.emit(f"POT {stmt.value.value}")
        self.emit(f"POKE {stmt.addr.value}")

    def visit_function_expr(self, expr: Function) -> None:
        # Generate code for the function call
        self.emit(f"CALL {expr.name.lexeme}")

    def visit_end_expr(self, expr: End) -> None:
        # Generate code for the end statement
        self.emit(f"HALT")

    def visit_poke2_stmt(self, stmt):
        stmt.value.accept(self)
        self.emit(f"POKE {stmt.addr.value}")



    def visit_sprint_stmt(self, stmt):
        stmt.string.accept(self)
        self.emit(f"POKE 0x100")
        stmt.x.accept(self)
        self.emit(f"POKE 0x101")
        stmt.y.accept(self)
        self.emit(f"POKE 0x102")
        stmt.scale.accept(self)
        self.emit(f"POKE 0x103")
        stmt.color.accept(self)
        self.emit(f"POKE 0x104")
        self.emit(f"POT 1")
        self.emit(f"POKE2 0x19")

    def visit_circle_stmt(self, stmt):
        stmt.body.accept(self)
        self.emit(f"POKE2 0x18")

    def visit_pixel_stmt(self, stmt):
        stmt.x.accept(self)
        self.emit(f"POKE 0x100")
        stmt.y.accept(self)
        self.emit(f"POKE 0x101")
        stmt.scale.accept(self)
        self.emit(f"POKE 0x102")
        stmt.color.accept(self)
        self.emit(f"POKE 0x103")
        self.emit(f"POT 1")
        self.emit(f"POKE2 0x14")

    def visit_for_stmt(self, stmt: For) -> None:
        # Generate labels for loop control
        start_label = self.get_next_label("@for_start")
        end_label = self.get_next_label("@for_end")

        # Push the end label onto the stack for break statements
        self.loop_end_labels.append(end_label)

        # 1. Initialize loop variable
        self.need_push = False
        stmt.init.accept(self)

        # 2. Start of loop
        self.emit(f"LABEL {start_label}")

        # 3. Check condition
        self.need_push = False
        stmt.condition.accept(self)
        self.emit(f"JNZ {end_label}")

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

        # Pop the label when we're done with this loop
        self.loop_end_labels.pop()

    def visit_peek2_expr(self, expr: Peek2) -> None:
        self.emit(f"PEEK2 {expr.addr.value}")

    def visit_binary_expr(self, expr: Binary) -> None:
        # Generate code for left operand - will push to stack
        old_push = self.need_push  # Save current push state
        self.need_push = True  # Left operand result needs to be on stack
        expr.left.accept(self)  # Generate code for left operand

        # Generate code for right operand - will push to stack
        self.need_push = True  # Right operand result needs to be on stack
        expr.right.accept(self)  # Generate code for right operand

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
                self.emit("GTH")  # Stack: pop 2, push comparison result
                self.emit("NOT")  # Stack: pop 2, push comparison result
            case TokenType.GREATER_EQUAL:
                self.emit("GTE")  # Stack: pop 2, push comparison result
            case TokenType.LESS:
                self.emit("LTH")
                self.emit("NOT")  # Stack: pop 2, push comparison result
            case TokenType.LESS_EQUAL:
                self.emit("LTE")  # Stack: pop 2, push comparison result
            case TokenType.EQUAL_EQUAL:
                self.emit("EQUAL")  # Stack: pop 2, push comparison result
            case TokenType.BANG_EQUAL:
                self.emit("EQUAL")  # Stack: pop 2, push comparison result
                self.emit("NOT")
        # Stack operations leave result on stack already
        # Restore previous push state
        self.need_push = old_push

    def visit_mouse_stmt(self, stmt: Mouse) -> None:
        stmt.body.accept(self)
        self.emit(f"POKE2 0x20")
        self.emit(f"POT 1")
        self.emit(f"POKE2 0x13")

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
        old_push = self.need_push  # Save current push state
        self.need_push = False  # Don't push right operand result yet
        expr.right.accept(self)  # Generate code for right operand

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

    def visit_peek_expr(self, expr: Peek) -> None:
        # Check if the address is a literal value (direct addressing)
        if isinstance(expr.addr, Literal):
            # For literal addresses, we can use them directly with PEEK
            self.emit(f"PEEK {expr.addr.value}")
            
            # Save old push state and restore it at the end
            old_push = self.need_push
            
            # If result needs to be on stack for a higher-level expression
            if old_push:
                self.emit("PUSH R1")
                
            # Restore previous push state
            self.need_push = old_push
        else:
            # For computed addresses, we need to evaluate the expression first
            old_push = self.need_push
            self.need_push = False
            expr.addr.accept(self)  # Address is now in R1
            
            # Need a temporary variable to store the computed address
            temp_addr = "0x8000"  # Use a safe temporary address
            
            # Store the computed address in the temporary location
            self.emit(f"POKE {temp_addr}")
            
            # Now peek the memory at the address contained in our temp variable
            self.emit(f"PEEK {temp_addr}")
            
            # If needed, push result to stack
            if old_push:
                self.emit("PUSH R1")
            
            # Restore previous push state
            self.need_push = old_push
    
   
    def visit_poke_expr(self, expr: Poke) -> None:
        # Generate code for the value first
        old_push = self.need_push
        self.need_push = False
        expr.value.accept(self)  # Value in R1
        
        # Check if the address is a literal value (direct addressing)
        if isinstance(expr.addr, Literal):
            # For literal addresses, we can use them directly with POKE
            self.emit(f"POKE {expr.addr.value}")
        else:
            # For computed addresses, we need to evaluate the expression first
            expr.addr.accept(self)  # Address is now in R1
            
            # Need a temporary variable to store the computed address
            temp_addr = "0x8000"  # Use a safe temporary address
            
            # Store the computed address in the temporary location
            self.emit(f"POKE {temp_addr}")
            
            # Now PEEK the value back to set up for the next instruction
            self.emit(f"PEEK {temp_addr}")
            
            # Get the value we want to poke back on the stack
            self.emit("PUSH R1")  # Push address to stack
            
            # Now poke the memory at the computed address
            self.emit(f"POKE {temp_addr}")
        
        # The result of the expression is the value that was poked
        # It's already in R1, so just leave it there
        
        # If needed, push result to stack for a higher-level expression
        if old_push:
            self.emit("PUSH R1")
            
        # Restore previous push state
        self.need_push = old_push
    
    def visit_poke2_expr(self, expr: Poke2) -> None:
        # Generate code for the value first
        old_push = self.need_push
        self.need_push = False
        expr.value.accept(self)  # Value in R1
        self.emit("PUSH R1")  # Save value on stack
        
        # Check if the address is a literal value (direct addressing)
        if isinstance(expr.addr, Literal):
            # For literal addresses, we can use them directly with POKE2
            self.emit(f"POKE2 {expr.addr.value}")
        else:
            # For computed addresses, we need to evaluate the expression first
            expr.addr.accept(self)  # Address is now in R1
            
            # Need a temporary variable to store the computed address
            temp_addr = "0x8000"  # Use a safe temporary address
            
            # Store the computed address in the temporary location
            self.emit(f"POKE {temp_addr}")
            
            # Now PEEK the value back to set up for the next instruction
            self.emit(f"PEEK {temp_addr}")
            
            # Get the value we want to poke back on the stack
            self.emit("PUSH R1")  # Push address to stack
            
            # Now poke2 the device memory at the computed address
            self.emit(f"POKE2 {temp_addr}")
        
        # The result of the expression is the value that was poked
        # It's already in R1, so just leave it there
        
        # If needed, push result to stack for a higher-level expression
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
        if instruction.endswith(":"):
            self.instructions.append(f"{instruction}")
        else:
            self.instructions.append(f"{instruction}")
            self.current_address += 1  # Each instruction takes 1 word
