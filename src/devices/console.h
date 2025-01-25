#ifndef PMX_CONSOLE
#define PMX_CONSOLE

#include "../pmx.h"

typedef struct PMXConsole {
    int width, height, scale, cursor_x, cursor_y;
    char* stdin;
    char* stdout;
    char* stderr;
    char* history;
} PMXConsole;

extern PMXConsole pmx_console;

void init_console(void);
void console_write(PMX *pmx, const char* input);
void console_deo(PMX *pmx, int addr);  // Changed to int to match pmx.h

#endif