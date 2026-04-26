from google import genai
from google.genai import types
from ai_tools import semantic_rag_filter, add_event_tool
import logging

def get_gemini_response(user_prompt: str, api_key: str, events_state: list) -> str:
    """
    Connects to Gemini API, provides context via Semantic RAG, 
    and handles automatic tool calling for scheduling events.
    """
    # 1. RAG Filtering
    context = semantic_rag_filter(user_prompt, events_state)
    
    # Format the context for the system prompt
    context_str = f"Target Events Found:\n{context['target_events']}\n\nBusy Times Map:\n{context['busy_times']}"
    
    # 2. Define the Tool (with closure to access events_state)
    def schedule_study_session(title: str, start_iso: str, end_iso: str, description: str) -> str:
        """
        Schedules a new study session or task on the calendar. ONLY call this if you are confident the time slot is free according to the Busy Times Map.
        
        Args:
            title: The name of the study session (e.g., 'Math Study').
            start_iso: Start time in ISO 8601 format (e.g., '2026-04-25T10:00:00Z').
            end_iso: End time in ISO 8601 format (e.g., '2026-04-25T11:00:00Z').
            description: Details about what to study.
        """
        try:
            # We call our guarded tool
            add_event_tool(title, start_iso, end_iso, description, events_state)
            return f"SUCCESS: Scheduled '{title}' from {start_iso} to {end_iso}."
        except ValueError as e:
            return f"FAILED to schedule due to error: {str(e)}. Please choose a different time."

    # 3. Setup Gemini Client
    client = genai.Client(api_key=api_key)
    
    system_instruction = f"""
    You are 'StudyPal', an AI Calendar Assistant. 
    Your job is to help the user plan their schedule. 
    You have access to their calendar context below.
    
    CONTEXT:
    {context_str}
    
    RULES:
    1. If the user asks to schedule something, use the `schedule_study_session` tool.
    2. Check the "Busy Times Map" to ensure you DO NOT double-book the user.
    3. If the tool returns a FAILED message (conflict), apologize and suggest a different time based on their free time.
    4. At the end of every response, you MUST output a Confidence Score between 0.0 and 1.0, formatted exactly like this: [Confidence Score: 0.95]
    """
    
    try:
        logging.info("Sending request to Gemini...")
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_prompt,
            config=types.GenerateContentConfig(
                tools=[schedule_study_session],
                system_instruction=system_instruction,
                temperature=0.2
            )
        )
        return response.text
    except Exception as e:
        logging.error(f"Gemini API Error: {e}")
        return f"Error connecting to Gemini API: {e}"
