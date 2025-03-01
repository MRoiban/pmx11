assembly_to_opcode = {
    "HALT": "0x00",
    "LOAD": {
        "R1": "0x01",
        "R2": "0x02",
        "R3": "0x03",
        "R4": "0x04",
        "R5": "0x05",
        "R6": "0x06",
        "R7": "0x07",
        "R8": "0x08",
    },
    "ADD": "0x09",
    "SUB": "0x0A",
    "PUSH": "0x0B",
    "POP": "0x0C",
    "EQUAL": "0x0D",
    "GTH": "0x0E",
    "LTH": "0x0F",
    "DUP": "0x10",
    "POT": "0x11",
    "OVR": "0x12",
    "INC": "0x13",
    "DCR": "0x14",
    "MUL": "0x15",
    "DIV": "0x16",
    "SQRT": "0x17",
    "POW": "0x18",
    "ABS": "0x19",
    "MOV": "0x20",
    "STR": "0xAA",
    "PEEK2": "0xAF",
    "POKE2": "0xBF",
    "SWAP": "0xCF",
    "GOTO": "0xDE",
    "JMP": "0xDF",
    "JNZ": "0xEF",
    "RMV": "0xEE",
    "RPC": "0xFE",
    "RET": "0xFF",
}

char_to_hex = {
    " ": "0x00",
    "A": "0x01",
    "B": "0x02",
    "C": "0x03",
    "D": "0x04",
    "E": "0x05",
    "F": "0x06",
    "G": "0x07",
    "H": "0x08",
    "I": "0x09",
    "J": "0x0A",
    "K": "0x0B",
    "L": "0x0C",
    "M": "0x0D",
    "N": "0x0E",
    "O": "0x0F",
    "P": "0x10",
    "Q": "0x11",
    "R": "0x12",
    "S": "0x13",
    "T": "0x14",
    "U": "0x15",
    "V": "0x17",
    "W": "0x18",
    "X": "0x19",
    "Y": "0x1A",
    "Z": "0x1B",
    "1": "0x1C",
    "2": "0x1D",
    "3": "0x1E",
    "4": "0x1F",
    "5": "0x20",
    "6": "0x21",
    "7": "0x22",
    "8": "0x23",
    "9": "0x24",
    "0": "0x25",
}

def assembler_START(lines, display_addr):
    program = []
    variables = {}
    instruction_count = 0
    
    for line in lines:
        # Skip empty lines and get content before comments
        line = line.split(";", 1)[0].strip()
        if not line or line.startswith("//"): 
            continue

        tokens = line.split()
        if not tokens:
            continue

        instruction = tokens[0]
        
        # Handle special directives
        if instruction in ["#START", "#END"]:
            if instruction == "#END":
                return program, variables, instruction_count, display_addr
            continue

        # Process regular instructions
        _, _, display_addr = parse_instructions(display_addr, program, variables, tokens, instruction)
        instruction_count += 1

    return program, variables, instruction_count, display_addr

# def assembler_STARTS(lines, display_addr):
#     program = []
#     variables = {}
#     count = 0
#     for line in lines:
#         if len(line.strip()) == 0:  # Skip empty lines
#             continue

#         # Remove inline comments starting with ';'
#         line = line.split(";", 1)[0].strip()

#         # Split by spaces for parsing
#         parts = line.strip().split()
#         if not parts:
#             continue  # Skip if line becomes empty after comment removal

#         instruction = parts[0]

#         if instruction.startswith("//"):  # Skip full-line comments
#             continue

#         # Handle specific instructions
#         if instruction == "#START":
#             continue
#         if instruction == "#END":
#             return program, variables, count, display_addr

#         _, _, display_addr = parse_instructions(
#             display_addr, program, variables, parts, instruction
#         )
#         count += 1

#     return program, variables, count, display_addr

def assemble_parser(input_string):
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


def assembler(asm_file, variables, pc=0):
    display_addr = 0x2AD00
    count = 0
    with open(asm_file, "r") as file:
        lines = file.readlines()

    program = []
    end_program = []
    assembled = None

    for line in lines:
        # Remove inline comments starting with ';'
        line = line.split(";", 1)[0].strip()

        if len(line) == 0:  # Skip empty or commented lines
            continue

        parts = line.split()
        instruction = parts[0]

        if instruction.startswith("//"):  # Skip full-line comments
            continue

        if instruction == "#START":
            if count is None:
                count = 0
            assembled = assembler_START(lines, display_addr)
            end_program += assembled[0]
            variables = {**variables, **assembled[1]}
            display_addr = assembled[3]
        if assembled is not None and count is not None and count <= assembled[2]:
            count += 1
            continue
        else:
            count = None
        if instruction == "#END":
            continue

        _, _, display_addr = parse_instructions(
            display_addr, program, variables, parts, instruction, pc
        )

    program += end_program
    return program, variables


