import uuid
from icalendar import Calendar, Event
from datetime import datetime
from dateutil import parser as date_parser

class CalendarManager:
    @staticmethod
    def parse_ics(file_content: bytes) -> list:
        """
        Parses an ICS file content (bytes) into a JSON-like list of event dictionaries.
        """
        cal = Calendar.from_ical(file_content)
        events = []
        for component in cal.walk():
            if component.name == "VEVENT":
                # Extract basic properties
                summary = str(component.get('summary', 'Untitled Event'))
                description = str(component.get('description', ''))
                
                # Extract times and convert to ISO format strings for JSON compatibility
                dtstart = component.get('dtstart')
                dtend = component.get('dtend')
                
                start_iso = dtstart.dt.isoformat() if dtstart else None
                end_iso = dtend.dt.isoformat() if dtend else None
                
                # Get or generate a unique ID
                uid = str(component.get('uid', uuid.uuid4()))
                
                events.append({
                    "id": uid,
                    "title": summary,
                    "description": description,
                    "start": start_iso,
                    "end": end_iso
                })
        return events

    @staticmethod
    def export_ics(json_events: list) -> bytes:
        """
        Converts a list of JSON-like event dictionaries back into an ICS file (bytes).
        """
        cal = Calendar()
        cal.add('prodid', '-//StudyPal AI Calendar//EN')
        cal.add('version', '2.0')

        for ev in json_events:
            event = Event()
            event.add('summary', ev.get('title', 'Untitled Event'))
            event.add('description', ev.get('description', ''))
            
            # Parse ISO strings back to datetime objects
            if ev.get('start'):
                start_dt = date_parser.parse(ev['start'])
                event.add('dtstart', start_dt)
            if ev.get('end'):
                end_dt = date_parser.parse(ev['end'])
                event.add('dtend', end_dt)
                
            event.add('dtstamp', datetime.now())
            event.add('uid', ev.get('id', str(uuid.uuid4())))
            
            cal.add_component(event)
            
        return cal.to_ical()
