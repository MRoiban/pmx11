/**
 * @file display.c
 * @brief Implementation file for the display module.
 *
 * This file contains the implementation of functions related to the display module.
 * The display module is responsible for rendering graphics on the screen using SDL library.
 */

#include <SDL.h>
#include <stdio.h>
#include "../pmx.h"
#include "./display.h"

#define SCREEN_WIDTH 800
#define SCREEN_HEIGHT 600


enum ALPHABET_ENUM {
    SPACE, A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z
};




struct alphabet {
    const char* bitmap[5];
    int height;
    int width;
    } 
    alphabet = {
        .bitmap = {
            "000000111011110011101111011111111110111110001111111111110001100001101111001011101111001110111101111111111100011000110001100011000111111",
            "000001000110001100011000110000100001000010001001000001010010100001010110101100011000110001100011000000100100011000110001010100101000001",
            "000001111111110100001000111110111101001111111001000001011100100001000110101100011111010101111101111100100100011000110001001000010001110",
            "000001000110001100011000110000100001000110001001000001010010100001000110101100011000010010100010000100100100010101010101010100010010000",
            "000001000111110011101111011111100000111110001111111110010001111111000110011011101000001101100011111100100111110010011011100010010011111",
        },
        .height = 5,
        .width = 130,
    };

#define ALPHABET_NUMBER 27
const AlphabetMapping alphabet_map[ALPHABET_NUMBER] = {
    {0x00, " "},
    {0x01, "A"},
    {0x02, "B"},
    {0x03, "C"},
    {0x04, "D"},
    {0x05, "E"},
    {0x06, "F"},
    {0x07, "G"},
    {0x08, "H"},
    {0x09, "I"},
    {0x0A, "J"},
    {0x0B, "K"},
    {0x0C, "L"},
    {0x0D, "M"},
    {0x0E, "N"},
    {0x0F, "O"},
    {0x10, "P"},
    {0x11, "Q"},
    {0x12, "R"},
    {0x13, "S"},
    {0x14, "T"},
    {0x15, "U"},
    {0x17, "V"},
    {0x18, "W"},
    {0x19, "X"},
    {0x1A, "Y"},
    {0x1B, "Z"},
};

#define COLORS 7 
const ColorMapping colors_map[COLORS] = {
    {"WHITE", 0xfff},
    {"BLACK", 0x000},
    {"RED", 0xf00},
    {"GREEN", 0x0f0},
    {"BLUE", 0x00f},
    {"YELLOW", 0xff0},
    {"MAGENTA", 0xf0f}
};

PMXDisplay pmx_display = {
    .width = SCREEN_WIDTH,
    .height = SCREEN_HEIGHT,
    .pixels = NULL // Initialize with the correct size
};
static SDL_Window *window;
static SDL_Renderer *renderer;
static SDL_Texture* texture = NULL;
static SDL_Surface* screenSurface = NULL;

void 
updateDisplayBg(Uint32 bg) {
    screenSurface = SDL_GetWindowSurface( window );
    // SDL_FillRect( screenSurface, NULL, SDL_MapRGB( screenSurface->format, 0x00, 0x00, 0x00 ) );
    SDL_UpdateWindowSurface( window );
}

void 
drawPixel(int x, int y, int scale, Uint32 color) {
    for (int i=1; i <scale+1;i++) {
        for (int j=0; j <scale;j++) {
            int x1 = ((x * scale) + (i-1)) * 800;
            int y1 =  (y * scale) + j;
            // printf("x: %d\n", x1);
            // printf("y: %d\n", y1);
            int c1 = x1+y1;
            // printf("c1: %d\n", c1);
            pmx_display.pixels[c1] = color;
        }
    }
}

void 
drawRect(int x, int y, int width, int height, int scale, Uint32 color) {
    for (int i = 0; i<width; i++) {
        for (int j = 0; j<height; j++) {
            drawPixel(x+i, y+j,scale,color);
        }
    }
}


