FROM docker.io/library/python:3.13 as builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY install/requirements.txt /tmp/requirements.txt

RUN uv venv && uv pip install -r /tmp/requirements.txt

#----------------

FROM docker.io/library/python:3.13-slim-bookworm

RUN apt-get update -y \
    && apt-get --no-install-recommends install -y chromium-headless-shell \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY --from=builder /app/.venv /venv

ENV SRC_DIR="/app/src"
ENV PATH="/venv/bin:$PATH"

WORKDIR /app

COPY src/ /app/src
COPY install/config_base/device.json /tmp/
COPY --chmod=700 docker-entrypoint.sh .

EXPOSE 80

ENTRYPOINT ["/app/docker-entrypoint.sh"]