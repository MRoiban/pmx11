/**
 * @file pmx11.c
 * @brief This file contains the implementation of the PMX11 emulator.
 */

#include "./devices/display.h"
#include "./devices/mouse.h"
#include "./devices/console.h"
#include "./devices/file.h"
#include "./extensions/window.h"
#include "./extensions/gui.h"
#include "./pmx.h"
#include "./emu.h"
#include <SDL.h>
#include <stdio.h>
#include <time.h>

// Device vector addresses (in main memory not dev array)
#define DISPLAY_VECTOR 0x500
#define MOUSE_VECTOR 0x510
#define KEYBOARD_VECTOR 0x520
#define FILE_VECTOR 0x530

// Custom SDL events for device communication
Uint32 display_event, mouse_event, keyboard_event, file_event, gui_event;

// Event data structure to include device address
typedef struct {
    Uint8 deviceAddr;  // Device address for emu_deo
} PMXEventData;

// For accessing vectors, use regular memory instead of device memory
// The vectors are stored as little-endian 16-bit values
#define GET_VECTOR(pmx, addr) (pmx->memory[addr] | (pmx->memory[addr + 1] << 8))



/**
 * @brief Process device events and trigger appropriate vectors
 * 
 * This function checks if there are pending device events and
 * dispatches them to the appropriate device handlers.
 * 
 * @param pmx The PMX structure
 * @param e The SDL event to process
 */
void process_device_events(PMX *pmx, SDL_Event *e) {
    PMXEventData *eventData = NULL;
    
    // Custom PMX device events
    if (e->type == display_event) {
        // SDL_Log("Display event received");
        
        // Extract device address from event data
        eventData = (PMXEventData*)e->user.data1;
        if (eventData && eventData->deviceAddr) {
            // Call device operation directly with the address
            emu_deo(pmx, eventData->deviceAddr);
            // Free the event data when done
            free(eventData);
            e->user.data1 = NULL;
            
            // Ensure the display is updated after processing display events
            if (pmx_display.power == 1) {
                pmx_display.bool_update = 1;
                display_update();
            }
        }
        
        // Trigger vector if available
        if (GET_VECTOR(pmx, DISPLAY_VECTOR) > 0) {
            // Save current PC
            int old_pc = pmx->pc;
            // Jump to vector
            pmx->pc = GET_VECTOR(pmx, DISPLAY_VECTOR);
            // Execute from vector
            step(pmx);
            // Restore PC
            pmx->pc = old_pc;
        }
    }
    else if (e->type == mouse_event) {
        // SDL_Log("Mouse event received");
        
        // Extract device address from event data
        eventData = (PMXEventData*)e->user.data1;
        if (eventData && eventData->deviceAddr) {
            // Call device operation directly with the address
            emu_deo(pmx, eventData->deviceAddr);
            // Free the event data when done
            free(eventData);
            e->user.data1 = NULL;
        }
        
        // Trigger vector if available
        if (GET_VECTOR(pmx, MOUSE_VECTOR) > 0) {
            // Save current PC
            int old_pc = pmx->pc;
            // Jump to vector
            pmx->pc = GET_VECTOR(pmx, MOUSE_VECTOR);
            // Execute from vector
            step(pmx);
            // Restore PC
            pmx->pc = old_pc;
        }
    }
    else if (e->type == keyboard_event) {
        // SDL_Log("Keyboard event received");
        
        // Extract device address from event data
        eventData = (PMXEventData*)e->user.data1;
        if (eventData && eventData->deviceAddr) {
            // Call device operation directly with the address
            emu_deo(pmx, eventData->deviceAddr);
            // Free the event data when done
            free(eventData);
            e->user.data1 = NULL;
        }
        
        // Trigger vector if available
        if (GET_VECTOR(pmx, KEYBOARD_VECTOR) > 0) {
            // Save current PC
            int old_pc = pmx->pc;
            // Jump to vector
            pmx->pc = GET_VECTOR(pmx, KEYBOARD_VECTOR);
            // Execute from vector
            step(pmx);
            // Restore PC
            pmx->pc = old_pc;
        }
    }
    else if (e->type == file_event) {
        // Extract device address from event data
        eventData = (PMXEventData*)e->user.data1;
        if (eventData && eventData->deviceAddr) {
            // Call device operation directly with the address
            emu_deo(pmx, eventData->deviceAddr);
            // Free the event data when done
            free(eventData);
            e->user.data1 = NULL;
        }
        
        // Trigger vector if available
        if (GET_VECTOR(pmx, FILE_VECTOR) > 0) {
            // Save current PC
            int old_pc = pmx->pc;
            // Jump to vector
            pmx->pc = GET_VECTOR(pmx, FILE_VECTOR);
            // Execute from vector
            step(pmx);
            // Restore PC
            pmx->pc = old_pc;
        }
    }
    // Process standard SDL events
    else if (e->type == SDL_MOUSEMOTION || 
             e->type == SDL_MOUSEBUTTONDOWN || 
             e->type == SDL_MOUSEBUTTONUP) {
        // Update mouse state directly from the event
        mouse_event_update(e);
        
        // Push a mouse event to trigger the vector
        SDL_Event mouse_evt;
        // Create event data with device address
        PMXEventData *eventData = malloc(sizeof(PMXEventData));
        eventData->deviceAddr = 0x20;  // Mouse state address
        
        mouse_evt.type = mouse_event;
        mouse_evt.user.data1 = eventData;  // Store eventData in user.data1
        mouse_evt.user.code = 0;
        SDL_PushEvent(&mouse_evt);
    }
    else if (e->type == SDL_KEYDOWN || e->type == SDL_KEYUP) {
        // Push a keyboard event to trigger the vector
        SDL_Event key_evt;
        // Create event data with device address
        PMXEventData *eventData = malloc(sizeof(PMXEventData));
        eventData->deviceAddr = 0x30;  // Keyboard address
        
        key_evt.type = keyboard_event;
        key_evt.user.data1 = eventData;  // Store eventData in user.data1
        key_evt.user.code = 0;
        SDL_PushEvent(&key_evt);
    }
    else if (e->type == gui_event) {
        eventData = (PMXEventData*)e->user.data1;
        if (eventData && eventData->deviceAddr) {
            // Call device operation directly with the address
            emu_deo(pmx, eventData->deviceAddr);
            // Free the event data when done
            free(eventData);
            e->user.data1 = NULL;
        }
    }
}

