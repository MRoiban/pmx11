# Compiler and flags
CC = gcc
CFLAGS = -Wall -Wextra -std=c11

# Platform-specific variables
ifeq ($(OS), Windows_NT)
    SDL = -IC:\mingw_dev_lib\include\SDL2 -LC:\mingw_dev_lib\lib -lmingw32 -lSDL2main -lSDL2
    EXE = ./build/pmx11.exe
    PYTHON = py
    RM = del /Q
else
    CFLAGS += -I/opt/homebrew/opt/sdl2/include/SDL2
    LDFLAGS = -L/opt/homebrew/opt/sdl2/lib -lSDL2
    EXE = ./build/pmx11
    PYTHON = .venv/bin/python3
    RM = rm -f
endif

# Object files
OBJS = pmx.o mouse.o display.o pmx11.o

# Default target
all: $(EXE)

# Linking
$(EXE): $(OBJS)
	mkdir -p ./build
	$(PYTHON) ./pmxAssembler.py
	$(CC) $(OBJS) $(SDL) $(LDFLAGS) -o $(EXE)

# Compilation rules
pmx.o: ./src/pmx.c ./src/pmx.h
	$(CC) $(CFLAGS) -c ./src/pmx.c -o pmx.o

display.o: ./src/devices/display.c ./src/devices/display.h
	$(CC) $(CFLAGS) $(SDL) -c ./src/devices/display.c -o display.o

mouse.o: ./src/devices/mouse.c ./src/devices/mouse.h
	$(CC) $(CFLAGS) $(SDL) -c ./src/devices/mouse.c -o mouse.o

pmx11.o: ./src/pmx11.c
	$(CC) $(CFLAGS) $(SDL) -c ./src/pmx11.c -o pmx11.o

# Clean rules
clean-all:
	$(RM) $(EXE) $(OBJS)

clean-objects:
	$(RM) $(OBJS)