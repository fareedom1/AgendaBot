import logging
import uuid
from datetime import datetime
from dateutil import parser as date_parser

# 1. Setup Logging for the AI Tools
logging.basicConfig(
    filename='ai_agent.log', 
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def _to_local_naive(dt_str: str) -> datetime:
    """Helper to parse a datetime string and convert it to a local, naive datetime."""
    dt = date_parser.parse(dt_str)
    if dt.tzinfo is not None:
        # Convert to system local time
        dt = dt.astimezone()
        # Make it naive
        dt = dt.replace(tzinfo=None)
    return dt

def check_conflict(start_dt: datetime, end_dt: datetime, existing_events: list) -> bool:
    """
    Conflict Evaluator: Checks if a given time slot overlaps with any existing events.
    Handles timezone-aware vs timezone-naive comparisons by forcing local naive time.
    """
    # Ensure inputs are local naive
    if start_dt.tzinfo is not None:
        start_dt = start_dt.astimezone().replace(tzinfo=None)
    if end_dt.tzinfo is not None:
        end_dt = end_dt.astimezone().replace(tzinfo=None)
        
    for ev in existing_events:
        ev_start = ev.get('start')
        ev_end = ev.get('end')
        if not ev_start or not ev_end:
            continue
            
        existing_start = _to_local_naive(ev_start)
        existing_end = _to_local_naive(ev_end)
        
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
    
    # We don't convert start_iso and end_iso because the calendar needs the exact string the LLM gave us
    # Assuming LLM outputs naive local ISO strings like '2026-04-29T09:00:00'
    
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
    and compresses all other events into a simple busy-time map in LOCAL time.
    """
    prompt_lower = prompt.lower()
    
    # Simple keyword extraction (can be expanded)
    keywords = ["test", "quiz", "exam", "assignment", "homework", "project", "presentation", "discussion"]
    active_keywords = [kw for kw in keywords if kw in prompt_lower]
    
    # If the user says "all my assignments", let's force the keywords to trigger if they match any event.
    if "all" in prompt_lower and ("assignment" in prompt_lower or "due" in prompt_lower):
        active_keywords = keywords
        
    target_events = []
    busy_map = []
    
    for ev in all_events:
        title = ev.get('title', '').lower()
        is_target = any(kw in title for kw in active_keywords)
        
        if is_target:
            target_events.append(ev)
        else:
            # Compress into a busy map string using Local Naive Time!
            if ev.get('start') and ev.get('end'):
                s_dt = _to_local_naive(ev['start'])
                e_dt = _to_local_naive(ev['end'])
                s = s_dt.strftime("%a %b %d %I:%M%p")
                e = e_dt.strftime("%I:%M%p")
                busy_map.append(f"Busy: {s} to {e}")
                
    return {
        "target_events": target_events,
        "busy_times": busy_map
    }
