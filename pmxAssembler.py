#!/usr/bin/env python3
"""
Command-line entry point for the PMX Assembler.
This is maintained for backward compatibility with existing build scripts.
"""

from pmxlang.assembler import assemble

if __name__ == "__main__":
    # Use the new modular assembler with default paths
    assemble("build/program.asm", "./build/program.rom") 