#include "window.h"

Window pmx_window = {
    .window_borderless = 0,
    .window_minimized = 0,
    .window_fullscreen = 1,
    .window_resizable = 0,
    .initialized = 0,
    .window_title = "Window",
}; 

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
}

