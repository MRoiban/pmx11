#include <SDL.h>
#include <stdio.h>
#include <time.h>
#include "./pmx.h"
#include "./devices/display.h"

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