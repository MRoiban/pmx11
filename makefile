CC = gcc
CFLAGS = -Wall -Wextra -std=c11
SDL = -IC:\mingw_dev_lib\include\SDL2 -LC:\mingw_dev_lib\lib -lmingw32 -lSDL2main -lSDL2

EXE = ./build/pmx11.exe
OBJS = pmx.o display.o pmx11.o

all: $(EXE)

$(EXE): $(OBJS)
	$(CC) $(OBJS) $(SDL) -o $(EXE)

pmx.o: ./src/pmx.c ./src/pmx.h
	$(CC) $(CFLAGS) -c ./src/pmx.c -o pmx.o

display.o: ./src/devices/display.c ./src/devices/display.h
	$(CC) $(CFLAGS) $(SDL) -c ./src/devices/display.c -o display.o

pmx11.o: ./src/pmx11.c 
	$(CC) $(CFLAGS) $(SDL) -c ./src/pmx11.c -o pmx11.o

clean.o:
	rm -f $(OBJS)

clean:
	rm -f $(EXE) $(OBJS)
