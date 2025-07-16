import os, sys

from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

class device_config():
    def get_resolution(self):
        return 800,480

    def load_env_key(self, key: str) -> str:
        load_dotenv(ENV_FILE)
        return os.getenv(key)

    def get_config(self, key: str, default: str):
        return default

device_config = device_config()


### CHANGE THIS FOR TESTING PLUGINS
from plugins.dashboard.dashboard import Dashboard
ENV_FILE = "/app/src/plugins/dashboard/.env.debug"

SETTINGS = {
    "calendar_future_days": 2,
    "lat": 50.775555,
    "long": 6.083611,
    "calendarURLs[]": ["https://horaro.org/vikingtv/test.ical"],
    "calendarColors[]": ["red"]
}

plugin_config = {"id": "dashboard"}
### STOP HERE


plugin_instance = Dashboard(config=plugin_config)
img = plugin_instance.generate_image(settings=SETTINGS, device_config=device_config)
img.save("/app/scripts/out.png")