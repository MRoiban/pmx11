#ifndef UTILS
#define UTILS



#define KILOBYTE (1024 * 64)
#define MEMORY_SIZE (20 * KILOBYTE) // 10 KB memory

#define REGISTER_NUMBER (8)
#define DISPLAY_SIZE (480000)
#define DISPLAY_BLOCK (MEMORY_SIZE - DISPLAY_SIZE)
#define MAX_VARIABLES (256)

typedef unsigned char Uint8;
typedef signed char Sint8;
typedef unsigned short Uint16;
typedef signed short Sint16;
typedef unsigned int Uint32;

typedef struct {
    Uint8 *text;
    int size;
} hexString;

void print(const char* string);

#endif