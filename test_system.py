import os
import json
import logging
from calendar_system import CalendarManager
from ai_tools import check_conflict, semantic_rag_filter

# Set up simple logging for the test output
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def fetch_canvas_events():
    import urllib.request
    url = "https://canvas.fau.edu/feeds/calendars/user_HdTa4a9eA35sLBeTgEjGvBfX8VmK0xqNIhBdo0SA.ics"
    logging.info("Fetching real Canvas ICS data...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req) as response:
            file_bytes = response.read()
            events = CalendarManager.parse_ics(file_bytes)
            logging.info(f"Successfully parsed {len(events)} events from Canvas.")
            return events
    except Exception as e:
        logging.error(f"Failed to fetch Canvas feed: {e}")
        return []

def run_tier1_zero_cost_tests(events):
    print("\n" + "="*40)
    print("--- TIER 1: ZERO-COST LOCAL TESTS ---")
    print("="*40)
    
    # Test RAG
    print("\n[Testing Semantic RAG Filter]")
    prompt = "I need to study for any quizzes or assignments coming up."
    context = semantic_rag_filter(prompt, events)
    print(f"Target Events Found: {len(context['target_events'])}")
    print(f"Busy Time Blocks Generated: {len(context['busy_times'])}")
    if len(context['target_events']) > 0:
        print(f"Sample Target: {context['target_events'][0]['title']}")
    
    # Test Conflict Evaluator
    print("\n[Testing Conflict Guardrail]")
    from dateutil import parser as date_parser
    if events:
        # Pick the first event and try to overlap with it
        first_event = events[0]
        s = date_parser.parse(first_event['start'])
        e = date_parser.parse(first_event['end'])
        
        # Exact overlap
        has_conflict = check_conflict(s, e, events)
        print(f"Testing exact overlap with '{first_event['title']}':")
        print(f"Conflict Detected? -> {'✅ YES (Expected)' if has_conflict else '❌ NO (Failed)'}")

def run_tier3_targeted_api_tests(events):
    print("\n" + "="*40)
    print("--- TIER 3: TARGETED BATCH API TEST ---")
    print("="*40)
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("⚠️ GEMINI_API_KEY environment variable not set.")
        print("Skipping API tests to save credits. Run `export GEMINI_API_KEY='your_key'` to enable.")
        return

    from ai_agent import get_gemini_response
    
    # We will test ONE highly complex prompt to get the most out of our API call
    test_prompt = "Find my first assignment in my schedule and schedule a 1-hour study session exactly during it to test if your conflict guardrail blocks you, then schedule it 2 hours before the assignment instead."
    
    print(f"Running targeted API test with prompt:\n\"{test_prompt}\"")
    print("Sending to Gemini... (This will consume a small amount of credits)")
    
    # Make a copy of events so we don't pollute the original list
    test_events_state = list(events)
    initial_count = len(test_events_state)
    
    response = get_gemini_response(test_prompt, api_key, test_events_state)
    
    print("\n[Agent Final Response]")
    print(response)
    
    print(f"\n[Calendar State Evaluation]")
    added_events = len(test_events_state) - initial_count
    print(f"Events added by agent: {added_events}")
    
    if added_events > 0:
        print("New Scheduled Events:")
        for ev in test_events_state[initial_count:]:
            print(f" - {ev['title']} ({ev['start']} to {ev['end']})")


if __name__ == "__main__":
    canvas_events = fetch_canvas_events()
    if canvas_events:
        run_tier1_zero_cost_tests(canvas_events)
        run_tier3_targeted_api_tests(canvas_events)
