#include "../pmx.h"

#ifndef PMX_DISPLAY
#define PMX_DISPLAY


typedef struct ColorMapping {
    const char *color;
    Uint32 hex;
} ColorMapping;


typedef struct PMXDisplay {
    int width, height, x1, x2, y1, y2, scale;
    Uint32 palette[4];
    Uint16 *pixels;
    Uint8 *fg, *bg;
} PMXDisplay;

extern PMXDisplay pmx_display;
void initDisplay(int w, int h, Uint32 bg);
void display_update(); 

#endif 