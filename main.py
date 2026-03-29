from pawpal_system import Owner, Pet, Task, Schedule
from datetime import date

def main():
    print("Initializing PawPal+ testing data...")
    
    owner = Owner("Fareed")
    fido = Pet(name="Fido", species="Dog", breed="Golden", age=3, weight=30.0)
    luna = Pet(name="Luna", species="Cat", breed="Siamese", age=2, weight=10.0)
    owner.add_pet(fido)
    owner.add_pet(luna)
    
    # 1. OUT OF ORDER tasks with frequency and time
    walk_task = Task(pet=fido, name="Afternoon Walk", description="Walk", duration_minutes=45, priority="High", time="14:00", frequency="daily")
    feed_cat_task = Task(pet=luna, name="Feed Breakfast", description="Wet food", duration_minutes=15, priority="High", time="08:00", frequency="daily")
    meds_task = Task(pet=fido, name="Give Medication", description="Pill", duration_minutes=5, priority="High", time="08:00", frequency="once")
    play_task = Task(pet=luna, name="Laser Pointer Time", description="Play", duration_minutes=30, priority="Low", time="18:30", frequency="weekly")
    
    tasks = [walk_task, feed_cat_task, meds_task, play_task]
    schedule = Schedule(available_minutes=120, schedule_date=date.today())
    
    print("\n--- Testing sort_by_time() ---")
    sorted_tasks = schedule.sort_by_time(tasks)
    for t in sorted_tasks:
        print(f"[{t.time}] {t.name}")
        
    # 2. Testing Conflicts
    schedule.detect_conflicts(tasks)

    # 3. Testing Filtering
    print("\n--- Testing filter_tasks() (Pet=Luna) ---")
    luna_tasks = schedule.filter_tasks(tasks, pet_name="Luna")
    for t in luna_tasks:
        print(f"Found: {t.name}")

    # 4. Testing Recurrence / Mark Completed
    print("\n--- Testing Recurring Automation (mark_completed) ---")
    print(f"Original Task: {feed_cat_task.name} ({feed_cat_task.frequency}) due on {feed_cat_task.due_date} (Status: {feed_cat_task.status})")
    next_task = feed_cat_task.mark_completed()
    print(f"Original Task status changed to: {feed_cat_task.status}")
    if next_task:
        print(f"Generated NEW Recurring Instance: '{next_task.name}' due on {next_task.due_date}!")

if __name__ == "__main__":
    main()
