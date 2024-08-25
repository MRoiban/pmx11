#include <SDL.h>
#include <stdio.h>
#include <time.h>
#include "./pmx.h"
#include "./devices/display.h"

void emu_deo(PMX *pmx, Uint32 addr) {
    addr = 0x12;
    Uint8 lv = (addr >> 4) & 0x0F;
    // printf("dev: %d\n", pmx->dev[addr]);
    // Uint32 port = pmx->dev[component];
    switch (lv)
    {
        case 0x00: break;
        case 0x01: display_deo(pmx,addr); break;
    
    default:
        break;
    }
}


void
emu_run(PMX *pmx) {
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