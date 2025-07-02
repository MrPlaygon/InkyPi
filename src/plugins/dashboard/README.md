## OS & Hardware Installation

1. Write Raspberry Pi OS (with config for Wifi and SSH) to the SD Card
2. Insert SD Card into Raspberry Pi
3. Connect Raspberry Pi and InkyImpression via GPIO
4. Turn on and connect via SSH (find IP with FritzBox! or `nmap -p 22 192.168.178.0/24`)



## Initial configuration

1. Update the system using `sudo apt update` and `sudo apt upgrade`

2. Change systemd target to not load GUI `systemctl set-default multi-user.target`

3. Disable Swap `sudo systemctl disable dphys-swapfile`

4. Install InkyPi
   ```bash
   git clone https://github.com/MrPlaygon/InkyPi.git
   cd InkyPi
   sudo bash install/install.sh
   ```

5. Add API keys to `/home/pi/InkyPi/.env`

6. Visit http://<ip-address>



## Good to knows

Plugin Location: `/home/pi/InkyPi/src/plugins`

Restart: `sudo systemctl restart inkypi`

Edit venv: `source /usr/local/inkypi/venv_inkypi/bin/activate`

Logs: `journalctl -xeu inkypi --follow`



## Troubleshooting

Error:

```bash
ERROR: THESE PACKAGES DO NOT MATCH THE HASHES FROM THE REQUIREMENTS FILE. If you have updated the package versions, please update the hashes. Otherwise, examine the package contents carefully; someone may have tampered with them.
    numpy from https://files.pythonhosted.org/packages/52/b8/7f0554d49b565d0171eab6e99001846882000883998e7b7d9f0d98b1f934/numpy-2.2.6-cp311-cp311-manylinux_2_17_aarch64.manylinux2014_aarch64.whl:
        Expected sha256 b64d8d4d17135e00c8e346e0a738deb17e754230d7e0810ac5012750bbd85a5a
             Got        627174283b1ddd6e0cd265c30002fe2957fae3a83c5953d0575611c7dd26f36f
```

Solution:

```bash
sudo -i
source "/usr/local/inkypi/venv_inkypi/bin/activate"
pip uninstall Pillow
pip install --no-cache-dir Pillow flask python-dotenv inky requests urllib3 werkzeug pillow pytz openai numpy feedparser
deactivate
exit
sudo systemctl restart inkypi.service
```

https://github.com/fatihak/InkyPi/issues/68



## Sources

- https://learn.pimoroni.com/article/getting-started-with-inky-impression
- https://www.youtube.com/watch?v=65sda565l9Y
- https://github.com/fatihak/InkyPi