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
    
    # Write the assembly code directly without post-processing
    with open("build/program.asm", "w") as f:
        f.write("\n".join(asm))

if __name__ == "__main__":
#    argparse filename
    import argparse
    parser = argparse.ArgumentParser(description="PMX Compiler")
    parser.add_argument("filename", type=str, help="Input PMX file")
    args = parser.parse_args()
    with open(args.filename, 'r') as file:
        src = file.read()
        run(src)
    
