# InkyPi in Podman

This document describes how to build and run InkyPi as container

## Building InkyPi

`podman build --jobs=2 -t inkypi .`

## Running InkyPi
with persistent config
make sure `/my/inkypi/config/dir` exists before starting the container

`podman run -p 80:80 --volume /my/inkypi/config/dir:/config --device=/dev/spidev0.0 --device=/dev/gpiomem inkypi`

## Running in Dev-Mode

This can be used to debug the flask application / settings page of a plugin on a machine not connected to a display

`podman run -p 80:80 -e INKYPI_DEV_MODE=yes inkypi`