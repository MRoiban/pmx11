/**
 * @file display.c
 * @brief Implementation file for the display module.
 *
 * This file contains the implementation of functions related to the display
 * module. The display module is responsible for rendering graphics on the
 * screen using SDL library.
 */

#include "./display.h"
#include "../pmx.h"
#include "../utils.h"
#include "display.h"
#include <SDL.h>
#include <stdio.h>
#include <string.h>

#define SCREEN_WIDTH 800
#define SCREEN_HEIGHT 600

// Define display device memory addresses
#define DISPLAY_POWER_ADDR 0x10
#define DISPLAY_CLEAR_ADDR 0x11
#define DISPLAY_CHAR_ADDR 0x12
#define DISPLAY_MOUSE_ADDR 0x13
#define DISPLAY_PIXEL_ADDR 0x14
#define DISPLAY_LINE_ADDR 0x15
#define DISPLAY_RECT_ADDR 0x16
#define DISPLAY_RECTFILL_ADDR 0x17
#define DISPLAY_HELLO_ADDR 0x18
#define DISPLAY_SPRINT_ADDR 0x19

// Display parameter memory locations
#define PARAM_BASE_ADDR 0x100
#define PARAM_X 0x100
#define PARAM_Y 0x101
#define PARAM_W 0x102
#define PARAM_H 0x103
#define PARAM_S 0x104
#define PARAM_C 0x105

enum ALPHABET_ENUM {
    SPACE,
    A,
    B,
    C,
    D,
    E,
    F,
    G,
    H,
    I,
    J,
    K,
    L,
    M,
    N,
    O,
    P,
    Q,
    R,
    S,
    T,
    U,
    V,
    W,
    X,
    Y,
    Z
};

struct numbers {
    const char *bitmap[5];
    int height;
    int width;
} numbers = {.bitmap = {"00001001110011100101001110011100111001110011100111",
                        "00011000010000100101001000010000001001010010100101",
                        "00001001110001100111001110011100011001110011100101",
                        "00001001000000100001000010010100001001010000100101",
                        "00001001110011100001001110011100001001110011100111"},
             .height = 5,
             .width = 100};

struct alphabet {
    const char *bitmap[5];
    int height;
    int width;
} alphabet = {
    .bitmap =
        {
            "000000111011110011101111011111111110111110001111111111110001100001"
            "101111001011101111001110111101111111111100011000110001100011000111"
            "111",
            "000001000110001100011000110000100001000010001001000001010010100001"
            "010110101100011000110001100011000000100100011000110001010100101000"
            "001",
            "000001111111110100001000111110111101001111111001000001011100100001"
            "000110101100011111010101111101111100100100011000110001001000010001"
            "110",
            "000001000110001100011000110000100001000110001001000001010010100001"
            "000110101100011000010010100010000100100100010101010101010100010010"
            "000",
            "000001000111110011101111011111100000111110001111111110010001111111"
            "000110011011101000001101100011111100100111110010011011100010010011"
            "111",
        },
    .height = 5,
    .width = 130,
};

struct cursor {
    const char *bitmap[5];
    int height;
    int width;
} cursor = {.bitmap =
                {
                    "11110",
                    "11000",
                    "10100",
                    "10010",
                    "00001",
                },
            .height = 5,
            .width = 5};

#define ALPHABET_NUMBER 37
const AlphabetMapping alphabet_map[ALPHABET_NUMBER] = {
    {0x00, " "}, {0x01, "A"}, {0x02, "B"}, {0x03, "C"}, {0x04, "D"},
    {0x05, "E"}, {0x06, "F"}, {0x07, "G"}, {0x08, "H"}, {0x09, "I"},
    {0x0A, "J"}, {0x0B, "K"}, {0x0C, "L"}, {0x0D, "M"}, {0x0E, "N"},
    {0x0F, "O"}, {0x10, "P"}, {0x11, "Q"}, {0x12, "R"}, {0x13, "S"},
    {0x14, "T"}, {0x15, "U"}, {0x16, "V"}, {0x17, "W"}, {0x18, "X"},
    {0x19, "Y"}, {0x1A, "Z"}, {0x1B, "1"}, {0x1C, "2"}, {0x1D, "3"},
    {0x1E, "4"}, {0x1F, "5"}, {0x20, "6"}, {0x21, "7"}, {0x22, "8"},
    {0x23, "9"}, {0x24, "0"}, 
};


