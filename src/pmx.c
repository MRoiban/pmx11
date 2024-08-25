#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "pmx.h"
#include "./devices/display.h"

void 
init_pmx(PMX *pmx) {
    if (pmx == NULL) {
        fprintf(stderr, "Error: PMX pointer is NULL\n");
        return;
    }
    pmx->memory = malloc(MEMORY_SIZE * sizeof(unsigned int));
    pmx->wst = malloc(MEMORY_SIZE * sizeof(unsigned int));
    pmx->rst = malloc(MEMORY_SIZE * sizeof(unsigned int));
    for (int i = 0; i < MEMORY_SIZE; i++) {
        pmx->memory[i] = 0;
        pmx->wst[i] = 0;
        pmx->rst[i] = 0;
    }
    printf("hey");
    for (int i = 0; i < REGISTER_NUMBER; i++) {
        pmx->registers[i] = 0;
    }
    pmx->sp = -1;
    pmx->rp = -1;
    pmx->pc = 0;
    pmx->time = 0;
}

void 
load_program(PMX *pmx, int *program, int length) {
    for (int i = 0; i < length; i++) {
        printf("load: %d\n", program[i]);
        pmx->memory[i] = program[i];
        printf("loadmem: %d\n", pmx->memory[i]);
    }
}

void
unload_program(PMX *pmx) {
    pmx->pc = 0;
    pmx->sp = -1;
    pmx->rp = -1;

    // Clear the program memory
    for (int i = 0; i < pmx->registers[7]; i++) {
        pmx->memory[i] = 0;
    }
    
    pmx->registers[7] = 0;
}


void 
add(PMX *pmx) {
    int a = pmx->wst[pmx->sp--];
    int b = pmx->wst[pmx->sp--];
    pmx->wst[++pmx->sp] = a + b;
    pmx->pc += 1;
}

void sub(PMX *pmx) {
    int a = pmx->wst[pmx->sp--];
    int b = pmx->wst[pmx->sp--];
    pmx->wst[++pmx->sp] = a - b;
    pmx->pc += 1;
}

void 
duplicate(PMX *pmx) {
    pmx->wst[pmx->sp + 1] = pmx->wst[pmx->sp];
    pmx->sp += 1;
    pmx->pc += 1;
}

void 
load(PMX *pmx, int reg, int value) {
    if (reg >= 1 && reg <= REGISTER_NUMBER) {
        pmx->registers[reg - 1] = value;
    }
    pmx->pc += 2;
}

void 
read_pc(PMX *pmx) {
    pmx->wst[++pmx->sp] = pmx->pc;
    pmx->pc += 1;
}

void 
push(PMX *pmx, int reg) {
    printf("Push R#: %d\n", reg);
    if (reg >= 1 && reg <= REGISTER_NUMBER) {
        printf("REG: %d", pmx->registers[reg - 1]);
        pmx->wst[++pmx->sp] = pmx->registers[reg - 1];
    }
    pmx->pc += 2;
}

void 
pop(PMX *pmx, int reg) {
    if (reg >= 1 && reg <= REGISTER_NUMBER) {
        pmx->registers[reg - 1] = pmx->wst[pmx->sp--];
    }
    pmx->pc += 2;
}

int halt(PMX *pmx, int running) {
    unload_program(pmx);
    return 0;
}

void 
jump(PMX *pmx) {
    printf("jmp: %d\n", pmx->wst[pmx->sp]);
    pmx->pc = pmx->wst[pmx->sp--];
}

void 
over(PMX *pmx) {
    pmx->wst[pmx->sp + 1] = pmx->wst[pmx->sp - 1];
    pmx->sp += 1;
    pmx->pc += 1;
}

void 
jump_if_not_zero(PMX *pmx) {
    int condition = pmx->wst[pmx->sp--];
    if (condition != 0) {
        jump(pmx);
    } else {
        pmx->pc += 1;
    }
}

void 
equal(PMX *pmx) {
    int co1 = pmx->wst[pmx->sp--];
    int co2 = pmx->wst[pmx->sp--];
    pmx->wst[++pmx->sp] = (co1 == co2) ? 0 : 1;
    pmx->pc += 1;
}

void 
greater_than(PMX *pmx) {
    int co1 = pmx->wst[pmx->sp--];
    int co2 = pmx->wst[pmx->sp--];
    pmx->wst[++pmx->sp] = (co1 > co2) ? 0 : 1;
    pmx->pc += 1;
}

void 
lower_than(PMX *pmx) {
    int co1 = pmx->wst[pmx->sp--];
    int co2 = pmx->wst[pmx->sp--];
    pmx->wst[++pmx->sp] = (co1 < co2) ? 0 : 1;
    pmx->pc += 1;
}

