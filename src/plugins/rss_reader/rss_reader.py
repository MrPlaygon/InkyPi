from plugins.base_plugin.base_plugin import BasePlugin
from PIL import Image, ImageDraw, ImageFont
import feedparser


class RSSReader(BasePlugin):

    def generate_image(self, settings, device_config):
        width, height = 800, 480

        # Load RSS Feed and use first 5 entries
        feed = feedparser.parse(settings.get("rssUrl"))
        text = ""
        for entry in feed.entries[:5]:  # Limit to first 5 items
            text += entry.title + "\n\n"

        # Create a white background image
        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)

        # Load a font (has to be ttf for textbbox to work)
        font = ImageFont.truetype("DejaVuSans.ttf", 20)

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
