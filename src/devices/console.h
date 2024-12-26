#include "../pmx.h"

#ifndef CONSOLE
#define CONSOLE

typedef struct console
{
    int width, height, scale, cursor_x, cursor_y;
    char* stdin;
    char* stdout;
    char* stderr;
    char* history;
};


#endif 