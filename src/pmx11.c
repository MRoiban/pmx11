/**
 * @file pmx11.c
 * @brief This file contains the implementation of the PMX11 emulator.
 */

#include <SDL.h>
#include <stdio.h>
#include <time.h>
#include "./pmx.h"
#include "./devices/display.h"

/**
 * @brief Perform device-specific operations based on the given address.
 *
 * This function performs device-specific operations based on the given address.
 * It sets the address to 0x12, extracts the low nibble of the address, and performs
 * operations based on the extracted value.
 *
 * @param pmx The PMX structure.
 * @param addr The address to perform operations on.
 */
void emu_deo(PMX *pmx, Uint32 addr) {
    addr = 0x12;
    Uint8 lv = (addr >> 4) & 0x0F;
    
    switch (lv)
    {
        case 0x00: break;
        case 0x01: display_deo(pmx,addr); break;
    
    default:
        break;
    }
}

/**
 * @brief Run the PMX11 emulator.
 *
 * This function runs the PMX11 emulator. It initializes the necessary components,
 * loads the program from a file, and enters the main loop where it processes events,
 * executes the program, updates the display, performs device-specific operations,
 * and increments the time counter.
 *
 * @param pmx The PMX structure.
 */
void emu_run(PMX *pmx) {
    SDL_Event e;
    int  quit = 0;
    clock_t start, end;
    int time_units = 0;
    start = clock(); // Get the initial time

    load_program_from_file(pmx, "program.rom");
    
    // MAIN LOOP
    while (!quit) {
        while (SDL_PollEvent(&e)) {if (e.type == SDL_QUIT) quit = 1;}
        run(pmx); 
        display_update();
        emu_deo(pmx, 0x12);
        pmx->time++;
        // printf("time: %d\n", pmx->time);
    }
}

int main(int argc, char* args[] ) {
    PMX pmx;
    init_pmx(&pmx);
    initDisplay(600,420,0x000);
    emu_run(&pmx);
    return 0;
}