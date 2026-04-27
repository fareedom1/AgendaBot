import logging
import json
from datetime import datetime
from litellm import completion
from ai_tools import semantic_rag_filter, add_event_tool

def get_ai_response(provider_model: str, user_prompt: str, api_key: str, events_state: list) -> str:
    """
    Connects to AI API via LiteLLM, implements the Core Agent Loop:
    Plan -> Execute (Reason, Act, Observe, Reflect) -> Evaluate.
    """
    # 1. RAG Filtering
    context = semantic_rag_filter(user_prompt, events_state)
    context_str = f"Target Events Found:\n{context['target_events']}\n\nBusy Times Map:\n{context['busy_times']}"
    
    # 2. Define the Tool wrapper
    def schedule_study_session(title: str, start_iso: str, end_iso: str, description: str) -> str:
        try:
            add_event_tool(title, start_iso, end_iso, description, events_state)
            return f"SUCCESS: Scheduled '{title}' from {start_iso} to {end_iso}."
        except ValueError as e:
            return f"FAILED to schedule due to error: {str(e)}"

    # 3. Define the standard OpenAI Tool schema
    tools = [
        {
            "type": "function",
            "function": {
                "name": "schedule_study_session",
                "description": "Schedules a new study session or task on the calendar. ONLY call this if confident the time slot is free according to the Busy Times Map.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "The name of the study session (e.g., 'Math Study')."},
                        "start_iso": {"type": "string", "description": "Start time in local naive ISO 8601 format WITHOUT timezones or 'Z' (e.g., '2026-04-25T10:00:00')."},
                        "end_iso": {"type": "string", "description": "End time in local naive ISO 8601 format WITHOUT timezones or 'Z' (e.g., '2026-04-25T11:00:00')."},
                        "description": {"type": "string", "description": "Details about what to study."}
                    },
                    "required": ["title", "start_iso", "end_iso", "description"]
                }
            }
        }
    ]

    current_time_str = datetime.now().strftime("%A, %B %d, %Y - %I:%M %p")
    
    system_instruction = f"""
    You are 'AgendaBot', an AI Calendar Assistant. 
    Your job is to help the user plan their schedule. 
    
    CURRENT SYSTEM TIME: 
    {current_time_str}
    (Use this to understand relative terms like "today", "tomorrow", or "next week").
    
    CONTEXT:
    {context_str}
    
    RULES & AGENT LOOP:
    1. PLANNING: If the user asks to schedule something, you MUST first output a <plan>...</plan> block breaking down the task.
    2. EXECUTION: Use the `schedule_study_session` tool to execute your plan. Check the "Busy Times Map" to avoid double-booking.
    3. TIMEZONES & HOURS: You MUST schedule events using LOCAL NAIVE TIME (do not append 'Z' or timezone offsets). Assume the user prefers study sessions during reasonable waking hours (e.g., 9:00 AM to 8:00 PM) unless specified otherwise.
    4. REFLECTION: If the tool returns a FAILED message, you MUST output a <reflection>...</reflection> block analyzing why it failed and proposing a new time, and then try the tool again with the new time.
    5. EVALUATION: Once all tasks are complete, verify the final calendar state matches the goal.
    6. At the end of your final response to the user, you MUST output a Confidence Score between 0.0 and 1.0, formatted exactly like this: [Confidence Score: X.XX]
    """
    
    planning_prompt = f"{user_prompt}\n\nPlease output a detailed <plan> block before taking any scheduling actions."
    
    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": planning_prompt}
    ]
    
    max_turns = 5
    final_response_text = ""
    
    for turn in range(max_turns):
        logging.info(f"Agent turn {turn + 1}")
        try:
            response = completion(
                model=provider_model,
                api_key=api_key,
                messages=messages,
                tools=tools,
                temperature=0.2,
                tool_choice="auto"
            )
        except Exception as e:
            logging.error(f"LLM API Error: {e}")
            error_str = str(e).lower()
            if "503" in error_str or "high demand" in error_str:
                return "🧠 **Brain freeze!** My brain is currently experiencing high traffic. Take a quick break and try asking me again in a few minutes, or switch to a different provider!"
            elif "429" in error_str or "quota" in error_str:
                return "🧠 **Brain exhausted!** We've hit our API quota limit for now. Please switch to a different provider or try again later!"
            elif "api_key" in error_str or "400" in error_str or "401" in error_str or "unauthorized" in error_str or "invalid" in error_str:
                return "🧠 **Brain disconnected!** It seems the brain link (API Key) you provided is invalid. Please double-check it in the sidebar!"
            else:
                return f"🧠 **Ouch, brain cramp!** Something went wrong while connecting to my brain: {str(e)}"

        message = response.choices[0].message
        
        # Append the model's response to history
        messages.append(message.model_dump(exclude_unset=True))
        
        # Check if the model decided to call a function
        if message.tool_calls:
            for tool_call in message.tool_calls:
                if tool_call.function.name == "schedule_study_session":
                    # Parse arguments safely
                    try:
                        args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        args = {}
                        
                    result = schedule_study_session(
                        title=args.get("title", ""),
                        start_iso=args.get("start_iso", ""),
                        end_iso=args.get("end_iso", ""),
                        description=args.get("description", "")
                    )
                    logging.info(f"Tool executed: {tool_call.function.name}. Result: {result}")
                    
                    if "FAILED" in result:
                        feedback = f"Result: {result}\nINSTRUCTION: Please enter a <reflection> block to analyze the failure, then call the tool again with a different time."
                    else:
                        feedback = f"Result: {result}"
                        
                    # Add tool response back to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": feedback
                    })
        else:
            # Phase 3: Evaluation & Final Response
            final_response_text = message.content or ""
            break
            
    if not final_response_text:
        final_response_text = "Agent reached maximum execution turns without finishing."
        
    return final_response_text
