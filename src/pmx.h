#include "./utils.h"
#ifndef PMX_H
#define PMX_H



#define POKE(i,j) pmx->memory[i] = j
#define POKE2(i,j) pmx->dev[i] = j
#define PEEK(i) pmx->memory[i]
#define PEEK2(i) pmx->dev[i]


typedef enum {
    CONSTANT,
    REGISTER,
    MEMORY,
    DEV,
} VariableType;

typedef struct {
    char name[32];
    VariableType type;
    int location;
    int value;
} Variable;

typedef struct {
    Variable variables[MAX_VARIABLES];
    int count;
} VariableTable;

typedef struct {
    unsigned int *memory;
    unsigned int *wst;
    unsigned int *rst;
    VariableTable* table;
    int sp;
    int rp;
    int pc;
    int step;
    int steps;
    int registers[REGISTER_NUMBER];
    int dev[512];
    int time;
    int log_enabled;
} PMX;

void
init_pmx(PMX *pmx, VariableTable *table);
void
init_variable_table(VariableTable *table);
void
add_variable(VariableTable *table, const char *name, VariableType type,
             int location, int value);
Variable *
get_variable(VariableTable *table, const char *name);
int
resolve_variable(PMX *pmx, Variable *var);
void
set_variable(PMX *pmx, Variable *var, int value);
void
load_program(PMX *pmx, int *program, int length);
void
unload_program(PMX *pmx);
int
halt(PMX *pmx, int running);
void
jump_if_not_zero(PMX *pmx);
void
console_deo(PMX *pmx, int addr);
void
store(PMX *pmx);
void
pmx_memmov(PMX *pmx);
void
pmx_memcpy(PMX *pmx);
void
run(PMX *pmx);
void
step(PMX *pmx);
void
load_program_from_file(PMX *pmx, VariableTable *table, const char *filename);
void
load_variables(VariableTable *table, const char *filename);

#endif