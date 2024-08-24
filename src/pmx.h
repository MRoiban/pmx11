#ifndef PMX_H
#define PMX_H

#define MEMORY_SIZE (1024 * 64 * 10) // 10 KB memory
#define REGISTER_NUMBER (8)

typedef unsigned char Uint8;
typedef signed char Sint8;
typedef unsigned short Uint16;
typedef signed short Sint16;
typedef unsigned int Uint32;

typedef struct {
    unsigned char *memory;
    unsigned char *wst;  // Stack
    unsigned char *rst;  // Stack
    int sp;
    int rp;
    int pc;
    int registers[REGISTER_NUMBER];  // R1, R2, R3
    int dev[0x100];
    int time;
} PMX;

void init_pmx(PMX *pmx);
void load_program(PMX *pmx, int *program, int length);
void unload_program(PMX *pmx);
void add(PMX *pmx);
void sub(PMX *pmx);
void duplicate(PMX *pmx);
void load(PMX *pmx, int reg, int value);
void read_pc(PMX *pmx);
void push(PMX *pmx, int reg);
void pop(PMX *pmx, int reg);
int halt(PMX *pmx, int running);
void jump(PMX *pmx);
void over(PMX *pmx);
void jump_if_not_zero(PMX *pmx);
void equal(PMX *pmx);
void greater_than(PMX *pmx);
void lower_than(PMX *pmx);
void swap(PMX *pmx);
void console_deo(PMX *pmx, int addr);
void increase(PMX *pmx);
void decrease(PMX *pmx);
void remove_top_of_stack(PMX *pmx);
void dev_write(PMX *pmx, int addr);
void put_on_top_of_stack(PMX *pmx, int value);
void goto_instruction(PMX *pmx);
void power(PMX *pmx);
void sqrt_instruction(PMX *pmx);
void abs_instruction(PMX *pmx);
void store(PMX *pmx);
void ret(PMX *pmx);
void run(PMX *pmx);
void load_program_from_file(PMX *pmx, const char *filename);

#endif // PMX_H