/**
 * @brief Free all pending events to prevent memory leaks
 * 
 * This function flushes the event queue and frees any event data
 * before the program exits.
 */
void cleanup_events() {
    SDL_Event e;
    
    // Process all pending events and free their data
    while (SDL_PollEvent(&e)) {
        if (e.type == display_event || e.type == mouse_event || 
            e.type == keyboard_event || e.type == file_event) {
            if (e.user.data1 != NULL) {
                free(e.user.data1);
                e.user.data1 = NULL;
            }
        }
    }
}

/**
 * @brief Handle direct device write operations
 * 
 * This function is called when a device memory location is written to,
 * triggering the appropriate device handler immediately.
 * 
 * @param pmx The PMX structure
 */
void handle_device_writes(PMX *pmx) {
    // We'll still handle critical operations immediately and also push events
    if (PEEK2(0x02) == 1) {  // Console write integer
        // Push an event with the device address
        SDL_Event event;
        PMXEventData *eventData = malloc(sizeof(PMXEventData));
        eventData->deviceAddr = 0x02;  // Console write integer address
        
        event.type = display_event;
        event.user.data1 = eventData;
        event.user.code = 0;
        SDL_PushEvent(&event);
        
        POKE2(0x02, 0);      // Reset the trigger
    }
    // Handle display operations
    if (PEEK2(0x10) == 1) {  // Display power
        // Push an event with the device address
        SDL_Event event;
        PMXEventData *eventData = malloc(sizeof(PMXEventData));
        eventData->deviceAddr = 0x10;  // Display power address
        
        event.type = display_event;
        event.user.data1 = eventData;
        event.user.code = 0;
        SDL_PushEvent(&event);
        
        POKE2(0x10, 0);      // Reset the trigger
    }
    
    if (PEEK2(0x11) == 1) {  // Display clear
        // Push an event with the device address
        SDL_Event event;
        PMXEventData *eventData = malloc(sizeof(PMXEventData));
        eventData->deviceAddr = 0x11;  // Display clear address
        
        event.type = display_event;
        event.user.data1 = eventData;
        event.user.code = 0;
        SDL_PushEvent(&event);
        
        POKE2(0x11, 0);      // Reset the trigger
    }
    // if (PEEK2(0x13) == 1) {  // Display clear
    //     // Push an event with the device address
    //     SDL_Event event;
    //     PMXEventData *eventData = malloc(sizeof(PMXEventData));
    //     eventData->deviceAddr = 0x13;  // Display clear address
        
    //     event.type = display_event;
    //     event.user.data1 = eventData;
    //     event.user.code = 0;
    //     SDL_PushEvent(&event);
        
    //     POKE2(0x13, 0);      // Reset the trigger
    // }
    
    // Check for drawing operations
    if (PEEK2(0x14) == 1) {  // Pixel drawing
        // Push an event with the device address
        SDL_Event event;
        PMXEventData *eventData = malloc(sizeof(PMXEventData));
        eventData->deviceAddr = 0x14;  // Pixel address
        
        event.type = display_event;
        event.user.data1 = eventData;
        event.user.code = 0;
        SDL_PushEvent(&event);
        
        POKE2(0x14, 0);      // Reset the trigger
    }
    
    if (PEEK2(0x15) == 1) {  // Line drawing
        // Push an event with the device address
        SDL_Event event;
        PMXEventData *eventData = malloc(sizeof(PMXEventData));
        eventData->deviceAddr = 0x15;  // Line address
        
        event.type = display_event;
        event.user.data1 = eventData;
        event.user.code = 0;
        SDL_PushEvent(&event);
        
        POKE2(0x15, 0);      // Reset the trigger
    }
    
    if (PEEK2(0x16) == 1) {  // Rectangle drawing
        // Push an event with the device address
        SDL_Event event;
        PMXEventData *eventData = malloc(sizeof(PMXEventData));
        eventData->deviceAddr = 0x16;  // Rectangle address
        
        event.type = display_event;
        event.user.data1 = eventData;
        event.user.code = 0;
        SDL_PushEvent(&event);
        
        POKE2(0x16, 0);      // Reset the trigger
    }
    
    if (PEEK2(0x17) == 1) {  // Filled rectangle drawing
        // Push an event with the device address
        SDL_Event event;
        PMXEventData *eventData = malloc(sizeof(PMXEventData));
        eventData->deviceAddr = 0x17;  // Filled rectangle address
        
        event.type = display_event;
        event.user.data1 = eventData;
        event.user.code = 0;
        SDL_PushEvent(&event);
        
        POKE2(0x17, 0);      // Reset the trigger
    }

    if (PEEK2(0x50) == 1) {  // GUI drawing
        // Push an event with the device address
        SDL_Event event;
        PMXEventData *eventData = malloc(sizeof(PMXEventData));
        eventData->deviceAddr = 0x50;  // GUI address
        
        event.type = display_event;
        event.user.data1 = eventData;
        event.user.code = 0;
        SDL_PushEvent(&event);
        
        POKE2(0x50, 0);      // Reset the trigger
    }
}