void 
swap(PMX *pmx) {
    int reg1 = pmx->wst[pmx->sp--];
    int reg2 = pmx->wst[pmx->sp--];
    int temp = pmx->registers[reg1 - 1];
    pmx->registers[reg1 - 1] = pmx->registers[reg2 - 1];
    pmx->registers[reg2 - 1] = temp;
    pmx->pc += 3;
}


// TODO: Move to console.c
void 
console_deo(PMX *pmx, int addr) {
    if (addr == 24) {
        fprintf(stderr, "%d\n", pmx->dev[addr]);
    } else if (addr == 25) {
        printf("%d\n", pmx->dev[addr]);
    }
    pmx->pc += 2;
}

void 
increase(PMX *pmx) {
    pmx->wst[pmx->sp]++;
    pmx->pc += 1;
}

void 
decrease(PMX *pmx) {
    pmx->wst[pmx->sp]--;
    pmx->pc += 1;
}

void 
remove_top_of_stack(PMX *pmx) {
    pmx->sp--;
    pmx->pc += 1;
}

// TODO: Move to console.c
void 
dev_write(PMX *pmx, int addr) {
    pmx->dev[addr] = pmx->wst[pmx->sp--];
    pmx->pc += 2;
}

void 
put_on_top_of_stack(PMX *pmx, unsigned int value) {
    printf("value: %d | memory: %d\n", value , pmx->memory[pmx->pc + 2]);
    // printf("memory: %d\n", pmx->memory[pmx->pc + 1]);
    pmx->wst[++pmx->sp] = value;
    pmx->pc += 2;
}

void 
goto_instruction(PMX *pmx) {
    // printf("wst: %x | next_pc: %d\n", pmx->wst[pmx->sp],  pmx->pc + 1);
    pmx->wst[++pmx->sp] =  pmx->pc + 1; 
    over(pmx);
    // pmx->wst[++pmx->sp] = pmx->memory[pmx->pc + 1];
    jump(pmx);
}

void 
power(PMX *pmx) {
    int value = pmx->wst[pmx->sp--];
    int power = pmx->wst[pmx->sp--];
    pmx->wst[++pmx->sp] = (int)pow(value, power);
    pmx->pc += 1;
}

void 
sqrt_instruction(PMX *pmx) {
    int value = pmx->wst[pmx->sp--];
    pmx->wst[++pmx->sp] = (int)sqrt(value);
    pmx->pc += 1;
}

void 
abs_instruction(PMX *pmx) {
    int value = pmx->wst[pmx->sp--];
    pmx->wst[++pmx->sp] = abs(value);
    pmx->pc += 1;
}

void 
store(PMX *pmx) {
    unsigned int addr = pmx->wst[pmx->sp--];
    int value = pmx->wst[pmx->sp--];
    pmx->memory[addr] = value;
    printf("in mem: %d | addr: %d\n", pmx->memory[addr], addr);
    pmx->pc += 1;
}


typedef struct {
    unsigned char opcode;
    const char *assembly;
} OpcodeMapping;

#define OPCODE_COUNT 31 // Number of opcodes

// Array of opcode mappings
const OpcodeMapping opcode_map[OPCODE_COUNT] = {
    {0x00, "RET"},
    {0x01, "LOAD R1"},
    {0x02, "LOAD R2"},
    {0x03, "LOAD R3"},
    {0x04, "LOAD R4"},
    {0x05, "LOAD R5"},
    {0x06, "LOAD R6"},
    {0x07, "LOAD R7"},
    {0x08, "LOAD R8"},
    {0x09, "ADD"},
    {0x0A, "SUB"},
    {0x0B, "PUSH"},
    {0x0C, "POP"},
    {0x0D, "EQUAL"},
    {0x0E, "GTH"},
    {0x0F, "LTH"},
    {0x10, "DUP"},
    {0x11, "POT"},
    {0x12, "OVR"},
    {0x13, "INC"},
    {0x14, "DCR"},
    {0xAA, "STR"},
    {0xAF, "DVO"},
    {0xBF, "DVW"},
    {0xCF, "SWAP"},
    {0xDE, "GOTO"},
    {0xDF, "JMP"},
    {0xEE, "RMV"},
    {0xEF, "JNZ"},
    {0xFE, "RPC"},
    {0xFF, "HALT"},
};
const char* 
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
    fprintf(file, "(%d) \tOPCODE: %x (%s)\n", pmx->pc, opcode, get_assembly_instruction(opcode));
    fprintf(file, "\t\tWST: [ ");
    for (int i = 0; i <= pmx->sp; i++) {
        fprintf(file, "%d ", pmx->wst[i]);
    }
    fprintf(file, "]\n");
    fprintf(file, "\t\tRST: [ ");
    for (int i = 0; i <= pmx->rp; i++) {
        fprintf(file, "%d ", pmx->rst[i]);
    }
    fprintf(file, "]\n");
    fprintf(file, "\t\tR1=%d, R2=%d, R3=%d, R4=%d, R5=%d, R6=%d, R7=%d, R8=%d\n", pmx->registers[0], pmx->registers[1], pmx->registers[2], pmx->registers[3],pmx->registers[4],pmx->registers[5],pmx->registers[6],pmx->registers[7]);
    fprintf(file, "-------------------------------------\n");

    // Close the file
    fclose(file);
}

