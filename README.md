# AgendaBot: AI-Assisted Calendar Planning App 📅

https://agendabot.streamlit.app

## Original Project Context (Modules 1-3)
My original project was **PawPal+**, a smart interactive Streamlit dashboard designed to help busy pet owners organize and track daily care routines. It featured a multi-pet management system and used a greedy task allocation algorithm to mathematically pack high-priority pet chores into a user's free time constraints. 

## What It Does and Why It Matters
**AgendaBot** is an evolution of that concept into an Agentic AI system. Instead of manually mapping chores, AgendaBot allows students to import their actual Canvas `.ics` calendar schedules and chat with an AI Agent. The AI analyzes their free time, filters their upcoming assignments/tests using an intelligent Semantic RAG (Retrieval-Augmented Generation) system, and autonomously schedules study sessions directly onto their interactive calendar. This matters because it relieves the cognitive load of planning and prevents students from accidentally double-booking themselves during critical study periods.

---

## Architecture Overview
The system is built on a **ReAct (Reason + Act)** Agentic Loop using Streamlit and LiteLLM.

![Data Flow](/assets/dataflow.png)

1. **Dynamic Semantic RAG Retriever**: When you ask the AI to plan a study session, the retriever parses your `.ics` JSON calendar. It extracts relevant academic events (e.g., "tests") AND dynamically matches any custom personal events (like a "date" or "gym") if you explicitly mention them in your chat. Everything else is compressed into a lightweight local time "Busy Time Map" to save tokens and ensure privacy.
2. **The Agent Loop**: Using `litellm`, the agent is forced to output a `<plan>` block explaining its reasoning.
3. **Guardrails & Execution**: The agent calls the `schedule_study_session` tool. This tool routes through our `check_conflict` Python Evaluator. If the AI attempts to schedule a session over an existing class, the Python backend throws an error, forcing the AI into a `<reflection>` block where it apologizes and tries a different time block.
4. **Human Verification**: The AI visually updates the Streamlit calendar grid, allowing the human user to click, edit, or delete the scheduled events before clicking "Export" to download the final `.ics`.

---

## Demo Walkthrough
*Please watch the video below for a full end-to-end demonstration of the application, including the AI analyzing inputs, reacting to conflicts, and successfully scheduling events on the visual calendar.*

![GIF Showcase](/assets/showcase.gif)

---

## Setup Instructions

The project is deployed via Streamlit and you can access it via the following link: 
https://agendabot.streamlit.app

To run this project reproducibly on any local machine:

1. **Clone the repository and enter the directory**:
   ```bash
   git clone <your-repo-link>
   cd applied-ai-system-project
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```

3. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Streamlit Dashboard**:
   ```bash
   streamlit run app.py
   ```

5. **Interact**: Upload an `.ics` file or provide a Canvas calendar URL. Select your AI provider (Gemini, OpenAI, or Groq) in the UI, input your free API key, and begin chatting!

---

## Sample Interactions

**Input 1:** *"I have a math test on Friday. Schedule a 2-hour study session for me on Thursday afternoon."*
**AI Output:** 
> `<plan>` The user has a math test on Friday. I need to schedule a 2-hour session on Thursday. I will check the Busy Times Map for Thursday. I see they have class until 3 PM. I will schedule the session from 4:00 PM to 6:00 PM. `</plan>` 
> *Calls Tool: schedule_study_session(title="Math Study", start="...", end="...")*
> "I have successfully scheduled a 2-hour Math Study session for you on Thursday from 4:00 PM to 6:00 PM. Good luck on your test! [Confidence Score: 0.95]"

**Input 2:** *"Schedule a 1-hour session right in the middle of my Wednesday physics lecture."*
**AI Output:**
> `<plan>` Attempting to schedule at 1:00 PM on Wednesday. `</plan>`
> *Calls Tool... Tool Returns FAILED: Time conflict detected!*
> `<reflection>` The tool rejected my request because it overlaps with the existing "Physics Lecture" event. I need to find a free slot. I see 3:00 PM is open. `</reflection>`
> *Calls Tool (Retry at 3:00 PM)... SUCCESS*
> "I tried to schedule it during your lecture, but my system prevented the double-booking! Instead, I've scheduled your study session right after class from 3:00 PM to 4:00 PM. [Confidence Score: 0.88]"

