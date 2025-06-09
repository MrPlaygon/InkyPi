from plugins.base_plugin.base_plugin import BasePlugin
from PIL import Image, ImageDraw, ImageFont
import requests
import textwrap

SUPPORTED_LANGUAGES = ["de", "en"]  # According to website

class UselessFacts(BasePlugin):

    def generate_settings_template(self):
        template_params = super().generate_settings_template()
        template_params['languages'] = sorted(SUPPORTED_LANGUAGES)
        return template_params

    def generate_image(self, settings, device_config):
        width, height = 800, 480

        # API URL
        url = f"https://uselessfacts.jsph.pl/api/v2/facts/random?language={settings.get('language')}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
        else:
            raise RuntimeError("Could not load fact.")

        text = data.get("text")
        text = textwrap.fill(text, width=70)

        # Create a white background image
        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("DejaVuSans.ttf", 20)  # Has to be ttf for textbbox

        # Get text size using textbbox
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Calculate position to center the text
        x = (width - text_width) // 2
        y = (height - text_height) // 2

        # Draw the text in black
        draw.text((x, y), text, fill="black", font=font)

        return image
