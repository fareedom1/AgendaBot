import streamlit as st
from pawpal_system import Pet, Task, Schedule, Owner
from datetime import date

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# Initialize Session State
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")
    default_pet = Pet(name="Mochi", species="cat", breed="Unknown", age=2, weight=10.0)
    st.session_state.owner.add_pet(default_pet)

if "pending_tasks" not in st.session_state:
    st.session_state.pending_tasks = []

if "last_schedule" not in st.session_state:
    st.session_state.last_schedule = None

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Your Configuration")
current_owner = st.session_state.owner
current_pet = current_owner.pets[0]

owner_name = st.text_input("Owner name", value=current_owner.name)
if owner_name != current_owner.name:
    current_owner.name = owner_name

pet_name = st.text_input("Pet name", value=current_pet.name)
species_options = ["dog", "cat", "other"]
try:
    default_index = species_options.index(current_pet.species.lower())
except ValueError:
    default_index = 2
species = st.selectbox("Species", species_options, index=default_index)

if pet_name != current_pet.name or species != current_pet.species:
    current_pet.update_info(name=pet_name, species=species.lower())

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    new_task = Task(
        pet=current_pet, 
        name=task_title, 
        description="Added from UI", 
        duration_minutes=int(duration), 
        priority=priority.capitalize()
    )
    st.session_state.pending_tasks.append(new_task)

if st.session_state.pending_tasks:
    st.write("Current Pending Tasks:")
    task_data = [{"Task": t.name, "Pet": t.pet.name, "Duration (min)": t.duration_minutes, "Priority": t.priority} for t in st.session_state.pending_tasks]
    st.table(task_data)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Generate Daily Schedule")
st.caption("Uses the Greedy Priority Algorithm to fit tasks perfectly into your schedule.")

available_minutes = st.slider("Available Free Time (Minutes)", min_value=10, max_value=300, value=60, step=10)

if st.button("⚙️ Generate Schedule"):
    if not st.session_state.pending_tasks:
        st.error("Please add some tasks first!")
    else:
        # 1. Instantiate the Schedule
        schedule = Schedule(available_minutes=available_minutes, schedule_date=date.today())
        
        # 2. Add all pending tasks
        for task in st.session_state.pending_tasks:
            schedule.add_task(task)
            
        # 3. Fire the Engine
        schedule.generate_daily_schedule()
        
        # 4. Save to Vault
        st.session_state.last_schedule = schedule

# Render the Output if it exists
if st.session_state.last_schedule:
    saved = st.session_state.last_schedule
    st.success(f"Schedule automatically generated for {saved.schedule_date}!")
    
    st.write("### ✅ Accepted Tasks")
    if saved.final_schedule:
        accepted_data = [{"Task": t.name, "Duration": f"{t.duration_minutes}m", "Priority": t.priority} for t in saved.final_schedule]
        st.table(accepted_data)
    else:
        st.warning("No tasks fit into the schedule!")
        
    with st.expander("🔍 Show Scheduler Reasoning Log"):
        for task in saved.pending_tasks:
            reason = saved.get_reasoning(task)
            if "Included" in reason:
                st.write(f"🟢 **{task.name}**: {reason}")
            else:
                st.write(f"🔴 **{task.name}**: {reason}")
