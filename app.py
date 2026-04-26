import streamlit as st
from streamlit_calendar import calendar
from calendar_system import CalendarManager

st.set_page_config(page_title="StudyPal", page_icon="📅", layout="wide")

st.title("📅 StudyPal AI Planner")
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
            file_name="studypal_schedule.ics",
            mime="text/calendar",
        )

    st.divider()
    # API Key Input moved to sidebar
    api_key = st.text_input(
        "🧠 Hey! I need the link to my brain please input your Gemini API Key:",
        type="password",
        help="Get your free key from Google AI Studio.",
    )
    st.caption(
        "🔒 *Privacy Note: Your API key is 100% safe. It is never saved, logged, or sent anywhere other than directly to Google's API. It disappears the moment you close this tab.*"
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
        }

        custom_css = """
            .fc-event-title {
                font-weight: bold;
            }
        """

        calendar_output = calendar(
            events=st.session_state.calendar_events,
            options=calendar_options,
            custom_css=custom_css,
        )
    else:
        st.info("Upload an `.ics` file or URL in the sidebar to see your schedule!")


with col_chat:
    st.subheader("🤖 Chat with StudyPal")
    
    # We use a container for chat messages so it scrolls independently
    chat_container = st.container(height=625)
    
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
    if prompt := st.chat_input("Ask StudyPal to plan your week..."):
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
                    with st.spinner("StudyPal is thinking..."):
                        from ai_agent import get_gemini_response

                        # Track events length to see if AI added anything
                        initial_events_count = len(st.session_state.calendar_events)

                        # Fetch response (this will auto-execute the scheduling tool if needed)
                        response_text = get_gemini_response(
                            prompt, api_key, st.session_state.calendar_events
                        )

                        st.markdown(response_text)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": response_text}
                        )

                        # If the AI scheduled an event, refresh the page to update the visual calendar
                        if len(st.session_state.calendar_events) > initial_events_count:
                            st.rerun()
