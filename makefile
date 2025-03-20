# Compiler and flags
CC = gcc
_CFLAGS = -Wall -Wextra -std=c11
CFLAGS = -std=c11
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
OBJS = utils.o pmx.o console.o mouse.o file.o display.o pmx11.o

# Default target
all: $(EXE)

# Build a specific PMX file
# Usage: make build-pmx FILENAME=path/to/file.pmx
build-pmx:
	@if [ -z "$(FILENAME)" ]; then \
		echo "Error: Please provide a PMX file using FILENAME=path/to/file.pmx"; \
		exit 1; \
	fi
	@echo "Building $(FILENAME)..."
	@mkdir -p ./build
	$(PYTHON) -m pmxlang.main $(FILENAME)
	make start
	@echo "Build complete. Run with: $(EXE)"

# Linking
$(EXE): $(OBJS)
	mkdir -p ./build
	$(PYTHON) ./pmxAssembler.py
	$(CC) $(OBJS) $(SDL) $(LDFLAGS) -o $(EXE)

utils.o: ./src/utils.h ./src/utils.c
	$(CC) $(CFLAGS) -c ./src/utils.c -o utils.o

# Compilation rules
pmx.o: ./src/pmx.c ./src/pmx.h
	if [ "$(LOG_FLAG)" = "--log" ]; then \
		$(CC) $(CFLAGS) -DLOG_ENABLED -c ./src/pmx.c -o pmx.o; \
	else \
		$(CC) $(CFLAGS) -c ./src/pmx.c -o pmx.o; \
	fi

display.o: ./src/devices/display.c ./src/devices/display.h
	$(CC) $(CFLAGS) $(SDL) -c ./src/devices/display.c -o display.o

console.o: ./src/devices/console.c ./src/devices/console.h
	$(CC) $(CFLAGS) -c ./src/devices/console.c -o console.o

mouse.o: ./src/devices/mouse.c ./src/devices/mouse.h
	$(CC) $(CFLAGS) $(SDL) -c ./src/devices/mouse.c -o mouse.o

file.o: ./src/devices/file.c ./src/devices/file.h
	$(CC) $(CFLAGS) $(SDL) -c ./src/devices/file.c -o file.o

pmx11.o: ./src/pmx11.c
	$(CC) $(CFLAGS) $(SDL) -c ./src/pmx11.c -o pmx11.o

start:
	clear
	make clean-all
	make
	make clean-objects
	./build/pmx11

# Clean rules
clean-all:
	$(RM) $(EXE) $(OBJS)

clean-objects:
	$(RM) $(OBJS)

.PHONY: all build-pmx start clean-all clean-objects