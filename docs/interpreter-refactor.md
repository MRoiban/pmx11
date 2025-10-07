# Interpreter Refactor Roadmap

> Scope: Introduce an instruction table and dedicated stack helpers, then split loader/utility code out of `src/pmx.c`.

## Goals

- Replace the switch-based dispatcher in `src/pmx.c` with a data-driven instruction table for easier maintenance and extension.
- Encapsulate stack and register mutations behind helper functions to remove macro side effects.
- Separate program loading, variable management, and memory utilities into focused modules, keeping `pmx.c` responsible solely for VM state and execution.

## Current Pain Points

- The 800+ line `src/pmx.c` mixes VM execution, loaders, and diagnostic helpers, making it hard to reason about behavior changes.
- Macros such as `add(pmx)` and `duplicate(pmx)` mutate `pmx->wst`, `pmx->sp`, and `pmx->pc` implicitly, complicating debugging and testing.
- Instruction decode logic is duplicated between the old `run` loop and the current `step` function, which still relies on a massive `switch` statement.

## Target Architecture

- `src/core/` (new): host `interpreter.c/h` where the instruction table and execution loop live.
- `src/core/stack.c/h`: expose push/pop/peek helpers that validate bounds, update the stack pointer, and emit diagnostics.
- `src/core/loader.c/h`: manage `load_program_from_file`, `load_variables`, and related parsing utilities.
- `src/core/opcodes.c/h`: define opcode metadata, wiring each opcode to an execution callback that accepts `(PMX *pmx)`.
- `src/core/debug.c/h` (optional follow-up): isolate logging/dump helpers currently in `pmx.c`.

## Implementation Steps

1. **Extract Stack Helpers**

   - Move stack/register macros into real functions (`stack_push`, `stack_pop`, etc.) under `src/core/stack.*`.
   - Update instruction implementations to use these helpers and return status codes for overflow/underflow.
2. **Build the Instruction Table**

   - **Create `opcode_handlers[]` mapping opcode bytes to handler structs `{name, execute_fn, cycles}`.**
   - **Port each switch arm in `step` into discrete handler functions stored alongside metadata.**
   - **Keep legacy behavior for error handling (`Warning: Invalid opcode`) via a fallback handler.**
3. **Refactor `step`**

   - Rewrite `step` to: fetch opcode, lookup handler, execute, and conditionally log via `#ifdef LOG_ENABLED`.
   - Ensure PC and SP updates happen *inside* handlers or shared utilities, not in the dispatcher.
4. **Peel Loader/Utility Code**

   - Move `load_program_from_file`, `load_variables`, and variable-table helpers into `src/core/loader.*`.
   - Relocate dump/logging helpers (`dump`, `MAX_LINE_LENGTH` constants) into `debug` module or remove if unused.
   - Update include paths so `pmx.c` only depends on the new headers.
5. **Slim Down `pmx.c`**

   - Leave `pmx.c` with VM struct management (`init_pmx`, `halt`, maybe minimal wrappers).
   - Confirm nothing else in the project includes `pmx.c` headers expecting moved symbols.

## Testing Checklist

- Existing ROMs (e.g., `examples/*.pmx`) execute without behavioral regressions.
- Stack helper unit tests cover overflow/underflow and register access.
- Instruction table dispatch verified via a smoke test that exercises representative opcodes.
- Loader module tested with malformed files to ensure error paths remain intact.

## Notes & Risks

- Watch for macros that rely on expression side effects; when converting to functions, adjust call sites to maintain order of evaluation.
- `PEEK`/`POKE` macros may need to move with stack helpers if they belong to a memory abstraction.
- Expect cyclic include issues while reorganizing; lean on forward declarations and keep headers minimal.
- Plan phased commits: helpers first, then dispatcher swap, then file separation.

## Definition of Done

- `src/pmx.c` drops below ~300 lines and contains only VM lifecycle concerns.
- Instruction additions require only editing the instruction table, not touching the dispatcher.
- No more stack/register mutations hidden inside macros; helper API enforces invariants.
- Documentation updated to reflect the new module layout and build rules.
