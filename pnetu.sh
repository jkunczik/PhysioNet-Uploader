#!/bin/bash

CALL_DIR=$PWD

# Change into the scripts root dir
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Test if conda is available
if ! hash conda 2>/dev/null; 
then
    echo "ERROR:  No conda found."
    echo "	Make sure Anaconda or MiniConda is installed."
    echo "	To enable this programm to find an existing installation, either" 
    echo "	run it from a conda prompt, or add the conda executable to PATH."
    exit 1;
fi

# Make conda fully accessible in sub-shell
eval "$(conda shell.bash hook)"


RES=$(conda activate Selenium 2>&1)
if [ "$RES" != "" ]; then
    conda env update -f environment.yml
    RES=$(conda activate Selenium 2>&1)
    if [ "$RES" != "" ]; then
        echo "$RES"
        echo "ERROR: Could not activate environment."
        exit 1; 
    fi
fi
python -m main $CALL_DIR "$@"
conda deactivate
