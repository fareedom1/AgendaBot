import streamlit as st
from pawpal_system import Pet, Task, Schedule, Owner
from datetime import date

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

# Initialize Session State
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")
    default_pet = Pet(name="Mochi", species="Cat", breed="Unknown", age=2, weight=10.0)
    st.session_state.owner.add_pet(default_pet)

if "pending_tasks" not in st.session_state:
    st.session_state.pending_tasks = []

if "completed_tasks" not in st.session_state:
    st.session_state.completed_tasks = []

if "last_schedule" not in st.session_state:
    st.session_state.last_schedule = None

st.title("🐾 PawPal+ Dashboard")
st.markdown("Your smart assistant for prioritizing and organizing your daily pet core routines!")
st.divider()

# --- 1. CONFIGURATION: PETS ---
current_owner = st.session_state.owner

col_name, _ = st.columns([1, 3])
with col_name:
    owner_name = st.text_input("Owner Name", value=current_owner.name)
    if owner_name != current_owner.name:
        current_owner.name = owner_name

st.subheader("Your Pets")
if current_owner.pets:
    pet_data = [{"Name": p.name, "Species": p.species.capitalize(), "Breed": p.breed, "Age": p.age, "Weight (lbs)": p.weight} for p in current_owner.pets]
    st.dataframe(pet_data, use_container_width=True)

with st.expander("➕ Add a New Pet"):
    with st.form("add_pet_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            new_pet_name = st.text_input("Pet Name")
        with c2:
            new_pet_species = st.selectbox("Species", ["Dog", "Cat", "Bird", "Other"])
        with c3:
            new_pet_breed = st.text_input("Breed (Optional)", value="Unknown")
            
        c4, c5, _ = st.columns(3)
        with c4:
            new_pet_age = st.number_input("Age (Years)", min_value=0, value=1)
        with c5:
            new_pet_weight = st.number_input("Weight (lbs)", min_value=0.0, value=10.0, step=1.0)
            
        if st.form_submit_button("Save Pet"):
            if new_pet_name:
                p = Pet(name=new_pet_name, species=new_pet_species, breed=new_pet_breed, age=new_pet_age, weight=new_pet_weight)
                current_owner.add_pet(p)
                st.success(f"{new_pet_name} added successfully!")
                st.rerun()

st.divider()

# --- 2. ADDING TASKS ---
st.subheader("Add Care Task")

with st.form("add_task_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", placeholder="Morning walk")
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col2:
        priority = st.selectbox("Priority", ["High", "Medium", "Low"], index=1)
        # Time input
        task_time_obj = st.time_input("Scheduled Time", value=None)
    with col3:
        frequency = st.selectbox("Frequency Tracking", ["Once", "Daily", "Weekly"], index=0)
        # Pet Selector dynamically populated!
        pet_names = [p.name for p in current_owner.pets]
        selected_pet_name = st.selectbox("Assign to Pet", pet_names) if pet_names else None

    if st.form_submit_button("➕ Add Task"):
        if not selected_pet_name:
            st.error("You must add a pet first!")
        elif not task_title:
            st.error("Task title cannot be empty.")
        elif not task_time_obj:
            st.error("Please assign a scheduled time.")
        else:
            time_str = task_time_obj.strftime("%H:%M")
            target_pet = next((p for p in current_owner.pets if p.name == selected_pet_name), None)
            
            new_task = Task(
                pet=target_pet, 
                name=task_title, 
                description="Added from UI", 
                duration_minutes=int(duration), 
                priority=priority,
                time=time_str,
                frequency=frequency
            )
            st.session_state.pending_tasks.append(new_task)
            st.success("Task added to queue!")
            st.rerun()

# Display Pending Tasks
if st.session_state.pending_tasks:
    st.write("##### Current Pending Tasks")
    # Interactive physical rows so we can trigger mark_completed() logically!
    for i, t in enumerate(st.session_state.pending_tasks):
        c1, c2, c3, c4 = st.columns([1, 4, 3, 2])
        with c1:
            if st.button("✅ Done", key=f"complete_btn_{i}_{t.name}"):
                # 1. Pop the designated chore out of the pending list
                completed_chore = st.session_state.pending_tasks.pop(i)
                # 2. Mathematically mark it completed and check for recurrence
                next_task = completed_chore.mark_completed()
                # 3. Route to the history log
                st.session_state.completed_tasks.append(completed_chore)
                # 4. If recurrent, push new clone back into pending queue
                if next_task:
                    st.session_state.pending_tasks.append(next_task)
                    st.toast(f"Recurring clone spawned for {next_task.due_date}!", icon="🔁")
                    
                st.rerun()
                
        with c2:
            st.write(f"**{t.name}**")
            st.caption(f"Priority: {t.priority}")
        with c3:
            st.write(f"🐾 {t.pet.name}")
            st.caption(f"{t.duration_minutes}m • [{t.frequency}]")
        with c4:
            st.write(f"🕒 {t.time}")
            st.caption(f"{t.due_date}")
else:
    st.info("No tasks in the queue.")

if st.session_state.completed_tasks:
    with st.expander("📚 View Completed Tasks History"):
        for t in reversed(st.session_state.completed_tasks):
            st.write(f"- ✅ **{t.name}** for {t.pet.name} (Scheduled: {t.due_date})")

st.divider()

# --- 3. SCHEDULE GENERATION ---
st.subheader("⚙️ Generate Daily Schedule")
st.write("The greedy-algorithm mathematically organizes tasks chronologically, fitting as many high-priority items into your free time as possible.")

available_minutes = st.slider("Total Free Time to Allocate (Minutes)", min_value=10, max_value=300, value=120, step=10)

# Check for conflicts instantly BEFORE generation using our detection pass!
if st.session_state.pending_tasks:
    # We instantiate a temporary Schedule purely to access its static-like logic
    temp_schedule = Schedule(available_minutes, date.today())
    conflicts = temp_schedule.detect_conflicts(st.session_state.pending_tasks)
    if conflicts:
        for c in conflicts:
            st.warning(f"⚠️ {c}")

if st.button("🚀 Generate Optimized Schedule", type="primary"):
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

# Render the Output beautifully if it exists
if st.session_state.last_schedule:
    saved = st.session_state.last_schedule
    st.success(f"Algorithm successfully mapped a daily plan for {saved.schedule_date}!")
    
    st.write("### ✅ Accepted Tasks (Chronological)")
    if saved.final_schedule:
        # Sort chronologically right before rendering using our algorithmic feature!!
        chronological_tasks = saved.sort_by_time(saved.final_schedule)
        
        accepted_data = [{"Time": t.time, "Task": t.name, "Pet": t.pet.name, "Duration": f"{t.duration_minutes}m", "Priority": t.priority} for t in chronological_tasks]
        st.dataframe(accepted_data, use_container_width=True)
    else:
        st.error("No tasks fit into the schedule!")
        
    with st.expander("🔍 Show Scheduler Reasoning Log"):
        for task in saved.pending_tasks:
            reason = saved.get_reasoning(task)
            if "Included" in reason:
                st.write(f"🟢 **{task.name}**: {reason}")
            else:
                st.write(f"🔴 **{task.name}**: {reason}")
