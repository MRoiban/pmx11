#include "window.h"
#include <stdlib.h>
#include <stdint.h>

#ifndef GUI_H
#define GUI_H

enum InteractableType {
    BUTTON,
    LABEL,
    TEXT,
};

typedef struct {
    int x;
    int y;
    int height;
    int width;
    int function_addr;
    int id;
    hexString string;
    int dirty;
    enum InteractableType type;
} Interactable;

// dynamic array for Interactable

typedef struct {
    Interactable *data;
    int count;
    int capacity;
} InteractableArray;

typedef struct Gui {
    InteractableArray interactables;
} Gui;

extern Gui pmx_gui;


void init_gui();
void update_gui();
void destroy_gui();
Interactable create_interactable(Interactable *interactable);
void register_interactable(Interactable *interactable);
void gui_deo(PMX *pmx, Uint32 addr);



#endif 