def parse_instructions(display_addr, program, variables, parts, instruction, pc=0):
    if instruction == "#END":
        return program, variables

    if instruction in [
        "LOAD",
        "MOV",
        "PUSH",
        "POP",
        "SWAP",
        "POKE2",
        "POT",
        "PEEK2",
        "VAR",
        "LABEL",
        "CALL",
        "WCHR",
        "WSTR",
        "IMPORT",
        "JMP",
    ]:
        if instruction == "LOAD":
            load_instruction(program, variables, parts, instruction)
        elif instruction == "VAR":
            var_instruction(variables, parts)
        elif instruction == "CALL":
            call_instruction(program, parts)
        elif instruction == "IMPORT":
            variables = import_instruction(program, variables, parts)
        elif instruction == "LABEL":
            label_instruction(program, variables, parts, pc)
        elif instruction == "WCHR":
            display_addr = wchr_instruction(display_addr, program, parts)
        elif instruction == "WSTR":
            display_addr = wstr_instruction(display_addr, program, parts)
        elif instruction in ["PUSH", "POP", "POKE2", "POT", "PEEK2", "JMP"]:
            unary_instruction(program, variables, parts, instruction)
        elif instruction in ["SWAP"]:
            swap_instruction(program, parts, instruction)
        elif instruction == "MOV":
            mov(program, parts, instruction, variables)
    else:
        if instruction in assembly_to_opcode:
            program.append(assembly_to_opcode[instruction])
    return program, variables, display_addr


def swap_instruction(program, parts, instruction):
    reg1 = parts[1].replace("R", "")
    reg2 = parts[2].replace("R", "")
    program.append(assembly_to_opcode[instruction])
    program.append(reg1)
    program.append(reg2)


def unary_instruction(program, variables, parts, instruction):
    reg = parts[1]
    reg_num = reg

    if reg not in variables:
        reg_num = reg.replace("R", "").replace("#", "")
    elif not ("@" in reg or "0x" in reg):
        reg_num = variables[reg]

    program.extend([assembly_to_opcode[instruction], reg_num])


def wchr_instruction(display_addr, program, parts):
    char = parts[1].strip(",")
    if char == "":
        return ...

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
    string, x, y, scale, color = (parts[1], 
                                  int(parts[2].strip('#,').strip()), 
                                  parts[3], 
                                  int(parts[4].strip('#,').strip()), 
                                  parts[5])
    
    for i, char in enumerate(string):
        offset = (scale * i) + ((i * scale) / 2 if i > 0 else 0)
        str_x = f"#{int(x + offset)}"
        display_addr = wchr_instruction(display_addr, program, [None, char, str_x, y, f"#{scale}", color])
    
    return display_addr


def add_to_display_mem(display_addr, program, item):
    program.append(assembly_to_opcode["POT"])
    program.append(item)
    program.append(assembly_to_opcode["POT"])
    program.append(display_addr)
    display_addr += 1
    program.append(assembly_to_opcode["STR"])
    return display_addr


def label_instruction(program, variables, parts, pc):
    name = parts[1]
    variables[name] = {"type": "constant", "value": len(program) + pc, "location": None}


def import_instruction(program, variables, parts):
    file = parts[1].strip('"')
    assembled = assembler(file, variables, len(program))
    program += assembled[0]
    variables = {**variables, **assembled[1]}
    return variables


def goto_instruction(program, parts, instruction):
    operand = parts[1]
    program.append(assembly_to_opcode[instruction])
    program.append(str(operand))


def call_instruction(program, parts):
    reg = parts[1]
    program.append("0x11")
    program.append(reg)
    program.append("0xDE")  # ? doesnt GOTO need a param?


def var_instruction(variables, parts):
    """
    Parse the VAR instruction to ensure all variables include a 'location' key.
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
    opcode = assembly_to_opcode[instruction][parts[1].replace(",", "")]
    if not (parts[2] in variables) and not ("0x" in parts[2]):
        operand = int(parts[2].replace("#", ""))
    else:
        ost = []
        vst = []
        size = len(parts)
        operand = variables[parts[2]] if not ("0x" in parts[2]) else parts[2]
        # TODO: this snippet was used for basic arithmetics with vars when using load, it's ugly asf
        # if size > 3:
        #     for i in range(1,size-2):
        #         if '-' in parts[2+i]:
        #             ost.append('-')
        #         elif '+' in parts[2+i]:
        #             ost.append('+')
        #         else:
        #             vst.append(int(parts[2+i]))

        #     ost_len = len(ost)
        #     for i in range(ost_len):
        #         a = vst.pop()
        #         op = ost.pop()
        #         if '-' in op:
        #             operand -= a
        #         elif '+' in op:
        #             operand += a
    program.append(opcode)
    program.append(str(operand))


def mov(program, parts, instruction, variables):
    opcode = assembly_to_opcode[instruction]
    
    def parse_operand(op, allow_immediate=True):
        if op in variables:
            value = variables[op].get("location") or variables[op]["value"]
            return 2, value
        elif op.startswith("R"):
            return 0, op.replace("R", "")
        elif op.startswith("@"):
            return 1, op.replace("@", "")
        elif op.startswith("#") and allow_immediate:
            return 3, int(op.replace("#", ""))
        raise ValueError(f"Invalid operand: {op}")

    src_flag, src_value = parse_operand(parts[1])
    dest_flag, dest_value = parse_operand(parts[2], allow_immediate=False)
    
    program.extend([opcode, src_flag, dest_flag, src_value, dest_value])


def replace_variables(program, variables):
    # print(variables)
    for i in range(len(program)):
        if "@" in str(program[i]):
            program[i] = str(variables[program[i]]["value"])

        elif program[i] in variables:
            program[i] = str(variables[program[i]]["value"])

        else:
            program[i] = str(program[i])
    return program


def write_rom_file(rom_file, program, variables):
    """
    Write the assembled program and variables to the output ROM file.
    """
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
        for instruction in program:
            file.write(f"{instruction}\n")


def assemble(asm_file, rom_file):
    variables = {}
    program, variables = assembler(asm_file, variables)
    program = replace_variables(program, variables)
    write_rom_file(rom_file, program, variables)


if __name__ == "__main__":
    assemble("program.asm", "./build/program.rom")
