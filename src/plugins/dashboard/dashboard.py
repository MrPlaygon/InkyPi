import icalendar
import pytz
from plugins.base_plugin.base_plugin import BasePlugin
import json
from PIL import Image, ImageDraw, ImageFont, ImageColor
from datetime import datetime, timedelta, time
from dateutil import parser
import requests
import logging
from urllib.request import urlopen
from todoist_api_python.api import TodoistAPI
import recurring_ical_events


FONT_NAME = "DejaVuSans.ttf"

# Weather
UNITS = {
    "standard": {
        "temperature": "K",
        "speed": "m/s"
    },
    "metric": {
        "temperature": "°C",
        "speed": "m/s"

    },
    "imperial": {
        "temperature": "°F",
        "speed": "mph"
    }
}

WEATHER_URL = "https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={long}&units={units}&appid={api_key}&cnt=5&lang=de"
WEATHER_ICON_URL = "https://openweathermap.org/img/wn/{icon}@2x.png"

# Todoist
PRIORITY_COLORS = ["red", "yellow", "green", "deepskyblue"]
TODOIST_MAX_TODOS = 10

MAX_CALENDAR_EVENTS = 4  # Max amount of individual events displayed


class Dashboard(BasePlugin):

    def load_font(self, font_size: int):
        try:
            font = ImageFont.truetype(FONT_NAME, size=font_size)
        except:
            font = ImageFont.load_default(size=font_size)

        return font

    def get_font_size_from_height(self, text: str, max_height: int) -> int:
        min_size = 4
        max_size = 128  # Arbitrary upper limit
        best_size = min_size
        height = 0

        while height < max_height:
            best_size += 4
            font = self.load_font(best_size)
            bbox = font.getbbox(text)
            height = bbox[3] - bbox[1]

        return best_size - 4

    def get_font_size_from_width(self, text: str, max_width: int) -> int:
        min_size = 4
        max_size = 128  # Arbitrary upper limit
        best_size = min_size
        width = 0

        while width < max_width:
            best_size += 4
            font = self.load_font(best_size)
            bbox = font.getbbox(text)
            width = bbox[2] - bbox[0]

        return best_size - 4

    # Uses Todoist API key to retrieve todoist tasks an returns list of tasks sorted by priority
    def get_todos(self, api_key: str) -> list[dict]:
        api = TodoistAPI(api_key)
        tasks = api.filter_tasks(query="date: yesterday")

        task_list = []

        for list_of_tasks in tasks:
            for task in list_of_tasks:
                task_dict = {
                    "id": task.id,
                    "content": task.content,  # this
                    "description": task.description,
                    "assignee_id": task.assignee_id,
                    "assigner_id": task.assigner_id,
                    "completed_at": task.completed_at,
                    "created_at": task.created_at,
                    "creator_id": task.creator_id,
                    "deadline": task.deadline,
                    "due": task.due,
                    "duration": task.duration,
                    "is_collapsed": task.is_collapsed,
                    "is_completed": task.is_completed,
                    "labels": task.labels,
                    "meta": task.meta,
                    "order": task.order,
                    "parent_id": task.parent_id,
                    "priority": task.priority,  # this
                    "project_id": task.project_id,
                    "section_id": task.section_id,
                    "updated_at": task.updated_at,
                    "url": task.url
                }
                print(task_dict)
                task_list.append(task_dict)

        task_list.sort(key=lambda t: t.get("priority", 4))
        return task_list[:TODOIST_MAX_TODOS]

    def draw_todos(self, todoist_tasks, draw, position):
        y_anchor = position[1]
        padding = 5
        task_max_height = position[3] - position[1] // 3
        if len(todoist_tasks) < 1:
            return

        task_height = min(((position[3] - position[1]) - (len(todoist_tasks)-1) * padding) // len(todoist_tasks), task_max_height)
        font_size = self.get_font_size_from_height("Ay", task_height - padding * 2)
        for task in todoist_tasks:
            font_size = min(self.get_font_size_from_width(task["content"], (position[2] - position[0] - padding * 2)), font_size)

        font = self.load_font(font_size)
        for task in todoist_tasks:
            draw.rounded_rectangle([position[0], y_anchor, position[2], y_anchor + task_height], fill=PRIORITY_COLORS[task["priority"]-1], radius=10)
            draw.text((position[0] + padding * 2, y_anchor + padding * 2), task["content"], font=font, fill="black", anchor="lt")

            y_anchor += task_height + padding

    def get_weather_data(self, api_key, units, lat, long):
        url = WEATHER_URL.format(lat=lat, long=long, units=units, api_key=api_key)
        response = requests.get(url)
        if not 200 <= response.status_code < 300:
            logging.error(f"Failed to retrieve weather data: {response.content}")
            raise RuntimeError("Failed to retrieve weather data.")
        datapoints = response.json()
        for datapoint in datapoints["list"]:
            dt_obj = datetime.strptime(datapoint["dt_txt"], "%Y-%m-%d %H:%M:%S")
            datapoint["formatted_time"] = dt_obj.strftime("%H:%M")
        return datapoints

    # Draws the events on the canvas
    def draw_calendar_events(self, events, draw, position: list[int], timezone: datetime.tzinfo):
        x0 = position[0]
        y0 = position[1]
        x1 = position[2]
        y1 = position[3]
        height = y1 - y0
        width = x1 - x0
        event_rect_max_height = height // 3

        if len(events) <= 0:
            padding = 20
            font_size = min(self.get_font_size_from_height("Nothing going on today...", event_rect_max_height - padding * 2), self.get_font_size_from_width("Nothing going on today...", width - padding * 2))
            font = self.load_font(font_size)
            draw.rounded_rectangle([x0, y0, x1, y0 + event_rect_max_height], outline="black", radius=5, width=4)
            draw.text((x0 + padding, y0 + padding), "Nothing going on today...", font=font, fill="black")
            return

        event_rect_height = (height - 5 * len(events) + 5) / len(events)
        event_rect_height = min(event_rect_height, event_rect_max_height)

        # Inital values for counting
        y0 = y0 #for understanding only
        y1 = y0 + event_rect_height
        event_padding = event_rect_height // 10 #TODO

        for i, event in enumerate(events):
            draw.rounded_rectangle([x0, y0, x1, y1], outline="black", radius=5, width=4)
            line_height = (event_rect_height - (event_padding * 3)) // 2

            summary_font_size = self.get_font_size_from_height(event["title"], line_height)
            summary_font = self.load_font(summary_font_size)
            draw.text((x0 + event_padding, y0 + event_padding), event["title"], font=summary_font, fill="black", anchor="lt")

            timeslot_string = self.format_datetime(event["start"], timezone) + " - " + self.format_datetime(event["end"], timezone)
            timeslot_font_size = min(self.get_font_size_from_height(timeslot_string, line_height), self.get_font_size_from_width(timeslot_string, x1-x0))
            timeslot_font = self.load_font(timeslot_font_size)
            draw.text((x0 + event_padding, y0 + event_padding + line_height + event_padding), timeslot_string, font=timeslot_font, fill="black", anchor="lt")

            y0 += event_rect_height + 5
            y1 += event_rect_height + 5

    # Helper function to make date readable
    def format_datetime(self, dt: str, timezone: datetime.tzinfo) -> str:
        dt = parser.isoparse(dt)
        dt = dt.astimezone(timezone)
        now = datetime.now()
        if dt.date() == now.date():
            return dt.strftime("%H:%M")
        else:
            return dt.strftime("%d.%m.%Y %H:%M")

    # Helper function to create dict from iCal event (see https://github.com/python-caldav/caldav/blob/master/examples/get_events_example.py)
    def parse_event(self, component, calendar) -> dict[str, str]:
        cur = {}
        cur["calendar"] = f"{calendar}"
        cur["summary"] = component.get("summary")
        cur["description"] = component.get("description")
        cur["location"] = component.get("location")
        cur["start"] = component.start.strftime("%Y-%m-%dT%H:%M")
        end_date = component.end
        if end_date:
            cur["end"] = end_date.strftime("%Y-%m-%dT%H:%M")
        cur["datestamp"] = component.get("dtstamp").dt.strftime("%Y-%m-%dT%H:%M")
        return cur

    def draw_current_date(self, draw, position):
        x0 = position[0]
        y0 = position[1]
        x1 = position[2]
        y1 = position[3]

        padding = (y1 - y0) // 10
        text = datetime.now().strftime("%d.%m.%Y")
        font_size = min(self.get_font_size_from_height(text, (y1-y0)-padding*2), self.get_font_size_from_width(text, x1 - x0))
        font = self.load_font(font_size)
        bbox = font.getbbox(text)
        width = bbox[2] - bbox[0]
        position[2] = x0 + width + padding + padding
        draw.rounded_rectangle(position, outline="blue", radius=7, width=3)
        draw.text((x0 + padding, y0 + padding), text, font=font,
                  fill="black", anchor="lt")

    def get_text_centered_position(self, text, font, position, area_width):
        text_bbox = font.getbbox(text)
        text_width = text_bbox[2] - text_bbox[0]
        text_pos = (position[0] + ((area_width - text_width) // 2), position[1])
        return text_pos

    def draw_weather_data(self, image, draw, position, weather_data):
        element_width = (position[2] - position[0]) // len(weather_data["list"])
        text_height = (position[3] - position[1]) - element_width # available height in pixels from bottom of icon to end of area
        padding = 6
        line_height = (text_height - 4 * padding) // 3
        font_size = min(self.get_font_size_from_height("Ay", line_height), self.get_font_size_from_width("xx.yy °C", element_width - padding * 2))
        font = self.load_font(font_size)

        for i, datapoint in enumerate(weather_data["list"]):
            description_text = datapoint["weather"][0]["description"]
            timestamp_text = datetime.strptime(datapoint["dt_txt"], "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
            temperature_text = str(datapoint["main"]["temp"]) + " °C"
            humidity_text = str(datapoint["main"]["humidity"]) + " %"
            icon_url = WEATHER_ICON_URL.format(icon=datapoint["weather"][0]["icon"])
            print(f"{timestamp_text} - {description_text} - {temperature_text} - {humidity_text} - {icon_url}")

            y_anchor = position[1]

            # Load Icon
            icon = Image.open(urlopen(icon_url))

            # Resize Icon
            icon = icon.resize((element_width, element_width))

            # Paste icon onto image
            icon_position = (position[0] + element_width * i, y_anchor)
            image.paste(icon, icon_position)
            y_anchor += element_width

            # Time
            timestamp_position = (icon_position[0], y_anchor)
            timestamp_position = self.get_text_centered_position(timestamp_text, font, timestamp_position, element_width)
            draw.text(timestamp_position, timestamp_text, font=font, fill="black")
            y_anchor += padding + font.getbbox(timestamp_text)[3] - font.getbbox(timestamp_text)[1]

            # Temperature
            temperature_position = (icon_position[0], y_anchor)
            temperature_position = self.get_text_centered_position(temperature_text, font, temperature_position, element_width)
            draw.text(temperature_position, temperature_text, font=font, fill="black")
            y_anchor += padding + font.getbbox(temperature_text)[3] - font.getbbox(temperature_text)[1]

            # Humidity
            humidity_position = (icon_position[0], y_anchor)
            humidity_position = self.get_text_centered_position(humidity_text, font, humidity_position, element_width)
            draw.text(humidity_position, humidity_text, font=font, fill="black")
            y_anchor += padding + font.getbbox(humidity_text)[3] - font.getbbox(humidity_text)[1]

    def fetch_ics_events(self, calendar_urls, calendar_colors, tz, start, end):
        parsed_events = []

        for calendar_url, color in zip(calendar_urls, calendar_colors):
            cal = self.fetch_calendar(calendar_url)
            events = recurring_ical_events.of(cal).between(start, end)
            contrast_color = self.get_contrast_color(color)

            for event in events:
                start, end, all_day = self.parse_data_points(event, tz)
                parsed_event = {
                    "title": str(event.get("summary")),
                    "start": start,
                    "backgroundColor": color,
                    "textColor": contrast_color,
                    "allDay": all_day
                }
                if end:
                    parsed_event['end'] = end

                parsed_events.append(parsed_event)

        print(parsed_events)
        parsed_events.sort(key=lambda ev: parser.isoparse(ev["start"]).astimezone(tz))

        for event in parsed_events:
            if not event["allDay"]:
                start_dt = parser.isoparse(event["start"]).astimezone(tz)
                event["formatted_start"] = start_dt.strftime("%H:%M")

                if event.get("end"):
                    end_dt = parser.isoparse(event["end"]).astimezone(tz)
                    # Check if it's the same day
                    if start_dt.date() == end_dt.date():
                        event["formatted_end"] = end_dt.strftime("%H:%M")
                    else:
                        event["formatted_end"] = end_dt.strftime("%d.%m.%Y %H:%M")

        return parsed_events

    def fetch_calendar(self, calendar_url):
        try:
            response = requests.get(calendar_url)
            response.raise_for_status()
            return icalendar.Calendar.from_ical(response.text)
        except Exception as e:
            raise RuntimeError(f"Failed to fetch iCalendar url: {str(e)}")

    def get_contrast_color(self, color):
        """
        Returns '#000000' (black) or '#ffffff' (white) depending on the contrast
        against the given color.
        """
        r, g, b = ImageColor.getrgb(color)
        # YIQ formula to estimate brightness
        yiq = (r * 299 + g * 587 + b * 114) / 1000

        return '#000000' if yiq >= 150 else '#ffffff'

    def parse_data_points(self, event, tz):
        all_day = False
        dtstart = event.decoded("dtstart")
        if isinstance(dtstart, datetime):
            start = dtstart.astimezone(tz).isoformat()
        else:
            start = dtstart.isoformat()
            all_day = True

        end = None
        if "dtend" in event:
            dtend = event.decoded("dtend")
            if isinstance(dtend, datetime):
                end = dtend.astimezone(tz).isoformat()
            else:
                end = dtend.isoformat()
        elif "duration" in event:
            duration = event.decoded("duration")
            end = (dtstart + duration).isoformat()
        return start, end, all_day

    def generate_image(self, settings, device_config) -> Image:
        #margins = 10
        #width, height = device_config.get_resolution()

        # Create a white background image
        #image = Image.new("RGB", (width, height), "white")
        #draw = ImageDraw.Draw(image)

        # Calendar view (bottom left)
        timezone = device_config.get_config("timezone", default="America/New_York")
        tz = pytz.timezone(timezone)
        current_dt = datetime.now(tz)
        start = datetime(current_dt.year, current_dt.month, current_dt.day)
        end = start + timedelta(days=int(settings.get("calendar_future_days")))
        calendar_urls = settings.get('calendarURLs[]')
        calendar_colors = settings.get('calendarColors[]')
        if not calendar_urls:
            raise RuntimeError("At least one calendar URL is required")
        for url in calendar_urls:
            if not url.strip():
                raise RuntimeError("Invalid calendar URL")

        events = self.fetch_ics_events(calendar_urls, calendar_colors, tz, start, end)
        print("Events:")
        print(events)
        #print(json.dumps(events, indent=2))
        #self.draw_calendar_events(events, draw, [margins, height // 2, (width-margins*3)//2+margins, height - margins], tz)

        # Today's date (top left)
        #self.draw_current_date(draw, [margins, margins, (width - 3 * margins) // 1.5 + margins, int(height * 0.125 + margins)])

        # Weather (middle left)
        weather_api_key = device_config.load_env_key("WEATHER_API_KEY")
        weather_data = self.get_weather_data(weather_api_key, "metric", settings.get("lat"), settings.get("long"))
        #self.draw_weather_data(image, draw, [margins, int(height * 0.125 + margins + margins), (width-margins*3)//2+margins, (height // 2) - margins], weather_data)
        print("Weather data:")
        print(weather_data)

        #Todoist todos (right)
        todoist_api_key = device_config.load_env_key("TODOIST_API_KEY")
        todoist_tasks = self.get_todos(todoist_api_key)
        #self.draw_todos(todoist_tasks, draw, [(width - 3 * margins) // 2 + 2 * margins, int(height * 0.125 + margins + margins), width - margins, height - margins])
        print("Todoist tasks:")
        print(todoist_tasks)

        # New approach
        template_params = dict()
        template_params["plugin_settings"] = settings
        template_params["events"] = events
        template_params["weather_data"] = weather_data
        template_params["todoist_tasks"] = todoist_tasks
        template_params["current_date"] = datetime.now().strftime("%d.%m.%Y")
        image = self.render_image(device_config.get_resolution(), "dashboard.html", "dashboard.css", template_params)


        return image



