#include "../pmx.h"

#ifndef PMX_CONSOLE
#define PMX_CONSOLE

typedef struct PMXConsole
{
    int width, height, scale, cursor_x, cursor_y;
    char* stdin;
    char* stdout;
    char* stderr;
    char* history;
} PMXConsole;

extern PMXConsole pmx_console;

void 
init_console();

#endif 