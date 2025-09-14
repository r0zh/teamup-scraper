import requests
from icalendar import Calendar, Event
from datetime import datetime
import pytz

# Constants
TEAMUP_API_URL = "https://teamup.com/ksfogsn8nf72mjdfcv/events"
SUBCALENDAR_ID = 13671838 # id of 2ºCIA subcalendar 
START_DATE = "2025-02-13"
END_DATE = "2025-06-07"
TIMEZONE = "Europe/Madrid"

# Fetch events from Teamup API
def fetch_teamup_events():
    params = {
        "startDate": START_DATE,
        "endDate": END_DATE,
        "tz": TIMEZONE
    }
    response = requests.get(TEAMUP_API_URL, params=params)
    
    if response.status_code == 200:
        return response.json().get("events", [])
    else:
        print(f"Failed to fetch events: {response.status_code}")
        return []

# Filter events by subcalendar_id
def filter_events_by_subcalendar(events, subcalendar_id):
    return [event for event in events if subcalendar_id in event.get("subcalendar_ids", [])]

# Convert Teamup event to iCalendar event
def create_ical_event(event):
    ical_event = Event()
    
    # Set summary (title)
    ical_event.add('summary', event.get("title", "No Title"))
    
    # Set start and end times
    start_dt = datetime.fromisoformat(event["start_dt"].replace("Z", "+00:00"))
    end_dt = datetime.fromisoformat(event["end_dt"].replace("Z", "+00:00"))
    
    # Add timezone information if datetime is naive
    timezone = pytz.timezone(TIMEZONE)
    if start_dt.tzinfo is None:
        start_dt = timezone.localize(start_dt)
    if end_dt.tzinfo is None:
        end_dt = timezone.localize(end_dt)
    
    ical_event.add('dtstart', start_dt)
    ical_event.add('dtend', end_dt)
    
    # Add location
    location = event.get("location")
    if location:
        ical_event.add('location', location)
    
    # Add description (notes)
    notes = event.get("notes", "")
    if notes:
        ical_event.add('description', notes)
    
    return ical_event

# Generate the .ics file
def generate_ics_file(events, output_file="calendar.ics"):
    cal = Calendar()
    cal.add('prodid', '-//2ºCIA//Teamup Calendar//')
    cal.add('version', '2.0')

    for event in events:
        ical_event = create_ical_event(event)
        cal.add_component(ical_event)
    
    with open(output_file, 'wb') as f:
        f.write(cal.to_ical())

    print(f"ICS file generated: {output_file}")

if __name__ == "__main__":
    # Fetch events from Teamup API
    events = fetch_teamup_events()
    
    # Filter events by subcalendar_id
    filtered_events = filter_events_by_subcalendar(events, SUBCALENDAR_ID)
    
    # Generate ICS file
    generate_ics_file(filtered_events)