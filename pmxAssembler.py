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
    "Z": "0x1B"
}

def assembler_START(lines, display_addr):
    program = []
    variables = {}
    count = 0
    for line in lines:
        if len(line) <= 0:
            continue
        
        parts = line.strip().split()
        for i in range(len(parts)):
            if "," in parts[i]:
                parts[i] = parts[i].split(",")[0]
        instruction = parts[0] if parts != [] else None
        # instruction = None if instruction == ';' else instruction
        if instruction != None:
            if '//' in instruction:
                instruction = None
                
        if instruction == "#START":
            continue
        if instruction == "#END":
            return program, variables, count, display_addr
        _ , _ , display_addr = parse_instructions(display_addr, program, variables, parts, instruction)
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
        if len(line) <= 0:
            continue
        
        parts = line.strip().split()
        for i in range(len(parts)):
            if "," in parts[i]:
                parts[i] = parts[i].split(",")[0]
        instruction = parts[0] if parts != [] else None
        # instruction = None if instruction == ';' else instruction
        if instruction != None:
            if '//' in instruction:
                instruction = None
                
        if instruction == "#START":
            if count == None:
                count = 0
            assembled = assembler_START(lines, display_addr)
            end_program += assembled[0]
            variables = {**variables, **assembled[1]}
            display_addr = assembled[3]
        if assembled != None and count != None and count <= assembled[2]:
            count += 1
            continue
        else:
            count = None
        if instruction == "#END":
            continue
            
        _ , _ , display_addr = parse_instructions(display_addr, program, variables, parts, instruction, pc)
        print(variables)
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
            mov(program, parts, instruction)
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
    char = parts[1]
    char_hex = char_to_hex[char]
    x = parts[2].replace("#", "")
    y = parts[3].replace("#", "") 
    scale = parts[4].replace("#", "")
    color = parts[5]
    display_addr = add_to_display_mem(display_addr, program, char_hex)
    display_addr = add_to_display_mem(display_addr, program, x)
    display_addr = add_to_display_mem(display_addr, program, y)
    display_addr = add_to_display_mem(display_addr, program, scale)
    display_addr = add_to_display_mem(display_addr, program, color)            
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
    var = parts[1]
    value = int(parts[2].replace("#", ""))
    variables[var] = value

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

def mov(program, parts, instruction):
    opcode = assembly_to_opcode[instruction]
    arg1 = parts[1].replace("R", "") if not('0x' in parts[1]) else parts[1]
    flag1 = 0
    if '0x' in arg1: flag1 = 1
    arg2 = parts[2].replace("R", "") if not('0x' in parts[2]) else parts[2]
    flag2 = 0
    if '0x' in arg2: flag2 = 1
    program.append(opcode)
    program.append(flag1)
    program.append(flag2)
    program.append(arg1)
    program.append(arg2)

def replace_variables(program, variables):
    print(variables)
    for i in range(len(program)):
        if "@" in str(program[i]):
            program[i] = str(variables[program[i]])
            
        elif program[i] in variables:
            program[i] = str(variables[program[i]])
        
        else:
            program[i] = str(program[i])
    return program
            
    

def write_rom_file(rom_file, program):
    with open(rom_file, "w") as file:
        file.write(",".join(program))


def assemble(asm_file, rom_file):
    variables = {}
    program, variables = assembler(asm_file, variables)
    program = replace_variables(program, variables)
    write_rom_file(rom_file, program)