#include "../pmx.h"

#ifndef CONSOLE
#define CONSOLE

typedef struct console
{
    char* stdin;
    char* stdout;
    char* stderr;
    char* history;
};


#endif 