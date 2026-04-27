import streamlit as st
from streamlit_calendar import calendar
from calendar_system import CalendarManager
from dateutil import parser

@st.dialog("Event Details")
def show_event_details(event):
    desc = event.get("extendedProps", {}).get("description", "")
    
    with st.form(key=f"edit_form_{event.get('id', 'unknown')}"):
        new_title = st.text_input("Title", value=event.get('title', ''))
        
        try:
            start_time = parser.parse(event.get("start")).strftime("%B %d, %Y at %I:%M %p")
            st.write(f"**Start:** {start_time}")
        except Exception:
            st.write(f"**Start:** {event.get('start', 'N/A')}")
            
        try:
            if event.get("end"):
                end_time = parser.parse(event.get("end")).strftime("%B %d, %Y at %I:%M %p")
                st.write(f"**End:** {end_time}")
        except Exception:
            if event.get('end'):
                st.write(f"**End:** {event.get('end')}")
                
        new_desc = st.text_area("Description", value=desc)
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("Save Changes")
        with col2:
            delete = st.form_submit_button("Delete Event", type="primary")
            
        if submit:
            for i, ev in enumerate(st.session_state.calendar_events):
                if ev["id"] == event["id"]:
                    st.session_state.calendar_events[i]["title"] = new_title
                    st.session_state.calendar_events[i]["description"] = new_desc
                    break
            st.rerun()
            
        if delete:
            st.session_state.calendar_events = [ev for ev in st.session_state.calendar_events if ev["id"] != event["id"]]
            st.rerun()

@st.dialog("Add New Event")
def show_add_event_dialog(start_str, end_str):
    with st.form(key="add_event_form"):
        title = st.text_input("Event Title")
        
        try:
            start_time = parser.parse(start_str).strftime("%B %d, %Y at %I:%M %p")
            st.write(f"**Start:** {start_time}")
        except Exception:
            st.write(f"**Start:** {start_str}")
            
        try:
            if end_str:
                end_time = parser.parse(end_str).strftime("%B %d, %Y at %I:%M %p")
                st.write(f"**End:** {end_time}")
        except Exception:
            if end_str:
                st.write(f"**End:** {end_str}")
                
        description = st.text_area("Description")
        
        submit = st.form_submit_button("Create Event")
        
        if submit:
            import uuid
            new_event = {
                "id": str(uuid.uuid4()),
                "title": title if title else "Untitled Event",
                "start": start_str,
                "end": end_str,
                "description": description
            }
            st.session_state.calendar_events.append(new_event)
            st.rerun()

st.set_page_config(page_title="AgendaBot", page_icon="📅", layout="wide")

st.title("📅 AgendaBot AI Planner")
st.markdown("Your smart calendar assistant for organizing study sessions!")
st.divider()

if "calendar_events" not in st.session_state:
    st.session_state.calendar_events = []

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR: Utilities & API Key ---
with st.sidebar:
    st.header("⚙️ Settings & Utilities")
    
    st.subheader("Import Calendar")
    
    # 1. File Uploader
    uploaded_file = st.file_uploader("Upload .ics file", type=["ics"])
    if uploaded_file is not None:
        if st.button("Import from File"):
            file_bytes = uploaded_file.read()
            parsed_events = CalendarManager.parse_ics(file_bytes)
            st.session_state.calendar_events = parsed_events
            st.success(f"Imported {len(parsed_events)} events!")
            st.rerun()

    # 2. URL Importer
    ics_url = st.text_input("Or paste an .ics URL (e.g. Canvas)")
    if ics_url:
        if st.button("Import from URL"):
            import urllib.request
            try:
                req = urllib.request.Request(
                    ics_url, headers={"User-Agent": "Mozilla/5.0"}
                )
                with urllib.request.urlopen(req) as response:
                    file_bytes = response.read()
                parsed_events = CalendarManager.parse_ics(file_bytes)
                st.session_state.calendar_events = parsed_events
                st.success(f"Imported {len(parsed_events)} events from URL!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to load URL: {e}")

    st.divider()

    if st.session_state.calendar_events:
        st.subheader("Export Calendar")
        exported_bytes = CalendarManager.export_ics(st.session_state.calendar_events)
        st.download_button(
            label="Download .ics",
            data=exported_bytes,
            file_name="AgendaBot_schedule.ics",
            mime="text/calendar",
        )

    st.divider()
    
    provider = st.selectbox(
        "🧠 Choose your AI Brain:",
        ["Google Gemini (gemini-2.5-flash)", "OpenAI (gpt-4o-mini)", "Groq (llama3-70b-8192)"],
        index=0
    )
    
    if "Gemini" in provider:
        key_label = "Input your Gemini API Key:"
        help_text = "Get your free key from Google AI Studio."
    elif "OpenAI" in provider:
        key_label = "Input your OpenAI API Key:"
        help_text = "Get your key from platform.openai.com."
    else:
        key_label = "Input your Groq API Key:"
        help_text = "Get your free key from console.groq.com."

    api_key = st.text_input(
        key_label,
        type="password",
        help=help_text,
    )
    st.caption(
        "🔒 *Privacy Note: Your API key is 100% safe. It is never saved, logged, or sent anywhere other than directly to the API. It disappears the moment you close this tab.*"
    )
    
    

