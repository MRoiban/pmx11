"""
Core functionality for the PMX assembler.
"""

from pmxlang.assembler.constants import assembly_to_opcode
from pmxlang.assembler.output import replace_variables, write_rom_file
from pmxlang.assembler.instructions import (
    call_instruction, goto_instruction, import_instruction, jnz_instruction, jz_instruction,
    label_instruction, load_instruction, memory_instruction, swap_instruction, unary_instruction,
    var_instruction, wchr_instruction, wstr_instruction, alloc_instruction, free_instruction
)



def assembler(asm_file, variables, pc=0):
    """Main assembler function to process an assembly file."""
    display_addr = 0x2AD00
    
    with open(asm_file, "r") as file:
        lines = file.readlines()

    program = []
    end_program = []

    for line in lines:
        # Remove inline comments starting with ';'
        line = line.split(";", 1)[0].strip()

        if len(line) == 0:  # Skip empty or commented lines
            continue

        parts = line.split()
        instruction = parts[0]

        if instruction.startswith("//"):  # Skip full-line comments
            continue

        _, _, display_addr = parse_instructions(
            display_addr, program, variables, parts, instruction, pc
        )

    program += end_program
    return program, variables


def parse_instructions(display_addr, program, variables, parts, instruction, pc=0):
    """Parse and process individual assembly instructions."""
    if instruction == "#END":
        return program, variables

    if instruction in [
        "LOAD", "MOV", "CPY", "PUSH", "POP", "POKE", "POKE2", "POT",
        "PEEK", "PEEK2", "VAR", "LABEL", "CALL", "JMP", "JNZ",
        "WCHR", "WSTR", "IMPORT", "ALLOC", "FREE"
    ]:
        if instruction == "LOAD":
            load_instruction(program, variables, parts, instruction)
        elif instruction == "VAR":
            var_instruction(variables, parts)
        elif instruction == "CALL":
            call_instruction(program, parts)
        elif instruction == "JNZ":
            jnz_instruction(program, parts)
        elif instruction == "JZ":
            jz_instruction(program, parts)
        elif instruction == "IMPORT":
            variables = import_instruction(program, variables, parts)
        elif instruction == "LABEL":
            label_instruction(program, variables, parts, pc)
        elif instruction == "WCHR":
            display_addr = wchr_instruction(display_addr, program, parts)
        elif instruction == "WSTR":
            display_addr = wstr_instruction(display_addr, program, parts)
        elif instruction in ["PUSH", "POP", "PEEK", "POKE", "POKE2", "POT", "PEEK2", "JMP"]:
            unary_instruction(program, variables, parts, instruction)
        elif instruction in ["MOV", "CPY"]:
            memory_instruction(program, parts, instruction, variables)
        elif instruction == "ALLOC":
            alloc_instruction(program, parts, instruction, variables)
        elif instruction == "FREE":
            free_instruction(program, parts, instruction, variables)
    else:
        if instruction in assembly_to_opcode:
            program.append(assembly_to_opcode[instruction])
            
    return program, variables, display_addr


def assemble(asm_file, rom_file):
    """Main entry point for the assembler."""
    variables = {}
    program, variables = assembler(asm_file, variables)
    program = replace_variables(program, variables)
    write_rom_file(rom_file, program, variables) 