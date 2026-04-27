from ai_tools import check_conflict, semantic_rag_filter, add_event_tool
from dateutil import parser as date_parser

def test_conflict_evaluator():
    print("--- Testing Conflict Evaluator ---")
    existing_events = [
        {"start": "2026-04-25T10:00:00Z", "end": "2026-04-25T11:00:00Z"}
    ]
    
    # 1. Exact overlap (Should conflict)
    s1 = date_parser.parse("2026-04-25T10:00:00Z")
    e1 = date_parser.parse("2026-04-25T11:00:00Z")
    print(f"Exact overlap: {check_conflict(s1, e1, existing_events)} (Expected: True)")
    
    # 2. Partial overlap (Should conflict)
    s2 = date_parser.parse("2026-04-25T10:30:00Z")
    e2 = date_parser.parse("2026-04-25T11:30:00Z")
    print(f"Partial overlap: {check_conflict(s2, e2, existing_events)} (Expected: True)")
    
    # 3. No overlap, completely after (Should not conflict)
    s3 = date_parser.parse("2026-04-25T11:00:00Z")
    e3 = date_parser.parse("2026-04-25T12:00:00Z")
    print(f"No overlap (After): {check_conflict(s3, e3, existing_events)} (Expected: False)")

    # 4. No overlap, completely before (Should not conflict)
    s4 = date_parser.parse("2026-04-25T08:00:00Z")
    e4 = date_parser.parse("2026-04-25T09:00:00Z")
    print(f"No overlap (Before): {check_conflict(s4, e4, existing_events)} (Expected: False)")

def test_rag_filter():
    print("\n--- Testing RAG Semantic Filter ---")
    all_events = [
        {"title": "Math 101 Test", "start": "2026-04-25T10:00:00Z", "end": "2026-04-25T11:00:00Z"},
        {"title": "Lunch", "start": "2026-04-25T12:00:00Z", "end": "2026-04-25T13:00:00Z"},
        {"title": "Physics Quiz", "start": "2026-04-26T09:00:00Z", "end": "2026-04-26T10:00:00Z"},
    ]
    
    prompt = "I need to study for my test and quiz."
    filtered_context = semantic_rag_filter(prompt, all_events)
    
    print(f"Prompt: '{prompt}'")
    print("Target Events (Should be Math Test and Physics Quiz):")
    for t in filtered_context['target_events']:
        print(f" - {t['title']}")
        
    print("Busy Map (Should be Lunch):")
    for b in filtered_context['busy_times']:
        print(f" - {b}")

if __name__ == "__main__":
    test_conflict_evaluator()
    test_rag_filter()
