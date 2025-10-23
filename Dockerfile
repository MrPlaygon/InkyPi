FROM docker.io/library/python:3.13-bookworm

COPY install/debian-requirements.txt /tmp/

COPY install/requirements.txt /tmp/

RUN apt-get update -y \
    && xargs -a /tmp/debian-requirements.txt apt-get --no-install-recommends install -y \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY src /usr/local/inkypi/src

RUN python3 -m venv /usr/local/inkypi/venv_inkypi \
    && /usr/local/inkypi/venv_inkypi/bin/python -m pip install --no-cache-dir --upgrade pip setuptools wheel \
    && /usr/local/inkypi/venv_inkypi/bin/python -m pip install --no-cache-dir -r /tmp/requirements.txt

COPY install/config_base/device.json /app/device.json

RUN ln --symbolic /data/device.json /usr/local/inkypi/src/config/device.json

RUN ln --symbolic /data/env /usr/local/inkypi/src/.env

VOLUME /data
#TODO add Volume for static assets (uploaded images)

EXPOSE 80

COPY --chmod=700 docker-entrypoint.sh /app/docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]