#define COLORS 7
const ColorMapping colors_map[COLORS] = {
    {"WHITE", 0xFFFFFF}, {"BLACK", 0x000000},  {"RED", 0xFF0000},    {"GREEN", 0x00FF00},
    {"BLUE", 0x0000FF},  {"YELLOW", 0xFFFF00}, {"MAGENTA", 0xFF00FF}};

PMXDisplay pmx_display = {
    .width = SCREEN_WIDTH,
    .height = SCREEN_HEIGHT,
    .pixels = NULL, // Initialize with the correct size
    .background = NULL,
    .power = 0,
    .bool_update = 0,
};
static SDL_Window *window;
static SDL_Renderer *renderer;
static SDL_Texture *texture = NULL;
static SDL_Surface *screenSurface = NULL;

/**
 * @brief Update the display background
 *
 * @param bg Background color
 */
void
updateDisplayBg(Uint32 bg) {
    // This function is now redundant with our improved double buffering
    // Just keep it as a no-op for backward compatibility
}

char uppercase(char c) {
    if (c >= 'a' && c <= 'z') {
        return c - 32;
    }
    return c;
}

Uint8 *str_to_hex_array(char *str, Uint8 *array) {
    for (int i = 0; i < strlen(str); i++) {
        array[i] = char_to_hex(uppercase(str[i]));
        // printf("str[%d]:%c turns to %x\n", i, str[i], array[i]);
    }
    return array;
}




/**
 * @brief Convert 24-bit RGB color (0xRRGGBB) to 12-bit RGB444 format for SDL
 *
 * @param color 24-bit RGB color value
 * @return Uint16 12-bit RGB444 color value
 */
Uint16 convertRGBtoRGB444(Uint32 color) {
    // Extract 8-bit RGB components
    Uint8 r = (color >> 16) & 0xFF;
    Uint8 g = (color >> 8) & 0xFF;
    Uint8 b = color & 0xFF;
    
    // Convert 8-bit (0-255) to 4-bit (0-15)
    Uint16 r4 = r >> 4;
    Uint16 g4 = g >> 4;
    Uint16 b4 = b >> 4;
    
    // Combine into RGB444 format (12-bit)
    return (r4 << 8) | (g4 << 4) | b4;
}

/**
 * @brief Draw a pixel on the display
 *
 * @param x The x-coordinate of the pixel
 * @param y The y-coordinate of the pixel
 * @param scale The scale factor of the pixel
 * @param color The color of the pixel
 */
void drawPixel(int x, int y, int scale, Uint32 color) {
    // Safety check to prevent buffer overflows
    if (x < 0 || y < 0 || 
        x >= pmx_display.width || 
        y >= pmx_display.height) {
        // print("drawPixel: out of bounds");
        return;
    }
    
    // Convert 24-bit RGB to 12-bit RGB444
    Uint16 rgb444 = convertRGBtoRGB444(color);
    
    for (int i = 0; i < scale; i++) {
        for (int j = 0; j < scale; j++) {
            // Calculate the actual screen coordinates
            int screenX = x * scale + i;
            int screenY = y * scale + j;
            
            // Check if the scaled coordinates are within bounds
            if (screenX >= 0 && screenX < pmx_display.width && 
                screenY >= 0 && screenY < pmx_display.height) {
                int index = screenY * pmx_display.width + screenX;
                pmx_display.pixels[index] = rgb444;
            }
        }
    }
}

/**
 * @brief Draw a rectangle on the display
 *
 * @param x The x-coordinate of the rectangle
 * @param y The y-coordinate of the rectangle
 * @param w The width of the rectangle
 * @param h The height of the rectangle
 * @param s The scale factor of the rectangle
 * @param c The color of the rectangle
 */
