# USAGE
# podman build -f scripts/Dockerfile .
# podman run -it --rm -v .:/app:Z <CONTAINER_HASH>
# /venv/bin/python3 /app/scripts/test_plugin2.py

FROM docker.io/library/debian:bookworm-slim

RUN apt-get update -y \
    && apt-get --no-install-recommends install -y chromium-headless-shell python3-full python3-pip python3-dev build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \

WORKDIR /app

COPY install/requirements.txt /tmp/requirements.txt

RUN python3 -m venv /venv \
    && /venv/bin/pip install --no-cache-dir -r /tmp/requirements.txt

ENV SRC_DIR="/app/src"

ENTRYPOINT ["bash"]