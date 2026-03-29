from pawpal_system import Owner, Pet, Task, Schedule
from datetime import date

def main():
    print("Initializing PawPal+ testing data...")
    
    # 1. Create Owner and Pets
    owner = Owner("Fareed")
    fido = Pet(name="Fido", species="Dog", breed="Golden Retriever", age=3, weight=30.0)
    luna = Pet(name="Luna", species="Cat", breed="Siamese", age=2, weight=10.0)
    
    owner.add_pet(fido)
    owner.add_pet(luna)
    
    # 2. Add Tasks
    walk_task = Task(pet=fido, name="Morning Walk", description="Walk around the block", duration_minutes=45, priority="High")
    feed_cat_task = Task(pet=luna, name="Feed Breakfast", description="Give wet food", duration_minutes=15, priority="High")
    play_task = Task(pet=luna, name="Laser Pointer Time", description="Play with laser pointer", duration_minutes=30, priority="Low")
    groom_task = Task(pet=fido, name="Brush Fur", description="Brush out shedding fur", duration_minutes=20, priority="Medium")
    
    # 3. Create Schedule with limited time (e.g., 60 minutes) to test constraints
    print("Testing constraints: We have 4 tasks total (110 minutes total), but only 60 minutes of free time available.\n")
    schedule = Schedule(available_minutes=60, schedule_date=date.today())
    owner.schedules.append(schedule)
    
    schedule.add_task(walk_task)
    schedule.add_task(feed_cat_task)
    schedule.add_task(play_task)
    schedule.add_task(groom_task)
    
    # Generate schedule
    schedule.generate_daily_schedule()
    
    # 4. Print "Today's Schedule" to the terminal
    schedule.display_plan()
    
    # Highlight the reasoning
    print("--- Scheduler Reasoning Log ---")
    for task in [walk_task, feed_cat_task, play_task, groom_task]:
        print(f"Task '{task.name}': {schedule.get_reasoning(task)}")

if __name__ == "__main__":
    main()