---

## Design Decisions
- **Why LiteLLM & Multi-Provider Support?** Agentic AI loops consume API rate limits very quickly (Google's free tier has a strict 15 Requests Per Minute limit). A single chat message can silently generate 5+ background requests as the AI "thinks" and "reflects", easily triggering 503 errors. I implemented `litellm` so users can bypass these strict limits by hot-swapping to **Groq**, which provides an enormous free tier (30+ RPM) and lightning-fast responses for seamless Agentic loops.
- **Why RAG Filtering?** Passing an entire semester's `.ics` calendar to the LLM would consume massive amounts of tokens and cause hallucinations. The trade-off was writing complex Python logic (`semantic_rag_filter`) to compress unrelated events into simple string maps (e.g., "Busy 10am-12pm"). To ensure users can still schedule around personal tasks, the filter was upgraded to be **dynamic**—if a user types "schedule before my date", the Python logic dynamically unhides the "date" event from the busy map and feeds it to the AI.
- **Why Python Guardrails?** AI is inherently unpredictable. Instead of trusting the AI to understand time overlaps, I built a deterministic Python function (`check_conflict`) that acts as a hard wall. This guarantees reliability.

---

## Testing Summary
We implemented a targeted API script (`test_system.py`) to simulate a full multi-turn Agent loop (conflict -> reflection -> retry) in a single, credit-efficient execution, alongside rigorous interactive testing in the Streamlit UI.
- **What Worked**: The Python `check_conflict` guardrail worked flawlessly, correctly identifying overlaps without wasting LLM tokens. The `<reflection>` hook also consistently forced the AI to seamlessly correct its own scheduling mistakes when a conflict was detected.
- **What Didn't**: 
  - **Temporal Amnesia & Timezones**: Initially, the AI scheduled events at random dates or offset times because it didn't know the current date and struggled with UTC 'Z' strings. I fixed this by automatically injecting the system's live date into the prompt and building a `_to_local_naive` Python helper.
  - **Rate Limits**: During interactive testing, the agentic loop frequently triggered 503 Quota errors because a single prompt generates multiple rapid API calls. This forced me to implement the `litellm` multi-provider architecture.
- **What I Learned**: The AI is completely blind to personal events by default! To save massive amounts of tokens and prevent hallucinations, the RAG filter compresses non-academic events into blank "Busy Times". I learned I had to build a dynamic keyword matcher so the AI only "sees" the full context of personal events (like a "date") if the user explicitly mentions them in the chat.

---

## Reflection and Ethics

**Limitations and Biases**
The system assumes standard 9-to-5 working/waking hours unless specified. It may have a bias against non-traditional schedules (e.g., night shift workers) if the LLM's training data assumes people want to study during the day. The semantic filter also relies on English keywords ("test", "exam"), meaning it might fail to filter correctly for calendars written in other languages.

**Misuse Prevention**
An AI scheduling tool could be misused to flood a user's calendar with spam events or overwrite critical deadlines. To prevent this, our `add_event_tool` only *appends* new events with a specific `#28a745` color tag; it is mathematically incapable of deleting or modifying the user's original imported `.ics` events. The user must manually click "Export" to save the changes, acting as a human-in-the-loop safeguard.

**Surprises During Testing**
I was surprised by how effectively the AI utilized the `<reflection>` block. When the hardcoded Python guardrail rejected a double-booking, the AI didn't just crash; it smoothly read the error message, apologized in its internal monologue, and successfully found a new open slot on its second try.

**AI Collaboration**
Working with Antigravity (the AI assistant) was incredibly productive for scaffolding the Streamlit UI and setting up the complex `icalendar` parsing logic. **Helpful Suggestion**: The AI correctly suggested using `st.session_state` to hold the calendar objects, which prevented the UI from wiping the AI's newly scheduled events every time the user typed a new chat message. **Flawed Suggestion**: Initially, the AI suggested sending the entire JSON calendar directly to the LLM. This is flawed because it could quickly exceed token limits and confuse the AI; I had to override this by requesting the Semantic RAG Filter to compress the data.
