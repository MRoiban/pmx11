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
#include <SDL.h>
#include <stdio.h>

#define SCREEN_WIDTH 800
#define SCREEN_HEIGHT 600

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
    {0x14, "T"}, {0x15, "U"}, {0x17, "V"}, {0x18, "W"}, {0x19, "X"},
    {0x1A, "Y"}, {0x1B, "Z"}, {0x1C, "1"}, {0x1D, "2"}, {0x1E, "3"},
    {0x1F, "4"}, {0x20, "5"}, {0x21, "6"}, {0x22, "7"}, {0x23, "8"},
    {0x24, "9"}, {0x25, "0"},
};

#define COLORS 7
const ColorMapping colors_map[COLORS] = {
    {"WHITE", 0xfff}, {"BLACK", 0x000},  {"RED", 0xf00},    {"GREEN", 0x0f0},
    {"BLUE", 0x00f},  {"YELLOW", 0xff0}, {"MAGENTA", 0xf0f}};

PMXDisplay pmx_display = {
    .width = SCREEN_WIDTH,
    .height = SCREEN_HEIGHT,
    .pixels = NULL, // Initialize with the correct size
    .power = 0,
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
    screenSurface = SDL_GetWindowSurface(window);
    SDL_UpdateWindowSurface(window);
}

/**
 * @brief Draw a pixel on the display
 *
 * @param x The x-coordinate of the pixel
 * @param y The y-coordinate of the pixel
 * @param scale The scale factor of the pixel
 * @param color The color of the pixel
 */
void
drawPixel(int x, int y, int scale, Uint32 color) {
    for (int i = 1; i < scale + 1; i++) {
        for (int j = 0; j < scale; j++) {
            int x1 = ((x * scale) + (i - 1)) * 800;
            int y1 = (y * scale) + j;
            // printf("x: %d\n", x1);
            // printf("y: %d\n", y1);
            int c1 = x1 + y1;
            // printf("c1: %d\n", c1);
            pmx_display.pixels[c1] = color;
        }
    }
    pmx_display.bool_update = 1;
}

/**
 * @brief Draw a rectangle on the display
 *
 * @param x The x-coordinate of the rectangle
 * @param y The y-coordinate of the rectangle
 * @param width The width of the rectangle
 * @param height The height of the rectangle
 * @param scale The scale factor of the rectangle
 * @param color The color of the rectangle
 */