void
drawRectFill(int x, int y, int w, int h, int s, int c) {
    if (s <= 0)
        return;
    
    // Convert color to RGB444 format
    Uint16 rgb444 = convertRGBtoRGB444(c);
    
    // Draw a filled rectangle by iterating through each pixel
    for (int i = 0; i < w; i++) {
        for (int j = 0; j < h; j++) {
            drawPixel(x + i, y + j, s, c);
        }
    }
}

void 
drawRect(int x, int y, int w, int h, int s, int c) {
    if (s <= 0)
        return;

    // printf("drawRect: x=%d, y=%d, w=%d, h=%d, s=%d, c=%d\n", x, y, w, h, s, c);
    
    // Convert color to RGB444 format
    Uint16 rgb444 = convertRGBtoRGB444(c);

    for (int i = 0; i < w; i++) {
        drawPixel(x + i, y, s, c);
        drawPixel(x + i, y + h - 1, s, c);
    }
    for (int j = 0; j < h; j++) {
        drawPixel(x, y + j, s, c);
        drawPixel(x + w - 1, y + j, s, c);
    }
}

/**
 * @brief Draw a bitmap on the display
 *
 * @param i The x-offset of the bitmap
 * @param j The y-offset of the bitmap
 * @param index The index of the character in the bitmap
 * @param width The width of the bitmap
 * @param bitmap The bitmap data
 * @param rows The number of rows in the bitmap
 * @param cols The number of columns in the bitmap
 * @param scale The scale factor of the bitmap
 * @param color The color of the bitmap
 */
void
drawBitmap(int i, int j, int index, int width, const char *bitmap[], int rows,
           int cols, int scale, Uint32 color) {
    const int startX = width * index;
    const int endX = width * (index + 1);

    for (int y = 0; y < rows; y++) {
        const char *row = bitmap[y];
        for (int x = startX; x < endX; x++) {
            if (row[x] == '1') {
                drawPixel(i + (x - startX), j + y, scale, color);
            }
        }
    }
}

/**
 * @brief Get the index of a character in the alphabet
 *
 * @param letter The character to get the index for
 * @return The index of the character in the alphabet
 */
int
getAlphabetIndex(char letter) {
    // Calculate the index (A -> 0, B -> 1, ..., Z -> 25)
    int index = letter - 'A';

    return index;
}

/**
 * @brief Get the index of a digit in the number bitmap
 *
 * @param digit The digit to get the index for
 * @return The index of the digit in the number bitmap
 */
int
getNumberIndex(char digit) {
    // Calculate the index ('1' -> 0, '2' -> 1, ..., '9' -> 8, '0' -> 9)
    int index;
    if (digit == '0') {
        index = 9; // Special case for '0'
    } else {
        index = digit - '1';
    }

    return index;
}

/**
 * @brief Draw a character on the display
 *
 * @param hex The hex value of the character to draw
 * @param x The x-coordinate of the character
 * @param y The y-coordinate of the character
 * @param scale The scale factor of the character
 * @param color The color of the character
 */
void
drawChar(Uint8 hex, int x, int y, int scale, Uint32 color) {
    // Check if the hex value is valid
    if (hex >= ALPHABET_NUMBER) {
        printf("Unsupported hex value: 0x%02x\n", hex);
        return;
    }
    
    // Find the character index in our alphabet_map
    for (int i = 0; i < ALPHABET_NUMBER; i++) {
        if (alphabet_map[i].hex == hex) {
            // Found the character
            if (hex >= 0x01 && hex <= 0x1A) {
                // It's a letter (A-Z)
                drawBitmap(x, y, i, 5, alphabet.bitmap, alphabet.height,
                          alphabet.width, scale, color);
            } 
            else if (hex >= 0x1B && hex <= 0x24) {
                // It's a number (1-9, 0)
                int numberIndex = hex - 0x1B; // Convert to 0-based index for numbers
                drawBitmap(x, y, numberIndex, 5, numbers.bitmap, numbers.height,
                          numbers.width, scale, color);
            }
            else if (hex == 0x00) {
                // It's a space - nothing to draw
            }
            return; // Exit after drawing
        }
    }
    
    // If we get here, the hex value wasn't found in the map
    printf("Hex value 0x%02x not found in alphabet map\n", hex);
}

