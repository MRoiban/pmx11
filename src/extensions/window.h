#include "../devices/display.h"

#ifndef WINDOW_H
#define WINDOW_H

#define RED 0xFF00
#define GREEN 0xABEEBB
#define WHITE 0xFFFFFF
#define BLACK 0x000000

typedef struct Window {
    PMXDisplay *display;
    int window_borderless;
    int window_minimized;
    int window_fullscreen;
    int window_resizable;
    char *window_title;
    int initialized;
} Window;

extern Window pmx_window;

Window *create_window(PMXDisplay *display, int window_borderless);
void update_window();
void destroy_window();

#endif