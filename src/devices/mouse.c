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
}

void mouse_update() {
    SDL_Event event;
    while (SDL_PollEvent(&event)) {
        if (event.type == SDL_MOUSEMOTION) {
            pmx_mouse.x = event.motion.x; // Relative x-motion
            pmx_mouse.y = event.motion.y; // Relative y-motion
        } else if (event.type == SDL_MOUSEBUTTONDOWN || event.type == SDL_MOUSEBUTTONUP) {
            int button_flag = (event.button.button == SDL_BUTTON_LEFT) ? 0x1 :
                              (event.button.button == SDL_BUTTON_RIGHT) ? 0x2 : 0x4;
            if (event.type == SDL_MOUSEBUTTONDOWN) {
                pmx_mouse.buttons |= button_flag; // Set button state
            } else {
                pmx_mouse.buttons &= ~button_flag; // Clear button state
            }
        }
    }
}

void
mouse_deo(PMX *pmx, Uint8 addr) {
    // printf("dev: %d\n", pmx->dev[addr]);
    // printf("deo addr: %d\n", pmx->dev[addr]);
    switch (addr) {
    case 0x20:
        pmx->dev[0x25] = pmx_mouse.x;
        pmx->dev[0x26] = pmx_mouse.y;
        pmx->dev[0x27] = pmx_mouse.buttons;
        break;
    case 0x21:
        break;
    case 0x22:
        break;
    default:
        break;
    }
}
