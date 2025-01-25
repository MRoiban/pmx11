/**
 * @file pmx.c
 * @brief Implementation of the PMX (Programmable Machine eXecutive) functions.
 *
 * This file contains the implementation of various functions for the PMX,
 * including initialization, loading and unloading programs, executing
 * instructions, and utility functions.
 *
 * The PMX is a virtual machine that executes a custom instruction set
 * architecture (ISA). It has a memory, registers, a stack, and various
 * instructions to perform arithmetic, control flow, and I/O operations.
 *
 * The functions in this file provide the necessary functionality to interact
 * with the PMX, load programs into memory, execute instructions, and monitor
 * the state of the PMX during execution.
 *
 * The PMX structure (PMX) holds the state of the PMX, including the memory,
 * registers, stack, and program counter. The functions in this file operate on
 * a PMX structure passed as a parameter.
 *
 * The PMX uses an opcode-based instruction set, where each instruction is
 * represented by a unique opcode. The opcode mappings are defined in the
 * opcode_map array, which maps each opcode to its corresponding assembly
 * instruction.
 *
 * The functions in this file are designed to be used in conjunction with other
 * modules of the PMX system, such as the display module for console output and
 * the device module for I/O operations.
 *
 * Note: Some functions in this file have TODO comments indicating that they
 * should be moved to separate modules. These functions are currently included
 * in this file for simplicity.
 */
#include "pmx.h"
#include "./devices/display.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define WST(i) pmx->wst[i]
#define PC pmx->pc
#define SP pmx->sp
#define increase(pmx) WST(SP)++; PC++
#define decrease(pmx) WST(SP)--; PC++
#define remove_top_of_stack(pmx) SP--; PC++
#define dev_write(pmx, addr) PEEK2(pmx, addr) = WST(SP--); PC += 2
#define add(pmx) WST(++SP)=WST(SP--)+WST(SP--);PC++
#define sub(pmx) WST(++SP)=WST(SP--)-WST(SP--);PC++
#define duplicate(pmx) WST(SP++) = WST(SP);SP++; PC++
#define load(pmx, reg, value) if (reg >= 1 && reg <= REGISTER_NUMBER) pmx->registers[reg - 1] = value; PC += 2
#define read_pc(pmx) WST(++SP) = PC; PC++
#define push(pmx, reg) if (reg >= 1 && reg <= REGISTER_NUMBER) WST(++SP) = pmx->registers[reg - 1]; PC += 2
#define pop(pmx, reg) if (reg >= 1 && reg <= REGISTER_NUMBER) pmx->registers[reg - 1] = WST(SP--); PC += 2
#define jump(pmx, pc) PC = pc
#define over(pmx) WST(SP++) = WST(SP--);SP += 1;PC++
#define equal(pmx) WST(SP--);WST(++SP) = (WST(SP--) == WST(SP--)) ? 0 : 1;PC++
#define greater_than(pmx) WST(++SP) = (WST(SP--) > WST(SP--)) ? 0 : 1;PC++
#define lower_than(pmx) WST(++SP) = (WST(SP--) < WST(SP--)) ? 0 : 1;PC++
#define swap(pmx) {int reg1 = WST(SP--);int reg2 = WST(SP--);int temp = pmx->registers[reg1 - 1];pmx->registers[reg1 - 1] = pmx->registers[reg2 - 1];pmx->registers[reg2 - 1] = temp;PC += 3;}
#define put_on_top_of_stack(pmx, value) WST(++SP) = value;PC += 2
#define goto_instruction(pmx) WST(++SP) = PC + 1;over(pmx);jump(pmx, WST(SP--))
#define power(pmx) WST(++SP) = (int)pow(WST(SP--), WST(SP--));PC++
#define sqrt_instruction(pmx) WST(++SP) = (int)sqrt(WST(SP--));PC++
#define abs_instruction(pmx) WST(++SP) = abs(WST(SP--));PC++
#define mul(pmx) WST(++SP) = WST(SP--) * WST(SP--);PC++
#define div_pmx(pmx) WST(++SP) = WST(SP--) / WST(SP--);PC++
#define ret(pmx) pmx->rst[++pmx->rp] = WST(SP--);PC++

