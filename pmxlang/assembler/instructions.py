"""
Functions for handling specific assembly instructions.
"""

from pmxlang.assembler.constants import assembly_to_opcode, char_to_hex
from pmxlang.assembler.utils import parse_arithmetic_expression


def alloc_instruction(program, parts, instruction, variables):
    """Process ALLOC instruction."""
    size = parse_arithmetic_expression(parts[1], variables)
    program.append(assembly_to_opcode[instruction])
    program.append(str(size))


def free_instruction(program, parts, instruction, variables):
    """Process FREE instruction."""
    addr = parse_arithmetic_expression(parts[1], variables)
    program.append(assembly_to_opcode[instruction])
    program.append(str(addr))


def swap_instruction(program, parts, instruction):
    """Process SWAP instruction."""
    reg1 = parts[1].replace("R", "")
    reg2 = parts[2].replace("R", "")
    program.append(assembly_to_opcode[instruction])
    program.append(reg1)
    program.append(reg2)


def unary_instruction(program, variables, parts, instruction):
    """Process instructions that take a single operand."""
    reg = parts[1]
    
    # Parse the operand as an arithmetic expression
    try:
        reg_num = parse_arithmetic_expression(reg, variables)
    except ValueError:
        # For backward compatibility if not an expression
        reg_num = reg
        if reg not in variables:
            # Handle register references by removing the 'R' prefix
            if instruction in ["PUSH", "POP"] and reg.startswith('R'):
                reg_num = reg.replace("R", "")
            else:
                reg_num = reg.replace("R", "").replace("#", "")
        elif not ("@" in reg or "0x" in reg):
            reg_num = variables[reg]
    
    program.extend([assembly_to_opcode[instruction], str(reg_num)])


def wchr_instruction(display_addr, program, parts):
    """Process WCHR instruction for character display."""
    char = parts[1].strip(",")
    if char == "":
        return display_addr

    char_hex = char_to_hex[char]
    params = []
    flags = []

    for i, part in enumerate(parts[2:6], 2):
        is_register = not any(x in part for x in ['#', '$', '0x'])
        value = part.replace('R', '').replace('#', '')
        
        if i == 5:  # Handle color parameter separately
            flags.append(0 if '0x' in part else 1)
        else:
            flags.append(1 if is_register else 0)
        params.append(value)

    # Add all values to display memory
    display_addr = add_to_display_mem(display_addr, program, char_hex)
    for param in params:
        display_addr = add_to_display_mem(display_addr, program, param)
    for flag in flags:
        display_addr = add_to_display_mem(display_addr, program, flag)
    display_addr = add_to_display_mem(display_addr, program, 1)

    return display_addr


def wstr_instruction(display_addr, program, parts):
    """Process WSTR instruction for string display."""
    print(parts)
    string, x, y, scale, color = (
        parts[1], 
        int(parts[2].strip('#,').strip()), 
        parts[3], 
        int(parts[4].strip('#,').strip()), 
        parts[5]
    )
    
    for i, char in enumerate(string):
        offset = (scale * i) + ((i * scale) / 2 if i > 0 else 0)
        str_x = f"#{int(x + offset)}"
        display_addr = wchr_instruction(display_addr, program, [None, char, str_x, y, f"#{scale}", color])
    
    return display_addr


def add_to_display_mem(display_addr, program, item):
    """Add an item to display memory at the specified address."""
    program.append(assembly_to_opcode["POT"])
    program.append(item)
    program.append(assembly_to_opcode["POT"])
    program.append(display_addr)
    display_addr += 1
    program.append(assembly_to_opcode["STR"])
    return display_addr


def label_instruction(program, variables, parts, pc):
    """Process LABEL instruction to define a label at the current position."""
    name = parts[1]
    variables[name] = {"type": "constant", "value": len(program) + pc, "location": None}


def import_instruction(program, variables, parts):
    """Process IMPORT instruction to include another assembly file."""
    from pmxlang.assembler.core import assembler  # Import here to avoid circular imports
    file = parts[1].strip('"')
    assembled = assembler(file, variables, len(program))
    program += assembled[0]
    variables = {**variables, **assembled[1]}
    return variables


def goto_instruction(program, parts, instruction):
    """Process GOTO instruction for jumps."""
    operand = parts[1]
    program.append(assembly_to_opcode[instruction])
    # program.append(str(operand))


def call_instruction(program, parts):
    """Process CALL instruction for subroutine calls."""
    reg = parts[1]
    program.append("0x11")  # POT
    program.append(reg) 
    program.append("0xDE")  # GOTO


def jnz_instruction(program, parts):
    """Process JNZ instruction for conditional jumps."""
    reg = parts[1]
    program.append("0x11")  # POT
    program.append(reg) 
    program.append("0xEF")  # JNZ


def jz_instruction(program, parts):
    """Process JZ instruction for conditional jumps."""
    reg = parts[1]
    program.append("0x11")  # POT
    program.append(reg) 
    program.append("0xF0")  # JZ


def var_instruction(variables, parts):
    """
    Parse the VAR instruction to define variables.
    Ensures all variables include a 'location' key.
    """
    name = parts[1]
    value = parts[2]

    if value.startswith("#"):  # Constant value
        variables[name] = {
            "type": "constant",
            "value": int(value.replace("#", "")),
            "location": None,
        }
    elif value.startswith("R"):  # Register
        variables[name] = {
            "type": "register",
            "location": int(value.replace("R", "")),
            "value": None,
        }
    elif value.startswith("@"):  # Memory address
        variables[name] = {
            "type": "memory",
            "location": int(value.replace("@", ""), 16),
            "value": None,
        }
    else:
        raise ValueError(f"Invalid variable declaration: {value}")


def load_instruction(program, variables, parts, instruction):
    """Process LOAD instruction to load values into registers."""
    opcode = assembly_to_opcode[instruction][parts[1].replace(",", "")]
    operand = parse_arithmetic_expression(parts[2], variables)
    program.append(opcode)
    program.append(str(operand))


def memory_instruction(program, parts, instruction, variables):
    """Process MOV instruction to move data between registers or memory."""
    opcode = assembly_to_opcode[instruction]
    src_addr = parse_arithmetic_expression(parts[1], variables)
    dst_addr = parse_arithmetic_expression(parts[2], variables)
    size = parse_arithmetic_expression(parts[3], variables)
    program.extend([opcode, src_addr, dst_addr, size]) 
