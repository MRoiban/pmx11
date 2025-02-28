#include <SDL.h>
#include "./mouse.h"

PMXMouse pmx_mouse = {
    .buttons = 0b000,
    .x = 0,
    .y = 0
};

void init_mouse(int w, int h) {
    pmx_mouse.x = w/2;
    pmx_mouse.y = h/2;
    SDL_ShowCursor(SDL_DISABLE);
}

void mouse_update() {
    SDL_Event event;
    while (SDL_PollEvent(&event)) {
        if (event.type == SDL_MOUSEMOTION) {
            pmx_mouse.x = event.motion.x; 
            pmx_mouse.y = event.motion.y; 
        } else if (event.type == SDL_MOUSEBUTTONDOWN || event.type == SDL_MOUSEBUTTONUP) {
            int button_flag = (event.button.button == SDL_BUTTON_LEFT) ? 0x1 :
                              (event.button.button == SDL_BUTTON_RIGHT) ? 0x2 : 0x4;
            if (event.type == SDL_MOUSEBUTTONDOWN) {
                pmx_mouse.buttons |= button_flag; 
            } else {
                pmx_mouse.buttons &= ~button_flag; 
            }
        }
    }
}

void
mouse_deo(PMX *pmx, Uint8 addr) {
    switch (addr) {
    case 0x20:
        POKE2(0x25, pmx_mouse.x);
        POKE2(0x26, pmx_mouse.y);
        POKE2(0x27, pmx_mouse.buttons);
        break;
    case 0x21:
        break;
    case 0x22:
        break;
    default:
        break;
    }
}
