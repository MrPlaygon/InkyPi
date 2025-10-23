#!/usr/bin/env bash

# Check config file
if [ ! -f "/data/device.json" ]; then
    cp /app/device.json /data/
    echo "Copying device.config to /data"
else
    echo "device.json already exists in /data"
fi

# Check env file
if [ ! -f "/data/env" ]; then
    touch /data/env
    echo "Created env file in /data"
else
    echo "env file already exists"
fi

# Start Inkypi
PROGRAM_PATH=/usr/local/inkypi
VENV_PATH="$PROGRAM_PATH/venv_inkypi"

source "$VENV_PATH/bin/activate"

export PROJECT_DIR="$PROGRAM_PATH"
export SRC_DIR="$PROGRAM_PATH/src"

python -u "$(realpath $PROGRAM_PATH/src/inkypi.py)"

deactivate