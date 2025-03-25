#include "gui.h"
#include "../devices/mouse.h"
#include "../emu.h"
#include "../pmx.h"

void
init_array(InteractableArray *arr) {
    arr->data = NULL;
    arr->count = 0;
    arr->capacity = 0;
}

void
push_array(InteractableArray *arr, Interactable item) {
    if (arr->count == arr->capacity) {
        size_t new_capacity = arr->capacity ? arr->capacity * 2 : 4;
        Interactable *new_data = (Interactable *)realloc(
            arr->data, new_capacity * sizeof(Interactable));
        if (!new_data) {
            // Handle memory allocation failure (e.g., return an error code)
            return; // or some error handling
        }
        arr->data = new_data;
        arr->capacity = new_capacity;
    }
    arr->data[arr->count++] = item;
}

void
free_array(InteractableArray *arr) {
    free(arr->data);
    arr->data = NULL;
    arr->count = arr->capacity = 0;
}

Gui pmx_gui = {.interactables = {0}};

void
init_gui() {
    init_array(&pmx_gui.interactables);
}

void
destroy_gui() {
    free_array(&pmx_gui.interactables);
}

int
inArea(Interactable *interactable, int x, int y) {
    return x >= interactable->x && x < interactable->x + interactable->width &&
           y >= interactable->y && y < interactable->y + interactable->height;
}


void
drawButton(Interactable *interactable) {
    drawRect(interactable->x, interactable->y, interactable->width,
             interactable->height, 1, BLACK);
    if (interactable->string.size != 0) {
        drawHexString(interactable->string.text, interactable->string.size, interactable->x + interactable->width / 4, interactable->y + interactable->height / 3 +2, 1, BLACK);
    }
    pmx_display.bool_update = 1;
}

void
update_gui(PMX *pmx) {
    for (int i = 0; i < pmx_gui.interactables.count; i++) {
        Interactable *interactable = &pmx_gui.interactables.data[i];
        switch (interactable->type) {
        case BUTTON:
            // printf("Button:\n x:%d, y:%d, width:%d, height:%d, id:%d, string_size: %d\n", interactable->x, interactable->y, interactable->width, interactable->height, interactable->id, interactable->string.size);
            if (inArea(interactable, pmx_mouse.x, pmx_mouse.y)) {
                if (pmx_mouse.buttons & 0x01) {
                    if (pmx_mouse.last_state != pmx_mouse.buttons) {
                        print("Button clicked\n");
                        POKE2(0x5a, interactable->id);
                        emu_deo(pmx, interactable->function_addr);
                    }
                }
            }
            drawButton(interactable);
            break;
        case LABEL:
            break;
        case TEXT:
            break;
        }
    }
}

void
register_interactable(Interactable *interactable) {
    push_array(&pmx_gui.interactables, *interactable);
}

void
gui_deo(PMX *pmx, Uint32 addr) {
    // 0x5a: current Button ID clicked
    switch (addr) {
    case 0x50: {
        print("GUI: Registering interactable");
        int type = PEEK2(0x100); // type: 0 (Button),1 (Label),2 (Text)
        int x = PEEK2(0x101);
        int y = PEEK2(0x102);
        int width = PEEK2(0x103);
        int height = PEEK2(0x104);
        int function_addr = PEEK2(0x105);
        int id = PEEK2(0x106);
        int size = PEEK2(0x107);
        
        Interactable interactable = {
            .x = x,
            .y = y,
            .width = width,
            .height = height,
            .function_addr = function_addr,
            .type = (enum InteractableType)type,
            .id = id == 0 ? pmx_gui.interactables.count : id,
            .string = {0}
        };
        
        if (size != 0) {
            // read size bytes from memory, they are char as hex
            hexString string = {0};
            string.size = size;
            string.text = (Uint8 *)malloc(size * sizeof(Uint8));
            
            if (string.text) {
                for (int i = 0; i < size; i++) {
                    string.text[i] = PEEK2(0x108 + i);
                }
                interactable.string = string;
            } else {
                // Handle memory allocation failure
                string.size = 0;
            }
        }
        
        // Register the fully populated interactable
        register_interactable(&interactable);
        break;
    }
    default:
        break;
    }
}