/**
 * @brief Draw a string on the display
 *
 * @param string The string to draw
 * @param x The x-coordinate of the string
 * @param y The y-coordinate of the string
 * @param scale The scale factor of the string
 * @param color The color of the string
 */
void
drawString(char string[], int x, int y, int scale, Uint32 color) {
    for (int i = 0; i < strlen(string); i++) {
        // Convert the character to its hex representation
        Uint8 hex = 0;
        for (int j = 0; j < ALPHABET_NUMBER; j++) {
            if (string[i] == *alphabet_map[j].UpLetter) {
                hex = alphabet_map[j].hex;
                break;
            }
        }
        
        drawChar(hex, x, y, scale, color);
        x += 6;
    }
}

/**
 * @brief Draw a string of hex values on the display
 *
 * @param hexString The array of hex values to draw
 * @param length The length of the hex array
 * @param x The x-coordinate of the string
 * @param y The y-coordinate of the string
 * @param scale The scale factor of the string
 * @param color The color of the string
 */
void
drawHexString(Uint8 hexString[], int length, int x, int y, int scale, Uint32 color) {
    for (int i = 0; i < length; i++) {
        drawChar(hexString[i], x, y, scale, color);
        x += 6;
    }
}

/**
 * @brief Shutdown the display and free resources
 */
void
shutdownDisplay() {
    // Release resources in the correct order
    if (texture != NULL) {
        SDL_DestroyTexture(texture);
        texture = NULL;
    }
    
    if (renderer != NULL) {
        SDL_DestroyRenderer(renderer);
        renderer = NULL;
    }
    
    if (window != NULL) {
        SDL_DestroyWindow(window);
        window = NULL;
    }
    
    // Free allocated memory
    if (pmx_display.pixels != NULL) {
        free(pmx_display.pixels);
        pmx_display.pixels = NULL;
    }
    
    if (pmx_display.background != NULL) {
        free(pmx_display.background);
        pmx_display.background = NULL;
    }
    
    pmx_display.power = 0;
    pmx_display.bool_update = 0;
}

/**
 * @brief Initialize the display
 *
 * @param w The width of the display
 * @param h The height of the display
 * @param bg The background color of the display
 */
void
initDisplay(int width, int height, Uint32 bg) {
    // Shutdown any previous display to free resources
    shutdownDisplay();
    
    // Set up display dimensions
    pmx_display.width = width;
    pmx_display.height = height;
    
    // Initialize SDL with video subsystem if not already initialized
    if (SDL_WasInit(SDL_INIT_VIDEO) == 0) {
        if (SDL_InitSubSystem(SDL_INIT_VIDEO) < 0) {
            fprintf(stderr, "SDL could not initialize video! SDL_Error: %s\n", SDL_GetError());
            return;
        }
    }
    
    // Allocate memory for the display buffers with proper alignment
    pmx_display.pixels = 
        (Uint16 *)malloc(width * height * sizeof(Uint16));
    pmx_display.background = 
        (Uint16 *)malloc(width * height * sizeof(Uint16));
        
    if (!pmx_display.pixels || !pmx_display.background) {
        fprintf(stderr, "Failed to allocate memory for display buffers\n");
        shutdownDisplay();
        return;
    }

    // Convert background color to RGB444 format
    Uint16 bg_rgb444 = convertRGBtoRGB444(bg);

    // Initialize both buffers with the background color
    for (int i = 0; i < width * height; i++) {
        pmx_display.pixels[i] = bg_rgb444;
        pmx_display.background[i] = bg_rgb444;
    }

    // Create a window with the correct size and position
    window = SDL_CreateWindow(
        "PMX Virtual Machine", 
        SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, 
        pmx_display.width, pmx_display.height, 
        SDL_WINDOW_SHOWN | (pmx_display.borderless ? SDL_WINDOW_BORDERLESS : 0)
    );
    
    if (window == NULL) {
        fprintf(stderr, "Failed to create window: %s\n", SDL_GetError());
        shutdownDisplay();
        return;
    }

    // Create a renderer with VSync and hardware acceleration
    renderer = SDL_CreateRenderer(
        window, -1, 
        SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC
    );
    
    if (renderer == NULL) {
        fprintf(stderr, "Failed to create renderer: %s\n", SDL_GetError());
        shutdownDisplay();
        return;
    }

    // Set the render logical size to match our pixel dimensions
    SDL_RenderSetLogicalSize(renderer, pmx_display.width, pmx_display.height);
    
    // Create texture with streaming access for efficient updates
    texture = SDL_CreateTexture(
        renderer,
        SDL_PIXELFORMAT_RGB444,  
        SDL_TEXTUREACCESS_STREAMING, 
        pmx_display.width, pmx_display.height
    );
    
    if (texture == NULL) {
        fprintf(stderr, "Unable to create texture: %s\n", SDL_GetError());
        shutdownDisplay();
        return;
    }
    
    // Enable bilinear filtering for smoother scaling
    SDL_SetHint(SDL_HINT_RENDER_SCALE_QUALITY, "1");
    
    // Set power flag and trigger initial update
    pmx_display.power = 1;
    pmx_display.bool_update = 1;
    
    // Initial display update to show the blank screen
    display_update();
}

