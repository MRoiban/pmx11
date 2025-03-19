#include "./console.h"
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

PMXConsole pmx_console = {.cursor_x = 0,
                          .cursor_y = 0,
                          .height = 0,
                          .width = 0,
                          .scale = 1,
                          .stdin = NULL,
                          .stdout = NULL,
                          .stderr = NULL,
                          .history = NULL};

void
init_console() {
    pmx_console.width = 80;  // Standard terminal width
    pmx_console.height = 24; // Standard terminal height
    pmx_console.scale = 1;
    pmx_console.cursor_x = 0;
    pmx_console.cursor_y = 0;

    size_t std_buff_size = 1024;
    size_t hist_buff_size = 4096;

    // Allocate memory for console buffers
    pmx_console.stdin = (char *)calloc(std_buff_size, sizeof(char));
    pmx_console.stdout = (char *)calloc(std_buff_size, sizeof(char));
    pmx_console.stderr = (char *)calloc(std_buff_size, sizeof(char));
    pmx_console.history = (char *)calloc(hist_buff_size, sizeof(char));

    // Check if memory allocation was successful
    if (!(pmx_console.stdin && pmx_console.stdout && pmx_console.stderr &&
          pmx_console.history)) {
        // fprintf(stderr, "Failed to allocate console buffers\n");
        // You should handle the memory allocation failure here if necessary
    }
}

#include <stdio.h>

void
console_write(PMX *pmx, const char *input) {
    if (input == NULL) {
        fprintf(stderr, "Error: Input string is NULL\n");
        return;
    }

    size_t len = strlen(input);
    for (size_t i = 0; i < len; i++) {
        POKE2(0x06, input[i]);
        console_deo(pmx, 0x01);
    }

    // Add newline at the end
    POKE2(0x06, '\n');
    console_deo(pmx, 0x01);
}

void
console_deo(PMX *pmx, int addr) { // Changed Uint8 to int to match pmx.h
    switch (addr) {
    case 0x00: {
        char c = PEEK2(0x05);
        fprintf(stderr, "%c", c);
        break;
    }
    case 0x01: {
        char c = PEEK2(0x06);
        printf("%c", c);
        break;
    }
    case 0x02: {
        int d = PEEK2(0x06);
        printf("%d\n", d);
        break;
    }
    default:
        break;
    }
}

// Update console.h to match:
/*
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
*/