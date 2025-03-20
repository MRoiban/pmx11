"""
Utility functions for the PMX assembler.
"""

def parse_arithmetic_expression(expr, variables):
    """
    Parse arithmetic expressions in the source code.
    Returns the evaluated result.
    """
    if not isinstance(expr, str):
        return expr
        
    # Remove whitespace
    expr = expr.strip()
    
    # Skip if it's already processed or not an expression
    if not any(op in expr for op in ['+', '-', '*', '/']):
        # Handle basic numbers and variables
        if expr.startswith('#'):
            return int(expr[1:])
        elif expr in variables:
            if isinstance(variables[expr], dict):
                return variables[expr].get("value") or variables[expr].get("location")
            return variables[expr]
        elif expr.startswith('0x'):
            try:
                return int(expr, 16)
            except ValueError:
                return expr
        elif expr.isdigit():
            return int(expr)
        else:
            # Not a parseable expression
            return expr
    
    # Handle arithmetic operations
    if '+' in expr:
        parts = [p for p in expr.split('+') if p]
        return sum(parse_arithmetic_expression(part, variables) for part in parts)
    elif '-' in expr:
        parts = [p for p in expr.split('-') if p]
        if len(parts) == 1:  # Negative number
            return -parse_arithmetic_expression(parts[0], variables)
        result = parse_arithmetic_expression(parts[0], variables)
        for part in parts[1:]:
            result -= parse_arithmetic_expression(part, variables)
        return result
    elif '*' in expr:
        parts = [p for p in expr.split('*') if p]
        result = 1
        for part in parts:
            result *= parse_arithmetic_expression(part, variables)
        return result
    elif '/' in expr:
        parts = [p for p in expr.split('/') if p]
        if len(parts) < 2:
            return expr  # Not a valid division expression
        result = parse_arithmetic_expression(parts[0], variables)
        for part in parts[1:]:
            parsed_part = parse_arithmetic_expression(part, variables)
            if parsed_part == 0:  # Avoid division by zero
                return expr
            result //= parsed_part
        return result
    
    # If we can't parse it, return the original expression
    return expr


def assemble_parser(input_string):
    """Parse input string for tokens."""
    result = ''
    current_token = ''
    
    for char in input_string:
        current_token += char
        if 'ox01' in current_token:
            result += 'var'
            current_token = ''
        elif current_token.strip() and not any(x in current_token for x in 'ox01'):
            current_token = ''
            
    return result.strip() 