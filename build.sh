#!/bin/bash

# Parse command line arguments
FILENAME=""
LOG_FLAG=""

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --filename)
            FILENAME="$2"
            shift
            ;;
        --log)
            LOG_FLAG="--log"
            ;;
        *)
            echo "Unknown parameter: $1"
            exit 1
            ;;
    esac
    shift
done

# Check if filename was provided
if [ -z "$FILENAME" ]; then
    echo "Error: Please provide a filename with --filename parameter"
    echo "Usage: ./build.sh --filename path/to/file.pmx"
    exit 1
fi

# Check if file exists
if [ ! -f "$FILENAME" ]; then
    echo "Error: File '$FILENAME' not found"
    exit 1
fi

# Check if file has .pmx extension
if [[ ! "$FILENAME" == *.pmx ]]; then
    echo "Error: File must have .pmx extension"
    exit 1
fi

# Build the PMX file using the makefile
make build-pmx FILENAME="$FILENAME" LOG_FLAG="$LOG_FLAG" 