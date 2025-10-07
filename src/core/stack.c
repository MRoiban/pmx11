#include "stack.h"

#include <string.h>

static int
stack_capacity(void) {
    return MEMORY_SIZE;
}

StackResult
stack_push(PMX *pmx, int reg) {
    if (pmx == NULL) {
        return STACK_ERR_NULL_PMX;
    }

    if (pmx->sp + 1 >= stack_capacity()) {
        return STACK_ERR_OVERFLOW;
    }
    pmx->sp++;
    pmx->wst[pmx->sp] = pmx->registers[reg - 1];
    pmx->pc += 2;
    return STACK_OK;
}

StackResult
stack_pop(PMX *pmx, int reg) {
    if (pmx == NULL) {
        return STACK_ERR_NULL_PMX;
    }

    if (pmx->sp < 0) {
        return STACK_ERR_UNDERFLOW;
    }

    if (reg >= 1 && reg <= REGISTER_NUMBER) {
        pmx->registers[reg - 1] = pmx->wst[pmx->sp];
        pmx->sp--;
    }
    pmx->pc += 2;

    return STACK_OK;
}

StackResult
stack_peek(PMX *pmx, int addr) {
    if (pmx == NULL) {
        return STACK_ERR_NULL_PMX;
    }


    if (addr != NULL) {
        pmx->sp++;
        pmx->wst[pmx->sp] = PEEK(addr);
    }
    pmx->pc+=2;

    return STACK_OK;
}

StackResult
stack_swap(PMX *pmx) {
    if (pmx == NULL) {
        return STACK_ERR_NULL_PMX;
    }

    if (pmx->sp < 1) {
        return STACK_ERR_UNDERFLOW;
    }

    unsigned int top = pmx->wst[pmx->sp--];
    unsigned int under = pmx->wst[pmx->sp--];
    pmx->wst[++pmx->sp] = top;
    pmx->wst[++pmx->sp] = under;
    return STACK_OK;
}

void
stack_reset(PMX *pmx) {
    if (pmx == NULL) {
        return;
    }

    pmx->sp = -1;
    if (pmx->wst != NULL) {
        memset(pmx->wst, 0, stack_capacity() * sizeof(unsigned int));
    }
}

int
stack_size(const PMX *pmx) {
    if (pmx == NULL) {
        return 0;
    }

    return pmx->sp + 1;
}