void 
ret(PMX *pmx) {
    pmx->rst[++pmx->rp] = pmx->wst[pmx->sp--];
    pmx->pc++;
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
        int instruction = pmx->memory[pmx->pc];
        // printf("%x\n",instruction);
        switch (instruction) {
            case 0x00: running=halt(pmx, running); break;
            case 0x01: load(pmx, 1, pmx->memory[pmx->pc + 1]); break;
            case 0x02: load(pmx, 2, pmx->memory[pmx->pc + 1]); break;
            case 0x03: load(pmx, 3, pmx->memory[pmx->pc + 1]); break;
            case 0x04: load(pmx, 4, pmx->memory[pmx->pc + 1]); break;
            case 0x05: load(pmx, 5, pmx->memory[pmx->pc + 1]); break;
            case 0x06: load(pmx, 6, pmx->memory[pmx->pc + 1]); break;
            case 0x07: load(pmx, 7, pmx->memory[pmx->pc + 1]); break;
            case 0x08: load(pmx, 8, pmx->memory[pmx->pc + 1]); break;
            case 0x09: add(pmx); break;
            case 0x0A: sub(pmx); break;
            case 0x0B: push(pmx, pmx->memory[pmx->pc + 1]); break;
            case 0x0C: pop(pmx, pmx->memory[pmx->pc + 1]); break;
            case 0x0D: equal(pmx); break;
            case 0x0F: lower_than(pmx); break;
            case 0x10: duplicate(pmx); break;
            case 0x11: put_on_top_of_stack(pmx, pmx->memory[pmx->pc + 1]); break;
            case 0x12: over(pmx); break;
            case 0x13: increase(pmx); break;
            case 0x14: decrease(pmx); break;
            case 0x24: sqrt_instruction(pmx); break;
            case 0x25: abs_instruction(pmx); break;
            case 0x23: power(pmx); break;
            case 0xAA: store(pmx); break;
            case 0xAF: console_deo(pmx, pmx->memory[pmx->pc + 1]); break;
            case 0xBF: dev_write(pmx, pmx->memory[pmx->pc + 1]); break;
            case 0xDE: goto_instruction(pmx); break;
            case 0xDF: jump(pmx); break;
            case 0xEE: remove_top_of_stack(pmx); break;
            case 0xEF: jump_if_not_zero(pmx); break;
            case 0xFE: read_pc(pmx); break;
            case 0xFF: ret(pmx); break;
            case 0x1CF: swap(pmx); break;
            case 0x2CF: swap(pmx); break;
            case 0x3CF: swap(pmx); break;
            default: running = 0; break;
        }
        dump(pmx, instruction);
    }
}

#define MAX_PROGRAM_SIZE 1000
#define MAX_LINE_LENGTH 200
void 
load_program_from_file(PMX *pmx, const char *filename) {
    // Open the file
    
    FILE *file = fopen(filename, "r");
    if (file == NULL) {
        printf("Failed to open file: %s\n", filename);
        return;
    }

    // Read the content from the file
    int program[MAX_PROGRAM_SIZE];
    int program_size = 0;

    char line[MAX_LINE_LENGTH];
    while (fgets(line, sizeof(line), file) != NULL) {
        char *token = strtok(line, ",");
        while (token != NULL) {
            int value;
            printf("strtoken: %s\n", token);
            // Check if the token starts with '0x' for hexadecimal values
            if (strncmp(token, "0x", 2) == 0) {
                sscanf(token, "%x", &value);
                printf("hex-token: %x\n", value);
            } else {
                sscanf(token, "%d", &value);
            }

            if (program_size >= MAX_PROGRAM_SIZE) {
                printf("Program size exceeds maximum limit\n");
                break;
            }
            program[program_size++] = value;
            token = strtok(NULL, ",");
        }
    }

    // Close the file
    fclose(file);

    // Load the program into memory
    pmx->registers[7] = program_size;
    load_program(pmx, program, program_size);
}


