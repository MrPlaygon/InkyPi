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

## Testing Plugins

This is mainly used to test chrome-headless html rendering

Settings (for plugin and also display resolution can be changed in `scripts/test_plugin2.py`
Env variables for the plugin can be set in a `.env.debug` file next to the plugins `plugin.py` file

```bash
podman build -f scripts/Dockerfile .
podman run -it --rm -v .:/app:Z <CONTAINER_HASH>

/venv/bin/python3 /app/scripts/test_plugin2.py
```

Image generated is stored in `scripts/out.png`