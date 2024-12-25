from icecream import ic
assembly_to_opcode = {
    "HALT": "0x00",
    "LOAD": {"R1": "0x01", "R2": "0x02", "R3": "0x03", "R4": "0x04","R5": "0x05","R6": "0x06","R7": "0x07","R8": "0x08"},
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
    "MOV": "0x20",
    "STR": '0xAA',
    "DVO": "0xAF",
    "DVW": "0xBF",
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
    "0": "0x25"
}

def assembler_START(lines, display_addr):
    program = []
    variables = {}
    count = 0
    for line in lines:
        if len(line.strip()) == 0:  # Skip empty lines
            continue
        
        # Remove inline comments starting with ';'
        line = line.split(';', 1)[0].strip()
        
        # Split by spaces for parsing
        parts = line.strip().split()
        if not parts:
            continue  # Skip if line becomes empty after comment removal
        
        instruction = parts[0]
        
        if instruction.startswith("//"):  # Skip full-line comments
            continue
        
        # Handle specific instructions
        if instruction == "#START":
            continue
        if instruction == "#END":
            return program, variables, count, display_addr
        
        _, _, display_addr = parse_instructions(display_addr, program, variables, parts, instruction)
        count += 1
    
    return program, variables, count, display_addr

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
        line = line.split(';', 1)[0].strip()
        
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
        
        _, _, display_addr = parse_instructions(display_addr, program, variables, parts, instruction, pc)
    
    program += end_program
    return program, variables


def parse_instructions(display_addr, program, variables, parts, instruction, pc=0):
    if instruction == "#END":
        return program, variables
    
    if instruction in ["LOAD","MOV", "PUSH", "POP", "SWAP", "DVW", "POT", 'DVO', 'VAR', 'LABEL', "CALL", "WCHR", "WSTR", "IMPORT"]:
        if instruction == "LOAD":
            load_instruction(program, variables, parts, instruction)
        elif instruction == 'VAR':
            var_instruction(variables, parts)
        elif instruction == 'CALL':
            call_instruction(program, parts)
        elif instruction == 'IMPORT':
            variables = import_instruction(program, variables, parts)
        elif instruction == 'LABEL':
            label_instruction(program, variables, parts, pc)
        elif instruction == 'WCHR':
            display_addr = wchr_instruction(display_addr, program, parts)
        elif instruction in ["PUSH", "POP", "DVW", "POT",'DVO']:
            unary_instrucition(program, variables, parts, instruction)
        elif instruction in ["SWAP"]:
            swap_instruction(program, parts, instruction)
        elif instruction == 'MOV':
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

def unary_instrucition(program, variables, parts, instruction):
    reg = parts[1]
    if not(reg in variables):
        reg_num = reg.replace("R", "") if "R" in reg else reg.replace("#", "")
    elif '@' in reg:
        reg_num = reg
    elif '0x' in reg:
        reg_num = reg
    else:
        reg_num = variables[reg]
                
    program.append(assembly_to_opcode[instruction])
    program.append(reg_num)

def wchr_instruction(display_addr, program, parts):
    char = parts[1].strip(',')  # Strip commas or other unwanted characters
    char_hex = char_to_hex[char]

    x = parts[2].replace("R", "") if not('#' in parts[2]) else parts[2]
    flag_x = 1
    if '#' in x: 
        flag_x = 0
        x = parts[2].replace("#", "")
    # print(x)
    
    y = parts[3].replace("R", "") if not('#' in parts[3]) else parts[3]
    flag_y = 1
    if '#' in y: 
        flag_y = 0
        y = parts[3].replace("#", "")
    
    scale = parts[4].replace("R", "") if not('#' in parts[4]) else parts[4]
    flag_s = 1
    if '#' in scale: 
        flag_s = 0
        scale = parts[4].replace("#", "")
    
    color = parts[5].replace("R", "") if not('0x' in parts[5]) else parts[5]
    flag_c = 1
    if '0x' in color: flag_c = 0
    # color = parts[5].replace("0x", "")
    
    display_addr = add_to_display_mem(display_addr, program, char_hex)
    display_addr = add_to_display_mem(display_addr, program, x)
    display_addr = add_to_display_mem(display_addr, program, y)
    display_addr = add_to_display_mem(display_addr, program, scale)
    display_addr = add_to_display_mem(display_addr, program, color)  
    display_addr = add_to_display_mem(display_addr, program, flag_x)  
    display_addr = add_to_display_mem(display_addr, program, flag_y)  
    display_addr = add_to_display_mem(display_addr, program, flag_s)  
    display_addr = add_to_display_mem(display_addr, program, flag_c)  
    display_addr = add_to_display_mem(display_addr, program, 1)  

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
    var = parts[1]
    variables[var] = len(program) + pc

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
    program.append("0xDE") #? doesnt GOTO need a param?

def var_instruction(variables, parts):
    """
    Parse the VAR instruction to ensure all variables include a 'location' key.
    """
    name = parts[1]
    value = parts[2]

    if value.startswith("#"):  # Constant value
        variables[name] = {"type": "constant", "value": int(value.replace("#", "")), "location": None}
    elif value.startswith("R"):  # Register
        variables[name] = {"type": "register", "location": int(value.replace("R", "")), "value": None}
    elif value.startswith("@"):  # Memory address
        variables[name] = {"type": "memory", "location": int(value.replace("@", ""), 16), "value": None}
    else:
        raise ValueError(f"Invalid variable declaration: {value}")



def load_instruction(program, variables, parts, instruction):
    opcode = assembly_to_opcode[instruction][parts[1]]
    if not(parts[2] in variables) and not('0x' in parts[2]):
        operand = int(parts[2].replace("#", ""))
    else:
        ost = []
        vst = []
        size = len(parts)
        operand = variables[parts[2]] if not('0x' in parts[2]) else parts[2]
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
    """
    Implements the MOV instruction with support for constants, variables, registers, and memory.
    """
    opcode = assembly_to_opcode[instruction]

    # Determine the source
    src = parts[1]
    if src in variables:  # Variable as source
        src_flag = 2
        src_value = variables[src].get("location")
        if src_value is None:  # Use the value directly for constants
            src_value = variables[src]["value"]
    elif src.startswith("R"):  # Register as source
        src_flag = 0
        src_value = src.replace("R", "")
    elif src.startswith("@"):  # Memory as source
        src_flag = 1
        src_value = src.replace("@", "")
    elif src.startswith("#"):  # Immediate value
        src_flag = 3
        src_value = int(src.replace("#", ""))  # Immediate values are directly encoded
    else:
        raise ValueError(f"Invalid source for MOV: {src}")

    # Determine the destination
    dest = parts[2]
    if dest in variables:  # Variable as destination
        dest_flag = 2
        dest_value = variables[dest].get("location")
        if dest_value is None:  # Use the value directly for constants
            dest_value = variables[dest]["value"]
    elif dest.startswith("R"):  # Register as destination
        dest_flag = 0
        dest_value = dest.replace("R", "")
    elif dest.startswith("@"):  # Memory as destination
        dest_flag = 1
        dest_value = dest.replace("@", "")
    else:
        raise ValueError(f"Invalid destination for MOV: {dest}")

    # Append the MOV instruction to the program
    program.append(opcode)
    program.append(src_flag)
    program.append(dest_flag)
    program.append(src_value)
    program.append(dest_value)



def replace_variables(program, variables):
    # print(variables)
    for i in range(len(program)):
        if "@" in str(program[i]):
            program[i] = str(variables[program[i]])
            
        elif program[i] in variables:
            program[i] = str(variables[program[i]])
        
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