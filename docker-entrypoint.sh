#!/usr/bin/env bash
set -eu  # Treat unset variables as error & Exit immediately if non-zero status - https://www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html

if [ ! -e "/app/src/config/device.json" ]; then
  if [ ! -e /config/device.json ]; then
    cp /tmp/device.json /config/device.json
  fi
  ln -s /config/device.json /app/src/config/device.json
fi

exec python /app/src/inkypi.py -d