/**
 * @brief Update the display
 */
void
display_update() {
    // Skip unnecessary updates
    if (!pmx_display.bool_update) {
        return;
    }
    
    // Skip if texture is invalid
    if (texture == NULL) {
        fprintf(stderr, "Cannot update display: texture is NULL\n");
        return;
    }
    
    Uint32 frameStart = SDL_GetTicks();
    
    // Lock the texture before updating it to ensure atomic operations
    void* pixelData;
    int pitch;
    if (SDL_LockTexture(texture, NULL, &pixelData, &pitch) != 0) {
        fprintf(stderr, "Failed to lock texture: %s\n", SDL_GetError());
        return;
    }
    
    // Copy our pixel data to the locked texture memory
    // This ensures the copy is atomic and not visible until presented
    memcpy(pixelData, pmx_display.pixels, pmx_display.width * pmx_display.height * sizeof(Uint16));
    
    // Unlock texture once copying is done
    SDL_UnlockTexture(texture);
    
    // Clear and render in a single step
    SDL_RenderClear(renderer);
    SDL_RenderCopy(renderer, texture, NULL, NULL);
    SDL_RenderPresent(renderer);
    
    // Control frame rate to match monitor refresh rate (typically 60Hz)
    Uint32 frameTime = SDL_GetTicks() - frameStart;
    Uint32 frameDelay = 16; // Target ~60 FPS
    if (frameDelay > frameTime) {
        SDL_Delay(frameDelay - frameTime);
    }
    
    // Reset the update flag only after the complete render cycle
    pmx_display.bool_update = 0;
}

/**
 * @brief Convert a character to hexadecimal
 *
 * @param character The character to convert
 * @return The hexadecimal value of the character
 */
int
char_to_hex(char character) {
    int hex = 0;  // Default value if not found
    for (int i = 0; i < ALPHABET_NUMBER; i++) {
        if (alphabet_map[i].UpLetter && *alphabet_map[i].UpLetter == character) {
            hex = alphabet_map[i].hex;
            break;
        }
    }
    return hex;
}

/**
 * @brief Draw characters in memory on the display
 *
 * @param pmx The PMX virtual machine
 */
