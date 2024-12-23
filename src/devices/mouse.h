#include "../pmx.h"
#ifndef PMX_MOUSE
#define PMX_MOUSE

typedef struct PMXMouse {
    int x, y;
    Uint8 buttons;
} PMXMouse;

extern PMXMouse pmx_mouse;

void
init_mouse(int w, int h);
void
mouse_update();
void
mouse_deo(PMX *pmx, Uint8 addr);

#endif