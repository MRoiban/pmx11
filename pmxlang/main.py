from pmxlang.scanner import Scanner
from pmxlang.parser import Parser, AstPrinter, Expression
from pmxlang.compiler import PMXCompiler

def run(source: str) -> None:
    # Stage 1: Lexical Analysis
    scanner = Scanner(source)
    tokens = scanner.scanTokens()
    
    # Stage 2: Parsing
    parser = Parser(tokens)
    statements = parser.parse()
    
    # Print AST for debugging (only for expressions, not all statements)
    printer = AstPrinter()
    print("Parsed", len(statements), "statements")
    for stmt in statements:
        if isinstance(stmt, Expression):
            print("AST:", printer.print(stmt.expression))
    
    # Stage 3: Compilation to PMX assembly
    compiler = PMXCompiler()
    asm = compiler.compile(statements)
    
    # Post-process assembly to fix POT instructions
    processed_asm = []
    for instruction in asm:
        # Fix POT instructions to include the required register operand
        if instruction.startswith('POT ') and 'R' not in instruction:
            # Replace 'POT value' with 'POT R1, value'
            value = instruction[4:].strip()
            instruction = f'POT R1, {value}'
        processed_asm.append(instruction)
    
    # Output the assembly code
    with open("build/program.asm", "w") as f:
        f.write("\n".join(processed_asm))

if __name__ == "__main__":
#    argparse filename
    import argparse
    parser = argparse.ArgumentParser(description="PMX Compiler")
    parser.add_argument("filename", type=str, help="Input PMX file")
    args = parser.parse_args()
    with open(args.filename, 'r') as file:
        src = file.read()
        run(src)
    