void
init_pmx(PMX *pmx, VariableTable *table) {
    if (pmx == NULL) {
        fprintf(stderr, "Error: PMX pointer is NULL\n");
        return;
    }
    pmx->memory = malloc(MEMORY_SIZE * sizeof(unsigned int));
    pmx->wst = malloc(MEMORY_SIZE * sizeof(unsigned int));
    pmx->rst = malloc(MEMORY_SIZE * sizeof(unsigned int));
    pmx->table = table;

    if (!pmx->memory || !pmx->wst || !pmx->rst) {
        free(pmx->memory);
        free(pmx->wst);
        free(pmx->rst);
        return;
    }

    memset(pmx->memory, 0, MEMORY_SIZE * sizeof(unsigned int));
    memset(pmx->wst, 0, MEMORY_SIZE * sizeof(unsigned int));
    memset(pmx->rst, 0, MEMORY_SIZE * sizeof(unsigned int));
    memset(pmx->registers, 0, REGISTER_NUMBER * sizeof(int));

    SP = -1;
    pmx->rp = -1;
    PC = 0;
    pmx->time = 0;
    pmx->step = 0;
}

void
init_variable_table(VariableTable *table) {
    table->count = 0;
}

void
add_variable(VariableTable *table, const char *name, VariableType type,
             int location, int value) {
    if (table->count >= MAX_VARIABLES) {
        printf(stderr, "Error: Maximum variable limit reached\n");
        return;
    }
    Variable *var = &table->variables[table->count++];
    strncpy(var->name, name, sizeof(var->name));
    var->type = type;
    var->location = location;
    var->value = value;
}

Variable *
get_variable(VariableTable *table, const char *name) {
    for (int i = 0; i < table->count; i++) {
        if (strcmp(table->variables[i].name, name) == 0) {
            return &table->variables[i];
        }
    }
    return NULL;
}

int
resolve_variable(PMX *pmx, Variable *var) {
    switch (var->type) {
    case CONSTANT:
        return var->value;
    case REGISTER:
        return pmx->registers[var->location];
    case MEMORY:
        return pmx->memory[var->location];
    case DEV:
        return pmx->dev[var->location];
    default:
        fprintf(stderr, "Error: Unknown variable type\n");
        return 0;
    }
}

void
set_variable(PMX *pmx, Variable *var, int value) {
    switch (var->type) {
    case CONSTANT:
        fprintf(stderr, "Error: Cannot modify a constant\n");
        break;
    case REGISTER:
        pmx->registers[var->location] = value;
        break;
    case MEMORY:
        pmx->memory[var->location] = value;
        break;
    default:
        fprintf(stderr, "Error: Unknown variable type\n");
        break;
    }
}

void
load_program(PMX *pmx, int *program, int length) {
    pmx->steps = length;
    for (int i = 0; i < length; i++) {
        PEEK(pmx, i) = program[i];
    }
}

void
unload_program(PMX *pmx) {
    PC = 0;
    SP = -1;
    pmx->rp = -1;

    // Clear the program memory
    for (int i = 0; i < pmx->registers[7]; i++) {
        PEEK(pmx, i) = 0;
    }

    pmx->registers[7] = 0;
}






int
halt(PMX *pmx, int running) {
    unload_program(pmx);
    return 0;
}


void
jump_if_not_zero(PMX *pmx) {
    int condition = WST(SP--);
    if (condition != 0) {
        jump(pmx,WST(SP--));
    } else {
        PC++;
    }
}





void
store(PMX *pmx) {
    unsigned int addr = WST(SP--);
    int value = WST(SP--);
    pmx->memory[addr] = value;
    PC++;
}

void
mov(PMX *pmx) {
    int flag1 = pmx->memory[++PC]; // Source type
    int flag2 = pmx->memory[++PC]; // Destination type
    int arg1 = pmx->memory[++PC];  // Source argument
    int arg2 = pmx->memory[++PC];  // Destination argument
    VariableTable *var_table = &pmx->table;
    int value = 0;

    // Resolve the source value
    if (flag1 == 0) { // Source is a register
        value = pmx->registers[arg1 - 1];
    } else if (flag1 == 1) { // Source is memory
        value = pmx->memory[arg1];
    } else if (flag1 == 2) { // Source is a variable
        Variable *var = get_variable(var_table, (const char *)arg1);
        if (var == NULL) {
            fprintf(stderr, "Error: Variable not found\n");
            return;
        }
        value = resolve_variable(pmx, var);
    } else {
        fprintf(stderr, "Error: Unknown source flag\n");
        return;
    }

    // Assign the value to the destination
    if (flag2 == 0) { // Destination is a register
        pmx->registers[arg2 - 1] = value;
    } else if (flag2 == 1) { // Destination is memory
        pmx->memory[arg2] = value;
    } else if (flag2 == 2) { // Destination is a variable
        Variable *var = get_variable(var_table, (const char *)arg2);
        if (var == NULL) {
            fprintf(stderr, "Error: Variable not found\n");
            return;
        }
        set_variable(pmx, var, value);
    } else {
        fprintf(stderr, "Error: Unknown destination flag\n");
        return;
    }

    PC++;
}