void
drawChar_mem(PMX *pmx) {
    int addr = DISPLAY_BLOCK;
    int x;
    int y;
    int scale;
    Uint32 color;
    while (addr < DISPLAY_SIZE && PEEK(addr) != 0) {
        Uint8 hex = PEEK(addr);
        
        if (PEEK(addr + 9) != 1)
            break;

        int flagx = PEEK(addr + 5);
        int flagy = PEEK(addr + 6);
        int flags = PEEK(addr + 7);
        int flagc = PEEK(addr + 8);
        int done = PEEK(addr + 9);

        if (flagx != 0) {
            x = pmx->registers[PEEK(addr + 1) - 1];
        } else {
            x = PEEK(addr + 1);
        }
        if (flagy != 0) {
            y = pmx->registers[PEEK(addr + 2) - 1];
        } else {
            y = PEEK(addr + 2);
        }
        if (flags != 0) {
            scale = pmx->registers[PEEK(addr + 3) - 1];
        } else {
            scale = PEEK(addr + 3);
        }
        if (flagc != 0) {
            color = pmx->registers[PEEK(addr + 4) - 1];
        } else {
            color = PEEK(addr + 4);
        }

        drawChar(hex, x, y, scale, color);

        addr += 10;
    }
}

/**
 * @brief Draw a fixed "HELLO" hex string on the display
 * 
 * @param x The x-coordinate of the string
 * @param y The y-coordinate of the string
 * @param scale The scale factor of the string
 * @param color The color of the string
 */
void
drawHelloHex(int x, int y, int scale, Uint32 color) {
    // Hex values for "HELLO"
    Uint8 hello[] = {0x08, 0x05, 0x0C, 0x0C, 0x0F};
    int length = sizeof(hello) / sizeof(hello[0]);
    // printf("hex:%d\n", length);
    for (int i = 0; i < length; i++) {
        drawChar(hello[i], x, y, scale, color);
        x += 6;
    }
}

/**
 * @brief Handle display DEO instructions
 *
 * @param pmx The PMX virtual machine
 * @param addr The DEO address
 */
