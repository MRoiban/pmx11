#include "./pmx.h"
#ifndef EMU_H
#define EMU_H

/**
 * @brief Perform device-specific operations based on the given address.
 *
 * This function performs device-specific operations based on the given address.
 * It directly dispatches to the appropriate device handler based on the address range.
 *
 * @param pmx The PMX structure.
 * @param addr The address to perform operations on.
 */
void
emu_deo(PMX *pmx, Uint32 addr);

#endif