import logging
import uuid
from datetime import datetime
from dateutil import parser as date_parser

# 1. Setup Logging for the AI Tools (Rubric Requirement)
logging.basicConfig(
    filename='ai_agent.log', 
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def check_conflict(start_dt: datetime, end_dt: datetime, existing_events: list) -> bool:
    """
    Conflict Evaluator: Checks if a given time slot overlaps with any existing events.
    Returns True if conflict exists, False otherwise.
    """
    for ev in existing_events:
        ev_start = ev.get('start')
        ev_end = ev.get('end')
        if not ev_start or not ev_end:
            continue
            
        existing_start = date_parser.parse(ev_start)
        existing_end = date_parser.parse(ev_end)
        
        # Overlap condition: (StartA < EndB) and (EndA > StartB)
        if start_dt < existing_end and end_dt > existing_start:
            return True
            
    return False

def add_event_tool(title: str, start_iso: str, end_iso: str, description: str, events_state: list) -> dict:
    """
    Agentic Tool: Attempts to schedule a new event.
    Raises ValueError if there is a time conflict (Guardrail).
    """
    logging.info(f"AI attempting to schedule: '{title}' from {start_iso} to {end_iso}")
    
    start_dt = date_parser.parse(start_iso)
    end_dt = date_parser.parse(end_iso)
    
    if start_dt >= end_dt:
        error_msg = "End time must be after start time."
        logging.error(error_msg)
        raise ValueError(error_msg)
        
    if check_conflict(start_dt, end_dt, events_state):
        error_msg = f"Time conflict detected for '{title}' between {start_iso} and {end_iso}. Please try another time."
        logging.warning(error_msg)
        raise ValueError(error_msg)
        
    # No conflict, safe to add!
    new_event = {
        "id": f"ai-planned-{uuid.uuid4()}",
        "title": f"📚 {title}",
        "description": description,
        "start": start_iso,
        "end": end_iso,
        "color": "#28a745" # Give AI events a green color
    }
    
    events_state.append(new_event)
    logging.info(f"Successfully scheduled: '{title}'")
    return new_event

def semantic_rag_filter(prompt: str, all_events: list) -> dict:
    """
    Advanced RAG Filter: Analyzes the prompt to extract target events 
    and compresses all other events into a simple busy-time map.
    """
    prompt_lower = prompt.lower()
    
    # Simple keyword extraction (can be expanded)
    keywords = ["test", "quiz", "exam", "assignment", "homework", "project", "presentation"]
    active_keywords = [kw for kw in keywords if kw in prompt_lower]
    
    target_events = []
    busy_map = []
    
    for ev in all_events:
        title = ev.get('title', '').lower()
        is_target = any(kw in title for kw in active_keywords)
        
        if is_target:
            target_events.append(ev)
        else:
            # Compress into a busy map string
            if ev.get('start') and ev.get('end'):
                s = date_parser.parse(ev['start']).strftime("%a %b %d %I:%M%p")
                e = date_parser.parse(ev['end']).strftime("%I:%M%p")
                busy_map.append(f"Busy: {s} to {e}")
                
    return {
        "target_events": target_events,
        "busy_times": busy_map
    }