# --- MAIN LAYOUT: Split into Calendar (Left) and Chat (Right) ---
col_cal, col_chat = st.columns([3, 1])

with col_cal:
    st.subheader("Your Schedule")
    if st.session_state.calendar_events:
        calendar_options = {
            "headerToolbar": {
                "left": "today prev,next",
                "center": "title",
                "right": "dayGridMonth,timeGridWeek,listWeek",
            },
            "initialView": "timeGridWeek",
            "slotMinTime": "06:00:00",
            "slotMaxTime": "24:00:00",
            "height": 700,
            "nowIndicator": True,
            "navLinks": True,
            "weekNumbers": True,
            "editable": True,
            "selectable": True,
            "selectMirror": True,
        }

        custom_css = """
            .fc-event {
                cursor: pointer;
                border-radius: 4px;
                box-shadow: 0 1px 2px rgba(0,0,0,0.1);
                transition: transform 0.1s ease;
            }
            .fc-event:hover {
                transform: scale(1.02);
            }
            .fc-event-title {
                font-weight: 600;
                padding: 2px 4px;
            }
            .fc-event-time {
                padding: 0 4px;
            }
        """

        calendar_output = calendar(
            events=st.session_state.calendar_events,
            options=calendar_options,
            custom_css=custom_css,
        )

        if calendar_output:
            if calendar_output.get("callback") == "eventClick":
                current_click_str = str(calendar_output.get("eventClick", {}))
                if st.session_state.get("last_handled_click") != current_click_str:
                    st.session_state["last_handled_click"] = current_click_str
                    event = calendar_output["eventClick"]["event"]
                    show_event_details(event)
                    
            elif calendar_output.get("callback") == "select":
                current_select_str = str(calendar_output.get("select", {}))
                if st.session_state.get("last_handled_select") != current_select_str:
                    st.session_state["last_handled_select"] = current_select_str
                    select_data = calendar_output["select"]
                    show_add_event_dialog(select_data["start"], select_data["end"])
                    
            elif calendar_output.get("callback") == "eventChange":
                current_change_str = str(calendar_output.get("eventChange", {}))
                if st.session_state.get("last_handled_change") != current_change_str:
                    st.session_state["last_handled_change"] = current_change_str
                    changed_event = calendar_output["eventChange"]["event"]
                    for i, ev in enumerate(st.session_state.calendar_events):
                        if ev["id"] == changed_event["id"]:
                            st.session_state.calendar_events[i]["start"] = changed_event["start"]
                            if changed_event.get("end"):
                                st.session_state.calendar_events[i]["end"] = changed_event["end"]
                            break
                    st.rerun()
    else:
        st.info("Upload an `.ics` file or URL in the sidebar to see your schedule!")


with col_chat:
    st.subheader("🤖 Chat with AgendaBot")
    
    # We use a container for chat messages so it scrolls independently
    chat_container = st.container(height=625)
    
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
    if prompt := st.chat_input("Ask AgendaBot to plan your week..."):
        if not api_key:
            st.error("Please provide my brain link (API Key) in the sidebar first!")
        else:
            # 1. Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)

                # 2. Call AI Agent
                with st.chat_message("assistant"):
                    with st.spinner("AgendaBot is thinking..."):
                        from ai_agent import get_ai_response
                        
                        provider_model = "gemini/gemini-2.5-flash"
                        if "OpenAI" in provider:
                            provider_model = "gpt-4o-mini"
                        elif "Groq" in provider:
                            provider_model = "groq/llama3-70b-8192"

                        # Track events length to see if AI added anything
                        initial_events_count = len(st.session_state.calendar_events)

                        # Fetch response (this will auto-execute the scheduling tool if needed)
                        response_text = get_ai_response(
                            provider_model, prompt, api_key, st.session_state.calendar_events
                        )

                        st.markdown(response_text)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": response_text}
                        )

                        # If the AI scheduled an event, refresh the page to update the visual calendar
                        if len(st.session_state.calendar_events) > initial_events_count:
                            st.rerun()