typedef struct {
    unsigned char opcode;
    const char *assembly;
} OpcodeMapping;

#define OPCODE_COUNT 32 // Number of opcodes

// Array of opcode mappings
const OpcodeMapping opcode_map[OPCODE_COUNT] = {
    {0x00, "RET"},     {0x01, "LOAD R1"}, {0x02, "LOAD R2"}, {0x03, "LOAD R3"},
    {0x04, "LOAD R4"}, {0x05, "LOAD R5"}, {0x06, "LOAD R6"}, {0x07, "LOAD R7"},
    {0x08, "LOAD R8"}, {0x09, "ADD"},     {0x0A, "SUB"},     {0x0B, "PUSH"},
    {0x0C, "POP"},     {0x0D, "EQUAL"},   {0x0E, "GTH"},     {0x0F, "LTH"},
    {0x10, "DUP"},     {0x11, "POT"},     {0x12, "OVR"},     {0x13, "INC"},
    {0x14, "DCR"},     {0x15, "MUL"},     {0x16, "DIV"},     {0x17, "SQRT"},
    {0x18, "POW"},     {0x19, "ABS"},     {0x20, "MOV"},     {0xAA, "STR"},
    {0xAF, "DVO"},     {0xBF, "DVW"},     {0xCF, "SWAP"},    {0xDE, "GOTO"},
    {0xDF, "JMP"},     {0xEE, "RMV"},     {0xEF, "JNZ"},     {0xFE, "RPC"},
    {0xFF, "HALT"},
};

const char *
get_assembly_instruction(unsigned char opcode) {
    for (int i = 0; i < OPCODE_COUNT; i++) {
        if (opcode_map[i].opcode == opcode) {
            return opcode_map[i].assembly;
        }
    }
    return "UNKNOWN"; // Return "UNKNOWN" if opcode is not found
}

void
dump(PMX *pmx, int opcode) {
    // Open the file in write mode
    FILE *file = fopen("./log.txt", "a");
    if (file == NULL) {
        // Handle file open error
        perror("Error opening file");
        return;
    }

    // Write the PMX state to the file

    if (opcode != 0x00) {
        fprintf(file, "(%d) \tOPCODE: %x (%s)\n", PC, opcode,
                get_assembly_instruction(opcode));
        fprintf(file, "\t\tWST: [ ");
        for (int i = 0; i <= SP; i++) {
            fprintf(file, "%d ", pmx->wst[i]);
        }
        fprintf(file, "]\n");
        fprintf(file, "\t\tRST: [ ");
        for (int i = 0; i <= pmx->rp; i++) {
            fprintf(file, "%d ", pmx->rst[i]);
        }
        fprintf(file, "]\n");
        fprintf(file,
                "\t\tR1=%d, R2=%d, R3=%d, R4=%d, R5=%d, R6=%d, R7=%d, R8=%d\n",
                pmx->registers[0], pmx->registers[1], pmx->registers[2],
                pmx->registers[3], pmx->registers[4], pmx->registers[5],
                pmx->registers[6], pmx->registers[7]);
        fprintf(file, "\t\tDISPLAY ADDR: [ ");
        for (int i = DISPLAY_BLOCK; i <= DISPLAY_BLOCK + 50; i++) {
            fprintf(file, "%d ", pmx->memory[i]);
        }
        fprintf(file, "]\n");
        fprintf(file, "-------------------------------------\n");
    }

    // Close the file
    fclose(file);
}



