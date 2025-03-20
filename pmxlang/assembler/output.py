"""
Functions for generating output from the assembler.
"""

from pmxlang.assembler.utils import parse_arithmetic_expression


def replace_variables(program, variables):
    """Replace variable references with their actual values in the program."""
    for i in range(len(program)):
        item = str(program[i])
        
        # Check if this is an arithmetic expression (contains +, -, *, /)
        if any(op in item for op in ['+', '-', '*', '/']):
            try:
                program[i] = str(parse_arithmetic_expression(item, variables))
                continue
            except ValueError:
                pass  # Not a valid expression, continue with normal processing
        
        # Normal variable replacement
        if "@" in item:
            program[i] = str(variables[item]["value"])
        elif item in variables:
            program[i] = str(variables[item]["value"])
        else:
            program[i] = str(item)
            
    return program


def write_rom_file(rom_file, program, variables):
    """Write the assembled program and variables to the output ROM file."""
    with open(rom_file, "w") as file:
        # Write variables section
        file.write("VARIABLES\n")
        for name, data in variables.items():
            if data["type"] == "constant":
                file.write(f"{name} CONSTANT {data['value']}\n")
            elif data["type"] == "runtime_register":
                file.write(f"{name} REGISTER {data['location']}\n")
            elif data["type"] == "runtime_memory":
                file.write(f"{name} MEMORY {hex(data['location'])}\n")

        # Write program instructions
        file.write("\nPROGRAM\n")
        
        # Track if the next item is a register for PUSH/POP
        is_register_for_push_pop = False
        last_opcode = None
        
        for i, instruction in enumerate(program):
            # Check if this is an opcode for PUSH or POP (0x0B or 0x0C)
            if instruction == "0x0B" or instruction == "0x0C":
                last_opcode = instruction
                is_register_for_push_pop = True
                file.write(f"{instruction}\n")
            # If this is a register for PUSH/POP, handle it specially
            elif is_register_for_push_pop:
                # If it starts with 'R', extract just the number
                if str(instruction).startswith('R'):
                    reg_num = str(instruction).replace('R', '')
                    file.write(f"{reg_num}\n")
                else:
                    file.write(f"{instruction}\n")
                is_register_for_push_pop = False
            else:
                file.write(f"{instruction}\n") 