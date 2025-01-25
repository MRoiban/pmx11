#include "file.h"

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