void
run(PMX *pmx) {
    int running = 1;
    FILE *file = fopen("./log.txt", "a");
    if (file == NULL) {
        // Handle file open error
        perror("Error opening file");
        return;
    }
    fclose(file);

    while (running) {
        int instruction = pmx->memory[PC];
        // printf("%x\n",instruction);
        switch (instruction) {
        case 0x00:
            running = halt(pmx, running);
            break;
        case 0x01:
            load(pmx, 1, pmx->memory[PC + 1]);
            break;
        case 0x02:
            load(pmx, 2, pmx->memory[PC + 1]);
            break;
        case 0x03:
            load(pmx, 3, pmx->memory[PC + 1]);
            break;
        case 0x04:
            load(pmx, 4, pmx->memory[PC + 1]);
            break;
        case 0x05:
            load(pmx, 5, pmx->memory[PC + 1]);
            break;
        case 0x06:
            load(pmx, 6, pmx->memory[PC + 1]);
            break;
        case 0x07:
            load(pmx, 7, pmx->memory[PC + 1]);
            break;
        case 0x08:
            load(pmx, 8, pmx->memory[PC + 1]);
            break;
        case 0x09:
            add(pmx);
            break;
        case 0x0A:
            sub(pmx);
            break;
        case 0x0B:
            push(pmx, pmx->memory[PC + 1]);
            break;
        case 0x0C:
            pop(pmx, pmx->memory[PC + 1]);
            break;
        case 0x0D:
            equal(pmx);
            break;
        case 0x0F:
            lower_than(pmx);
            break;
        case 0x10:
            duplicate(pmx);
            break;
        case 0x11:
            put_on_top_of_stack(pmx, pmx->memory[PC + 1]);
            break;
        case 0x12:
            over(pmx);
            break;
        case 0x13:
            increase(pmx);
            break;
        case 0x14:
            decrease(pmx);
            break;
        case 0x20:
            mov(pmx);
            break;
        case 0x24:
            sqrt_instruction(pmx);
            break;
        case 0x25:
            abs_instruction(pmx);
            break;
        case 0x23:
            power(pmx);
            break;
        case 0xAA:
            store(pmx);
            break;
        case 0xAF:
            console_deo(pmx, pmx->memory[PC + 1]);
            break;
        case 0xBF:
            dev_write(pmx, pmx->memory[PC + 1]);
            break;
        case 0xDE:
            goto_instruction(pmx);
            break;
        case 0xDF:
            jump(pmx, pmx->memory[PC + 1]);
            break;
        case 0xEE:
            remove_top_of_stack(pmx);
            break;
        case 0xEF:
            jump_if_not_zero(pmx);
            break;
        case 0xFE:
            read_pc(pmx);
            break;
        case 0xFF:
            ret(pmx);
            break;
        case 0x1CF:
            swap(pmx);
            break;
        case 0x2CF:
            swap(pmx);
            break;
        case 0x3CF:
            swap(pmx);
            break;
        default:
            running = 0;
            break;
        }
        dump(pmx, instruction);
    }
}

void
step(PMX *pmx) {
    int running = 1;
    int instruction;
    FILE *file = fopen("./log.txt", "a");
    if (file == NULL) {
        // Handle file open error
        perror("Error opening file");
        return;
    }

    fclose(file);
    if (pmx->step < pmx->steps) {
        instruction = pmx->memory[PC];
        pmx->step++;
    } else {
        instruction = 0x00;
    }
    switch (instruction) {
    case 0x00:
        running = halt(pmx, running);
        break;
    case 0x01:
        load(pmx, 1, pmx->memory[PC + 1]);
        break;
    case 0x02:
        load(pmx, 2, pmx->memory[PC + 1]);
        break;
    case 0x03:
        load(pmx, 3, pmx->memory[PC + 1]);
        break;
    case 0x04:
        load(pmx, 4, pmx->memory[PC + 1]);
        break;
    case 0x05:
        load(pmx, 5, pmx->memory[PC + 1]);
        break;
    case 0x06:
        load(pmx, 6, pmx->memory[PC + 1]);
        break;
    case 0x07:
        load(pmx, 7, pmx->memory[PC + 1]);
        break;
    case 0x08:
        load(pmx, 8, pmx->memory[PC + 1]);
        break;
    case 0x09:
        add(pmx);
        break;
    case 0x0A:
        sub(pmx);
        break;
    case 0x0B:
        push(pmx, pmx->memory[PC + 1]);
        break;
    case 0x0C:
        pop(pmx, pmx->memory[PC + 1]);
        break;
    case 0x0D:
        equal(pmx);
        break;
    case 0x0F:
        lower_than(pmx);
        break;
    case 0x10:
        duplicate(pmx);
        break;
    case 0x11:
        put_on_top_of_stack(pmx, pmx->memory[PC + 1]);
        break;
    case 0x12:
        over(pmx);
        break;
    case 0x13:
        increase(pmx);
        break;
    case 0x14:
        decrease(pmx);
        break;
    case 0x15:
        mul(pmx);
        break;
    case 0x16:
        div_pmx(pmx);
        break;
    case 0x17:
        sqrt_instruction(pmx);
        break;
    case 0x18:
        power(pmx);
        break;
    case 0x19:
        abs_instruction(pmx);
        break;
    case 0x20:
        mov(pmx);
        break;
    case 0x24:
        sqrt_instruction(pmx);
        break;
    case 0x25:
        abs_instruction(pmx);
        break;
    case 0x23:
        power(pmx);
        break;
    case 0xAA:
        store(pmx);
        break;
    case 0xAF:
        console_deo(pmx, pmx->memory[PC + 1]);
        break;
    case 0xBF:
        dev_write(pmx, pmx->memory[PC + 1]);
        break;
    case 0xDE:
        goto_instruction(pmx);
        break;
    case 0xDF:
        jump(pmx, pmx->memory[PC + 1]);
        break;
    case 0xEE:
        remove_top_of_stack(pmx);
        break;
    case 0xEF:
        jump_if_not_zero(pmx);
        break;
    case 0xFE:
        read_pc(pmx);
        break;
    case 0xFF:
        ret(pmx);
        break;
    case 0x1CF:
        swap(pmx);
        break;
    case 0x2CF:
        swap(pmx);
        break;
    case 0x3CF:
        swap(pmx);
        break;
    default:
        running = 0;
        break;
    }
    dump(pmx, instruction);
}