void
display_deo(PMX *pmx, Uint8 addr) {
    // Handle various display device operations
    switch (addr) {
    case DISPLAY_POWER_ADDR: // 0x10
        if (pmx_display.power == 0) {
            int width = PEEK2(0x1B);
            int height = PEEK2(0x1C);
            int background = PEEK2(0x1D);
            int borderless = PEEK2(0x1E);
            pmx_display.borderless = borderless;
            
            // Validate dimensions to avoid crashes
            if (width <= 0 || width > 1920) width = SCREEN_WIDTH;
            if (height <= 0 || height > 1080) height = SCREEN_HEIGHT;
            
            initDisplay(width, height, background);
            pmx_display.power = 1;
        }
        else {
            int width = PEEK2(0x1B);
            int height = PEEK2(0x1C);
            int background = PEEK2(0x1D);
            int borderless = PEEK2(0x1E);
            pmx_display.borderless = borderless;
            
            // Validate dimensions to avoid crashes
            if (width <= 0 || width > 1920) width = SCREEN_WIDTH;
            if (height <= 0 || height > 1080) height = SCREEN_HEIGHT;
            
            // Convert background color to RGB444 format
            Uint16 bg_rgb444 = convertRGBtoRGB444(background);

            // Initialize both buffers with the background color
            for (int i = 0; i < width * height; i++) {
                pmx_display.pixels[i] = bg_rgb444;
                pmx_display.background[i] = bg_rgb444;
            }
        }
        break;
        
    case DISPLAY_CLEAR_ADDR: // 0x11
        // Perform a deep copy from background to pixels buffer
        // This operation must be atomic to prevent tearing
        memcpy(pmx_display.pixels, pmx_display.background, pmx_display.width * pmx_display.height * sizeof(Uint16));
        break;
        
    case DISPLAY_CHAR_ADDR: // 0x12
        drawChar_mem(pmx);
        break;
        
    case DISPLAY_MOUSE_ADDR: { // 0x13
        // Draw Mouse - uses the current mouse position from device memory
        int x = PEEK2(0x25);
        int y = PEEK2(0x26);
        drawBitmap(x / 2, y / 2, 0, cursor.width, cursor.bitmap, cursor.height,
                   cursor.width, 2, 0xffffff); // Use full white color which will be converted
        break;
    }
    
    case DISPLAY_PIXEL_ADDR: { // 0x14
        // pixel: x,y,s,c - directly read parameters from memory
        int x = PEEK2(PARAM_X);
        int y = PEEK2(PARAM_Y);
        int s = PEEK2(PARAM_W);  // Scale parameter at 0x102
        int c = PEEK2(PARAM_H);  // Color parameter at 0x103
        drawPixel(x, y, s, c);
        break;
    }
    
    case DISPLAY_LINE_ADDR: { // 0x15
        // line: x1,y1,x2,y2,s,c
        int x1 = PEEK2(PARAM_X);
        int y1 = PEEK2(PARAM_Y);
        int x2 = PEEK2(PARAM_W); // Reusing the W parameter for x2
        int y2 = PEEK2(PARAM_H); // Reusing the H parameter for y2
        int s = PEEK2(PARAM_S);
        int c = PEEK2(PARAM_C);
        drawLine(x1, y1, x2, y2, s, c);
        break;
    }
    
    case DISPLAY_RECT_ADDR: { // 0x16
        // rectangle: x,y,w,h,s,c
        int x = PEEK2(PARAM_X);
        int y = PEEK2(PARAM_Y);
        int w = PEEK2(PARAM_W);
        int h = PEEK2(PARAM_H);
        int s = PEEK2(PARAM_S);
        int c = PEEK2(PARAM_C);
        // Draw the rectangle outline
        // drawLine(x, y, x + w, y, s, c);         // top
        // drawLine(x, y, x, y + h, s, c);         // left
        // drawLine(x, y + h, x + w, y + h, s, c); // bottom
        // drawLine(x + w, y, x + w, y + h, s, c); // right
        drawRect(x, y, w, h, s, c);
        break;
    }
    
    case DISPLAY_RECTFILL_ADDR: { // 0x17
        // rectangle fill: x,y,w,h,s,c
        int x = PEEK2(PARAM_X);    
        int y = PEEK2(PARAM_Y);
        int w = PEEK2(PARAM_W);
        int h = PEEK2(PARAM_H);
        int s = PEEK2(PARAM_S);
        int c = PEEK2(PARAM_C);
        drawRectFill(x, y, w, h, s, c);
        break;
    }
    
    case DISPLAY_HELLO_ADDR: { // 0x18
        // Draw fixed "HELLO" hex string
        int x = 100;
        int y = 100;
        int s = 1;
        int c = 200;
        drawHelloHex(x, y, s, c);
        break;
    }
    
    case DISPLAY_SPRINT_ADDR: { // 0x19
        // sprint: x,y,s,c,string (read from memory)
        int x = PEEK2(PARAM_Y);
        int y = PEEK2(PARAM_W);
        int s = PEEK2(PARAM_H);
        int c = PEEK2(PARAM_S);
        
        // Read hex values from memory starting at PARAM_X
        Uint8 hexString[1]; // Buffer for the hex values
        hexString[0] = PEEK2(PARAM_X);
        
        drawHexString(hexString, 1, x, y, s, c);
        break;
    }
    
    default:
        // Unknown display operation
        return;
    }
    
    // Always mark display for update after any operation
    pmx_display.bool_update = 1;
}

/**
 * @brief Draw a line on the display
 *
 * @param x1 The x-coordinate of the start point
 * @param y1 The y-coordinate of the start point
 * @param x2 The x-coordinate of the end point
 * @param y2 The y-coordinate of the end point
 * @param scale The scale factor of the line
 * @param color The color of the line
 */
void
drawLine(int x1, int y1, int x2, int y2, int scale, int color) {
    int dx = abs(x2 - x1);
    int dy = abs(y2 - y1);
    int sx = (x1 < x2) ? 1 : -1;
    int sy = (y1 < y2) ? 1 : -1;
    int err = dx - dy;
    
    while (1) {
        drawPixel(x1, y1, scale, color);
        
        if (x1 == x2 && y1 == y2) break;
        
        int e2 = 2 * err;
        if (e2 > -dy) {
            if (x1 == x2) break;
            err -= dy;
            x1 += sx;
        }
        if (e2 < dx) {
            if (y1 == y2) break;
            err += dx;
            y1 += sy;
        }
    }
}