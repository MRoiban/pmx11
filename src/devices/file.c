#include <stdio.h>
#include <dirent.h>
#include <errno.h>
#include <limits.h>
#include <string.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <unistd.h>

#include "file.h"

typedef struct PMXFile {
    DIR *dir;
    FILE *f;
    char filename[1024];
    struct dirent *de;
    enum state {
        IDLE,
        FILE_READ,
        FILE_WRITE,
    } state;
    int outside_sandbox;
} PMXFile;

void
file_reset() {}

void
file_init() {}

void
file_write() {}

void
file_read() {}

void
file_delete() {}

void
file_deo(PMX *pmx, Uint8 addr) {
    switch (addr) {
    case 0x30:
        file_init();
        break;
    case 0x31:
        file_reset();
        break;
    case 0x32:
        file_read();
        break;
    case 0x33:
        file_write();
        break;
    case 0x34:
        file_delete();
        break;
    default:
        break;
    }
}