void 
drawBitmap(int i, int j, 
           int index, int width, 
           const char* bitmap[], 
           int rows, int cols, 
           int scale, Uint32 color) 
{
    for (int y = 0; y < rows; y++) {
        for (int x = 0+(width*index); x < (width*(index+1)); x++) {
            if (bitmap[y][x] == '1') {
                int newX = y+j;
                int newY = (x+i)-(width*index);
                drawPixel(newX, newY, scale, color);
            }
        }
    }
}

void
drawChar(int index, int x, int y, int scale, Uint32 color) {
    drawBitmap(x, y, index, 5, alphabet.bitmap, alphabet.height, alphabet.width, scale, color);
}

int 
getAlphabetIndex(char letter) {
    // Calculate the index (A -> 0, B -> 1, ..., Z -> 25)
    int index = letter - 'A';

    return index;
}

void
drawString(char string[], int x, int y, int scale, Uint32 color) {
    int index;
    for (int i = 0; i < strlen(string);i++) {
        if (string[i] == ' '){
            index = 0;
        }
        else {
            index = getAlphabetIndex(string[i])+1; //+1 because i've assigned 0 to space!
        }
        drawChar(index, x, y, scale, color);
        x+=6;
    }
}

void
initDisplay(int w, int h, Uint32 bg) {
    pmx_display.width = SCREEN_WIDTH;
    pmx_display.height = SCREEN_HEIGHT;
    pmx_display.pixels = (Uint16*)malloc(SCREEN_WIDTH * SCREEN_HEIGHT * sizeof(Uint16));
    
    for (int i = 0; i < SCREEN_WIDTH * SCREEN_HEIGHT; i++) {
        pmx_display.pixels[i] = bg;
        // pmx_display.pixels[i] =0x000;
    }

    
    // drawString("PMX VIRTUAL MACHINE", 0, 0, 5, colors_map[2].hex);

    // Create a window
    window = SDL_CreateWindow("PMX Virtual Machine", SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED, pmx_display.width, pmx_display.height, SDL_WINDOW_SHOWN);
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
    
    texture = SDL_CreateTexture(renderer, SDL_PIXELFORMAT_RGB444, SDL_TEXTUREACCESS_STREAMING, pmx_display.width, pmx_display.height);
    if (texture == NULL) {
        fprintf(stderr, "Unable to create texture: %s\n", SDL_GetError());
        SDL_DestroyRenderer(renderer);
        SDL_DestroyWindow(window);
        SDL_Quit();
    }
    
}

void 
display_update() {
    SDL_UpdateTexture(texture, NULL, pmx_display.pixels, SCREEN_WIDTH * sizeof(Uint16));
    SDL_RenderClear(renderer);
    // Clear the renderer, copy the texture, and present the updated frame
    SDL_RenderCopy(renderer, texture, NULL, NULL);
    SDL_RenderPresent(renderer);
}

void 
drawChar_mem(PMX *pmx){
    int index; int scale;
    int x; int y; Uint32 color;
    int new_line = pmx_display.width/scale;
    char *c;
    for (int addr = DISPLAY_BLOCK; addr < DISPLAY_SIZE;){
        if (pmx->memory[addr] != 0) {
            for (int i=0; i<ALPHABET_NUMBER;i++){
           if (alphabet_map[i].hex == pmx->memory[addr]) c = alphabet_map[i].UpLetter;
           if (pmx->memory[addr] == 0) break;
        }
        x = pmx->memory[addr+1];
        pmx->memory[addr+1]++;
        y = pmx->memory[addr+2];
        pmx->memory[addr+2]++;
        scale = pmx->memory[addr+3];
        color = pmx->memory[addr+4];
        index = getAlphabetIndex(*c)+1;
        drawChar(index, x, y, scale, color);
        addr += 5;
        // printf("addr: %d\n", pmx->memory[addr - 1]);
        }
        else break;
    }
}

void 
display_deo(PMX *pmx, Uint8 addr) {
    // printf("dev: %d\n", pmx->dev[addr]);
    // printf("deo addr: %d\n", pmx->dev[addr]);
    switch (addr)
    {
    case 0x10: break;
    case 0x11: break;
    case 0x12: drawRect(0, 0, 600, 800, 1, 0x000); drawChar_mem(pmx); break;
    default:
        break;
    }
}