#include <dirent.h>
#include <errno.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

#include "file.h"

#define MAX_FILES 1024

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

PMXFile pmxfile[MAX_FILES];

void
file_reset(PMXFile *file) {
    if (file->f != NULL) {
        fclose(file->f);
        file->f = NULL;
    }
    file->state = IDLE;
    file->outside_sandbox = 0;
    memset(file->filename, 0, sizeof(file->filename));
}

static Uint16
file_init(PMXFile *file, char *filename, int max_len) {
    char *p = file->filename;
    int len = sizeof(p);
    if (len > max_len)
        len = max_len;
    while (len) {
        *p++ = *filename++;
        len--;
    }
    return 0;
}

static Uint16
file_write(PMXFile *file, void *src, int len, Uint8 flags) {
    if (file->state != FILE_WRITE) {
        if ((file->f = fopen(file->filename, (flags & 0x01) ? "ab" : "wb")) !=
            NULL) {
            file->state = FILE_WRITE;
        }
    }
    if (file->state == FILE_WRITE)
        fwrite(src, 1, len, file->f);

    return 0;
}

static Uint16
file_read(PMXFile *file, void *dest, int len) {
    if (file->state != FILE_READ) {
        if ((file->f = fopen(file->filename, "rb")) != NULL) {
            file->state = FILE_READ;
        }
    }
    if (file->state == FILE_READ)
        fread(dest, 1, len, file->f);
    return 0;
}

static Uint16
file_delete(PMXFile *file) {
    file_reset(file);
    return unlink(file->filename);
}

void
file_deo(PMX *pmx, Uint8 addr) {
    switch (addr) {
    case 0x30: {
        int addr = PEEK2(0x36);
        int len = PEEK2(0x37);
        char filename[len];
        for (int i = 0; i < len; i++) {
            filename[i] = PEEK(addr + i);
        }
        file_init(&pmxfile[0], filename, len);
        printf("filename: %s\n", pmxfile[0].filename);
        POKE2(0x30, 0);
        break;
    }
    case 0x31:
        file_reset(&pmxfile[0]);
        break;
    case 0x32:
        file_read(&pmxfile[0], &pmx->memory[0x100], PEEK2(0x37));
        break;
    case 0x33:
        file_write(&pmxfile[0], &pmx->memory[0x100], PEEK2(0x37),
                   PEEK2(0x38));
        break;
    case 0x34:
        file_delete(&pmxfile[0]);
        break;
    default:
        break;
    }
}
