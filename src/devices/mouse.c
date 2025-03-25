#include <SDL.h>
#include "./mouse.h"
#include "../pmx.h"

// Mouse device memory addresses
#define MOUSE_STATE_ADDR 0x20
#define MOUSE_X_ADDR 0x25
#define MOUSE_Y_ADDR 0x26
#define MOUSE_BUTTONS_ADDR 0x27

PMXMouse pmx_mouse = {
    .buttons = 0b000,
    .x = 0,
    .y = 0
};

/**
 * @brief Initialize the mouse
 * 
 * @param w Initial x position (usually half the screen width)
 * @param h Initial y position (usually half the screen height)
 */
void init_mouse(int w, int h) {
    pmx_mouse.x = w/2;
    pmx_mouse.y = h/2;
    SDL_ShowCursor(SDL_ENABLE);  // Show the system cursor
}

/**
 * @brief Update mouse state from SDL event
 * 
 * @param event SDL event containing mouse information
 */
void mouse_event_update(SDL_Event *event) {
    if (event->type == SDL_MOUSEMOTION) {
        pmx_mouse.x = event->motion.x; 
        pmx_mouse.y = event->motion.y; 
    } else if (event->type == SDL_MOUSEBUTTONDOWN || event->type == SDL_MOUSEBUTTONUP) {
        int button_flag = (event->button.button == SDL_BUTTON_LEFT) ? 0x1 :
                          (event->button.button == SDL_BUTTON_RIGHT) ? 0x2 : 0x4;
        if (event->type == SDL_MOUSEBUTTONDOWN) {
            pmx_mouse.buttons |= button_flag; 
        } else {
            pmx_mouse.buttons &= ~button_flag; 
        }
    }
    
    // Device memory is updated in mouse_deo when requested by the program
}

/**
 * @brief Update internal mouse state (called during frame updates)
 */
void mouse_update() {
    // No longer polls events directly - just syncs memory if needed
    // This is kept for backward compatibility but most work is now done
    // in the event-driven system
}

/**
 * @brief Handle mouse device output operations
 * 
 * @param pmx The PMX virtual machine
 * @param addr The mouse device address
 */
void mouse_deo(PMX *pmx, Uint8 addr) {
    switch (addr) {
    case MOUSE_STATE_ADDR: // 0x20
        // Write current mouse state to device memory
        POKE2(MOUSE_X_ADDR, pmx_mouse.x);
        POKE2(MOUSE_Y_ADDR, pmx_mouse.y);
        POKE2(MOUSE_BUTTONS_ADDR, pmx_mouse.buttons);
        if (pmx_mouse.last_state != pmx_mouse.buttons) {
            POKE2(0x14, pmx_mouse.last_state);
            pmx_mouse.last_state = pmx_mouse.buttons;
        }
        POKE2(0x13, 1);
        break;
    // Additional mouse device operations can be added here
    default:
        break;
    }
}
