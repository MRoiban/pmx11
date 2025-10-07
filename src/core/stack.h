#ifndef PMX_CORE_STACK_H
#define PMX_CORE_STACK_H

#include "../pmx.h"

/**
 * @brief Result codes for stack helper operations.
 */
typedef enum {
    STACK_OK = 0,
    STACK_ERR_NULL_PMX,
    STACK_ERR_OVERFLOW,
    STACK_ERR_UNDERFLOW,
    STACK_ERR_INVALID_REGISTER,
    STACK_ERR_INVALID_ADDRESS
} StackResult;

StackResult stack_push(PMX *pmx, int reg);
StackResult stack_pop(PMX *pmx, int reg);
StackResult stack_peek(PMX *pmx, int addr);
StackResult stack_swap(PMX *pmx);
void stack_reset(PMX *pmx);
int stack_size(const PMX *pmx);

#endif