#define MAX_LINE_LENGTH 20000

void
load_variables(VariableTable *table, const char *filename) {
    FILE *file = fopen(filename, "r");
    if (!file) {
        fprintf(stderr, "Error: Could not open file %s\n", filename);
        return;
    }

    char line[256];
    int in_variables = 0;

    while (fgets(line, sizeof(line), file)) {
        if (strncmp(line, "VARIABLES", 9) == 0) {
            in_variables = 1;
            continue;
        } else if (strncmp(line, "PROGRAM", 7) == 0) {
            in_variables = 0;
            break;
        }

        if (in_variables) {
            char name[32];
            char type[16];
            int value;
            sscanf(line, "%s %s %x", name, type, &value);

            if (strcmp(type, "CONSTANT") == 0) {
                add_variable(table, name, CONSTANT, 0, value);
            } else if (strcmp(type, "REGISTER") == 0) {
                add_variable(table, name, REGISTER, value, 0);
            } else if (strcmp(type, "MEMORY") == 0) {
                add_variable(table, name, MEMORY, value, 0);
            }
        }
    }

    fclose(file);
}

void
load_program_from_file(PMX *pmx, VariableTable *table, const char *filename) {
    FILE *file = fopen(filename, "r");
    if (!file) {
        fprintf(stderr, "Error: Could not open file %s\n", filename);
        return;
    }
    char line[256];
    int in_variables = 0;
    int in_program = 0;
    int program_index = 0;

    while (fgets(line, sizeof(line), file)) {
        char *trimmed = strtok(line, "\n");
        if (!trimmed)
            continue; // Skip empty lines

        if (strcmp(trimmed, "VARIABLES") == 0) {
            in_variables = 1;
            in_program = 0;
            continue;
        }

        if (strcmp(trimmed, "PROGRAM") == 0) {
            in_program = 1;
            in_variables = 0;
            continue;
        }

        if (in_variables) {
            char name[32], type[16];
            int value;

            if (sscanf(trimmed, "%s %s %d", name, type, &value) != 3) {
                fprintf(stderr, "Error: Invalid variable declaration '%s'\n",
                        trimmed);
                continue;
            }

            if (strcmp(type, "CONSTANT") == 0) {
                add_variable(table, name, CONSTANT, 0, value);
            } else if (strcmp(type, "REGISTER") == 0) {
                add_variable(table, name, REGISTER, value, 0);
            } else if (strcmp(type, "MEMORY") == 0) {
                add_variable(table, name, MEMORY, value, 0);
            } else {
                fprintf(stderr, "Error: Unknown variable type '%s'\n", type);
            }
        }

        if (in_program) {
            char *token = strtok(trimmed, ",");
            while (token) {
                int instruction;

                // Parse as hexadecimal or decimal
                if (strncmp(token, "0x", 2) == 0) {
                    sscanf(token, "%x", &instruction); // Hexadecimal
                } else {
                    sscanf(token, "%d", &instruction); // Decimal
                }
                if (strncmp(token, "$", 1) == 0) {
                    Variable *var =
                        get_variable(table, token + 1); // Skip "var_" prefix
                    if (var != NULL) {
                        instruction = var->value;
                    } else {
                        fprintf(stderr, "Error: Variable %s not found\n",
                                token);
                    }
                }
                // Debugging
                // printf("Parsing token: %d\n", instruction);

                // Ensure valid memory boundaries
                if (program_index >= MEMORY_SIZE) {
                    fprintf(stderr, "Error: Program exceeds memory size\n");
                    fclose(file);
                    return;
                }

                // Store instruction in memory
                pmx->memory[program_index++] = instruction;

                // Next token
                token = strtok(NULL, ",");
            }
        }
    }

    if (!in_variables && !in_program) {
        fprintf(stderr,
                "Error: Missing VARIABLES or PROGRAM section in input file\n");
    }

    fclose(file);
    pmx->steps = program_index;
    pmx->registers[7] = program_index; // Store program size
}