/**
 * @brief Run the PMX11 emulator.
 *
 * This function runs the PMX11 emulator. It initializes the necessary
 * components, loads the program from a file, and enters the main loop where it
 * processes events, executes the program, updates the display, and
 * handles device operations using an event-driven approach.
 *
 * @param pmx The PMX structure.
 */
void
emu_run(PMX *pmx) {
    SDL_Event e;
    int quit = 0;
    // Register custom event types for device communication
    display_event = SDL_RegisterEvents(1);
    mouse_event = SDL_RegisterEvents(1);
    keyboard_event = SDL_RegisterEvents(1);
    file_event = SDL_RegisterEvents(1);
    
    // Load the program
    load_program_from_file(pmx, pmx->table, "./build/program.rom");
    
    // Initialize frame timing
    Uint64 frame_interval = SDL_GetPerformanceFrequency() / 60;
    Uint64 next_refresh = SDL_GetPerformanceCounter() + frame_interval;
    
    // MAIN LOOP
    while (!quit) {
        // Process all pending events
        while (SDL_PollEvent(&e)) {
            if (e.type == SDL_QUIT) {
                quit = 1;
                // Dump memory to file in a readable format
                FILE *file = fopen("build/memory.dump", "w");
                if (file) {
                    for (int i = 0; i < MEMORY_SIZE; i++) {
                        // Print address at the start of each line
                        if (i % 16 == 0) {
                            if (i > 0) fprintf(file, "\n");
                            fprintf(file, "0x%08x: ", i);
                        }
                        
                        // Print value in hex format
                        fprintf(file, "%08x ", pmx->memory[i]);
                        
                        // Add extra space in the middle of each line for readability
                        if (i % 16 == 7) fprintf(file, " ");
                    }
                    fclose(file);
                }
                printf("Memory dumped to build/memory.dump\n");
            } else {
                // Process device-specific events
                process_device_events(pmx, &e);
            }
        }
        
        // Execute the next instruction
        step(pmx);
        
        // Handle any immediate device operations
        handle_device_writes(pmx);
        
        // Update display at fixed frame rate
        Uint64 now = SDL_GetPerformanceCounter();
        if (now >= next_refresh) {
            if (pmx_display.power == 1) {
                // display_update();
                if (!pmx_window.initialized) {
                    printf("Display updated\n");
                    create_window(&pmx_display, 0);
                }
                update_window();
                update_gui(pmx);
            }
            next_refresh = now + frame_interval;
        }
        
        // Update time counter
        pmx->time++;
        
        // If no more events, add a small delay to prevent 100% CPU usage
        if (!SDL_PollEvent(NULL)) {
            SDL_Delay(1);
        }
    }
    
    // Free all pending events to prevent memory leaks
    cleanup_events();
}

int
main(int argc, char *args[]) {
    print("PMX11 Emulator - 20 Mar 2025.");
    FILE *file = fopen("build/log.txt", "w");
    if (file == NULL) {
        perror("Error opening file");
        return 0;
    }
    fclose(file);
    
    // Initialize SDL first
    if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_EVENTS) < 0) {
        fprintf(stderr, "SDL could not initialize! SDL_Error: %s\n", SDL_GetError());
        return 1;
    }
    
    PMX pmx;
    VariableTable variable_table;
    init_variable_table(&variable_table);
    init_pmx(&pmx, &variable_table);
    init_gui();
    
    // Initialize mouse after display
    init_mouse(600, 420);
    
  
    // Run the emulator
    emu_run(&pmx);
    
    // Clean up SDL
    SDL_Quit();
    
    return 0;
}