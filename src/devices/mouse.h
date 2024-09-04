#include "../pmx.h"
#ifndef PMX_MOUSE
#define PMX_MOUSE

void init_mouse(int w, int h, Uint32 bg);
void mouse_update(); 
void mouse_deo(PMX *pmx, Uint8 addr);

#endif 