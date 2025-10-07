#include "window.h"
#include "../devices/mouse.h"

Window pmx_window = {
    .window_borderless = 0,
    .window_minimized = 0,
    .window_fullscreen = 1,
    .window_resizable = 0,
    .initialized = 0,
    .window_title = "Window",
}; 

// External declaration of the SDL window so we can access it
extern SDL_Window *get_sdl_window();
extern void set_window_position(int x, int y);
extern void get_window_position(int *x, int *y);

void draw_frame() {
    if (!pmx_window.window_borderless) {
        Uint8 WindowTitle[6];
        str_to_hex_array(pmx_window.window_title, WindowTitle);
        // Make sure width is valid before rendering
        if (pmx_display.width <= 0) return;
        
        // Draw the top bar
        drawRectFill(0, 0, 
                    pmx_display.width, 20,
                    1, GREEN);
                    
        // Draw horizontal lines within the bar
        for (int i = 0; i < 4; i++) {
            int y = 6 + i * 2;
            if (y < pmx_display.height) {
                drawLine(0, y, pmx_display.width/2 - 50, y, 1, BLACK);
                drawLine(pmx_display.width/2 + 50, y, pmx_display.width, y, 1, BLACK);  
            }
        }
        drawHexString(WindowTitle, 6, pmx_display.width/2 - 35/2, 6, 1, BLACK);
    }
    drawRect(0,0,pmx_display.width/2,pmx_display.height/2,2,0x000000);
}

void render_frame() {
    if (!pmx_window.initialized) return;
    draw_frame();
    // Set the update flag to ensure the display gets refreshed
    pmx_display.bool_update = 1;
}

// Variables for tracking window dragging
static int drag_start_x = 0;
static int drag_start_y = 0;
static int window_x = 0;
static int window_y = 0;
static int is_dragging = 0;

// Move window to the given position
void move_window(int x, int y) {
    // Use our direct window access function
    set_window_position(x, y);
    
    // Store the current position
    window_x = x;
    window_y = y;
}

// Start window dragging operation
void move_window_to_drag_start(int x, int y) {
    // Check if mouse is in the title bar area (within 20 pixels from the top)
    if (!pmx_window.window_borderless && pmx_mouse.y < 20) {
        // Store the starting position of the drag
        drag_start_x = x;
        drag_start_y = y;
        
        // Get current window position
        get_window_position(&window_x, &window_y);
        
        // Set dragging flag
        is_dragging = 1;
    }
}

// Handle mouse movement during dragging
void move_window_to_drag_end(int x, int y) {
    // Only move if we're currently dragging (we already check for button pressed in update_window)
    if (is_dragging) {
        // Calculate the mouse movement delta
        int delta_x = x - drag_start_x;
        int delta_y = y - drag_start_y;
        
        // Move window to new position
        move_window(window_x + delta_x, window_y + delta_y);
    }
}

Window *create_window(PMXDisplay *display, int window_borderless) {
    pmx_window.display = display;
    pmx_window.window_borderless = window_borderless;
    pmx_window.window_minimized = 0;
    pmx_window.window_fullscreen = 1;
    pmx_window.window_resizable = 0;
    pmx_window.initialized = 1;
    return &pmx_window;
}

void update_window() {
    display_update();
    render_frame();
    
    // Start dragging only when mouse is in title bar
    if (pmx_mouse.y < 20 && !pmx_window.window_borderless && !is_dragging) {
        // Handle window dragging - check if left mouse button was just pressed
        if ((pmx_mouse.buttons & 0x1) && !(pmx_mouse.last_state & 0x1)) {
            move_window_to_drag_start(pmx_mouse.x, pmx_mouse.y);
        }
    }
    
    // Continue dragging regardless of mouse position once started
    if (is_dragging) {
        // Update window position if still dragging
        if (pmx_mouse.buttons & 0x1) {
            move_window_to_drag_end(pmx_mouse.x, pmx_mouse.y);
        } else {
            // If mouse button is released, end dragging
            is_dragging = 0;
        }
    }
}

