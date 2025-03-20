#include "../pmx.h"

#ifndef PMX_DISPLAY
#define PMX_DISPLAY

typedef struct AlphabetMapping {
    Uint32 hex;
    char *UpLetter;
} AlphabetMapping;

typedef struct ColorMapping {
    const char *color;
    Uint32 hex;
} ColorMapping;

typedef struct PMXDisplay {
    int width, height, x1, x2, y1, y2, scale;
    Uint32 palette[4];
    Uint16 *pixels;
    Uint16 *background;
    Uint8 *fg, *bg;
    Uint8 power;
    Uint8 borderless;
    Uint8 bool_update;
    int permanent_buffer[DISPLAY_SIZE];
} PMXDisplay;

extern PMXDisplay pmx_display;
void
initDisplay(int w, int h, Uint32 bg);
void
shutdownDisplay();
void
display_update();
void
display_deo(PMX *pmx, Uint8 addr);
void
drawLine(int x2, int x1, int y2, int y1, int s, int c);
int
char_to_hex(char character);

#endif