#include "emu.h"

#include "./devices/display.h"
#include "./devices/mouse.h"
#include "./devices/console.h"
#include "./devices/file.h"
#include "./extensions/gui.h"
#include "./pmx.h"


void
emu_deo(PMX *pmx, Uint32 addr) {
    Uint8 lv = (addr >> 4) & 0x0F;

    switch (lv) {
    case 0x00:
        console_deo(pmx, addr);
        break;
    case 0x01:
        display_deo(pmx, addr);
        break;
    case 0x02:
        mouse_deo(pmx, addr);
        break;
    case 0x03:
        file_deo(pmx, addr);
        break;
    case 0x05:
        gui_deo(pmx, addr);
        break;
    default:
        break;
    }
}