void
drawRect(int x, int y, int width, int height, int scale, Uint32 color) {
    for (int i = 0; i < width; i++) {
        for (int j = 0; j < height; j++) {
            drawPixel(x + i, y + j, scale, color);
        }
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
    int startX = width * index;
    int endX = width * (index + 1);

    for (int y = 0; y < rows; y++) {
        for (int x = startX; x < endX; x++) {
            if (bitmap[y][x] == '1') {
                int newX = y + j;
                int newY = x - startX + i;
                drawPixel(newX, newY, scale, color);
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
 * @param character The character to draw
 * @param x The x-coordinate of the character
 * @param y The y-coordinate of the character
 * @param scale The scale factor of the character
 * @param color The color of the character
 */
void
drawChar(char character, int x, int y, int scale, Uint32 color) {
    if (character >= 'A' && character <= 'Z') {
        // Character is a letter (A-Z)
        int index = getAlphabetIndex(character) + 1; // Convert to 0-based index
        drawBitmap(x, y, index, 5, alphabet.bitmap, alphabet.height,
                   alphabet.width, scale, color);
    } else if (character >= '0' && character <= '9') {
        // Character is a number (0-9)
        int index = getNumberIndex(character); // Convert to 0-based index
        drawBitmap(x, y, index, 5, numbers.bitmap, numbers.height,
                   numbers.width, scale, color);
    } else {
        // Invalid character or space
        printf("Unsupported character: %c\n", character);
    }
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
    int index;
    for (int i = 0; i < strlen(string); i++) {
        if (string[i] == ' ') {
            index = 0;
        } else {
            index = getAlphabetIndex(string[i]) +
                    1; // +1 because I've assigned 0 to space!
        }
        drawChar(index, x, y, scale, color);
        x += 6;
    }
}

/**
 * @brief Initialize the display
 *
 * @param w The width of the display
 * @param h The height of the display
 * @param bg The background color of the display
 */
void
initDisplay(int w, int h, Uint32 bg) {
    pmx_display.width = SCREEN_WIDTH;
    pmx_display.height = SCREEN_HEIGHT;
    pmx_display.pixels =
        (Uint16 *)malloc(SCREEN_WIDTH * SCREEN_HEIGHT * sizeof(Uint16));

    for (int i = 0; i < SCREEN_WIDTH * SCREEN_HEIGHT; i++) {
        pmx_display.pixels[i] = bg;
        // pmx_display.pixels[i] =0x000;
    }

    // drawString("PMX VIRTUAL MACHINE", 0, 0, 5, colors_map[2].hex);

    // Create a window
    window = SDL_CreateWindow("PMX Virtual Machine", SDL_WINDOWPOS_UNDEFINED,
                              SDL_WINDOWPOS_UNDEFINED, pmx_display.width,
                              pmx_display.height, SDL_WINDOW_SHOWN);
    if (window == NULL) {
        fprintf(stderr, "Failed to create window: %s\n", SDL_GetError());
        SDL_Quit();
    }

    // Create a renderer
    renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);
    if (renderer == NULL) {
        fprintf(stderr, "Failed to create renderer: %s\n", SDL_GetError());
        SDL_DestroyWindow(window);
        SDL_Quit();
    }

    updateDisplayBg(bg);

    texture = SDL_CreateTexture(renderer, SDL_PIXELFORMAT_RGB444,
                                SDL_TEXTUREACCESS_STREAMING, pmx_display.width,
                                pmx_display.height);
    if (texture == NULL) {
        fprintf(stderr, "Unable to create texture: %s\n", SDL_GetError());
        SDL_DestroyRenderer(renderer);
        SDL_DestroyWindow(window);
        SDL_Quit();
    }
}

/**
 * @brief Update the display
 */
void
display_update() {
    if (pmx_display.bool_update) {
        // Check if an update is necessary
        if (SDL_UpdateTexture(texture, NULL, pmx_display.pixels,
                              SCREEN_WIDTH * sizeof(Uint16)) != 0) {
            // Handle error
            fprintf(stderr, "Failed to update texture: %s\n", SDL_GetError());
            return;
        }

        // Clear the renderer, copy the texture, and present the updated frame
        SDL_RenderClear(renderer);
        if (SDL_RenderCopy(renderer, texture, NULL, NULL) != 0) {
            // Handle error
            fprintf(stderr, "Failed to copy texture to renderer: %s\n",
                    SDL_GetError());
            return;
        }
        SDL_RenderPresent(renderer);

        pmx_display.bool_update = 0; // Reset the update flag
    }
}

/**
 * @brief Convert a character to hexadecimal
 *
 * @param character The character to convert
 * @return The hexadecimal value of the character
 */
int
char_to_hex(char character) {
    int hex;
    for (int i = 0; i < ALPHABET_NUMBER; i++) {
        if (alphabet_map[i].UpLetter == character) {
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
    while (addr < DISPLAY_SIZE && PEEK(pmx, addr) != 0) {
        char *c = NULL;
        for (int i = 0; i < ALPHABET_NUMBER; i++) {
            if (alphabet_map[i].hex == PEEK(pmx, addr)) {
                c = alphabet_map[i].UpLetter;
                break;
            }
        }

        if (PEEK(pmx, addr+9) != 1)
            break;

        if (c == NULL)
            break;

        int flagx = PEEK(pmx, addr + 5);
        int flagy = PEEK(pmx, addr + 6);
        int flags = PEEK(pmx, addr + 7);
        int flagc = PEEK(pmx, addr + 8);
        int done = PEEK(pmx, addr + 9);

        if (flagx != 0) {
            x = pmx->registers[PEEK(pmx, addr + 1) - 1];
        } else {
            x = PEEK(pmx, addr + 1);
        }
        if (flagy != 0) {
            y = pmx->registers[PEEK(pmx, addr + 2) - 1];
        } else {
            y = PEEK(pmx, addr + 2);
        }
        if (flags != 0) {
            scale = pmx->registers[PEEK(pmx, addr + 3) - 1];
        } else {
            scale = PEEK(pmx, addr + 3);
        }
        if (flagc != 0) {
            color = pmx->registers[PEEK(pmx, addr + 4) - 1];
        } else {
            color = PEEK(pmx, addr + 4);
        }

        drawChar(*c, x, y, scale, color);

        addr += 10;
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
    // printf("dev: %d\n", pmx->dev[addr]);
    // printf("deo addr: %d\n", pmx->dev[addr]);
    switch (addr) {
    case 0x10:
        if (pmx_display.power == 0) {
            initDisplay(600, 420, 0x000);
            pmx_display.power = 1;
        }
        break;
    case 0x11:
        break;
    case 0x12:
        drawRect(0, 0, 600, 800, 1, 0x000);
        drawChar_mem(pmx);
        break;
    case 0x13: {
        int x = PEEK2(pmx, 0x25);
        int y = PEEK2(pmx, 0x26);
        drawBitmap(x / 2, y / 2, 0, cursor.width, cursor.bitmap, cursor.height,
                   cursor.width, 2, 0xfff);
        break;
    }
    default:
        break;
    }
}