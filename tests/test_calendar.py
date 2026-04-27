import urllib.request
from calendar_system import CalendarManager

def test_real_calendar():
    url = "https://canvas.fau.edu/feeds/calendars/user_HdTa4a9eA35sLBeTgEjGvBfX8VmK0xqNIhBdo0SA.ics"
    print(f"Fetching calendar from {url}...")
    
    # 1. Fetch the real ICS file
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        ics_data = response.read()
        
    print(f"Downloaded {len(ics_data)} bytes of data.")
    
    # 2. Parse it
    json_events = CalendarManager.parse_ics(ics_data)
    print(f"\nSuccessfully parsed {len(json_events)} events!")
    
    print("\nFirst 3 parsed JSON events:")
    for ev in json_events[:3]:
        print(ev,"\n")

    # 3. Export it back
    exported_ics = CalendarManager.export_ics(json_events)
    print("\nFirst 20 lines of exported ICS:")
    lines = exported_ics.decode('utf-8').splitlines()
    for line in lines[:20]:
        print(line)

if __name__ == "__main__":
    test_real_calendar()
