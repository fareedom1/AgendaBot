import sys
import os

# Add the parent directory to sys.path so we can import pawpal_system
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import date, timedelta
from pawpal_system import Pet, Task, Schedule

def test_task_completion():
    # 1. Arrange: Create a Pet and a Task
    fido = Pet(name="Fido", species="Dog", breed="Mutt", age=3, weight=30.0)
    walk_task = Task(pet=fido, name="Walk", description="Morning walk", duration_minutes=30, priority="High")
    
    # Verify initial state is "pending"
    assert walk_task.status == "pending", "Task should initialize with 'pending' status."
    
    # 2. Act: Complete the task
    walk_task.mark_completed()
    
    # 3. Assert: Verify status changed to "completed"
    assert walk_task.status == "completed", "mark_completed() should change status to 'completed'."


def test_pet_task_addition():
    # 1. Arrange: Create a Pet and a Task
    luna = Pet(name="Luna", species="Cat", breed="Siamese", age=2, weight=10.0)
    feed_task = Task(pet=luna, name="Feed", description="Wet food", duration_minutes=10, priority="High")
    
    # Verify initial task count is 0
    assert len(luna.tasks) == 0, "A new Pet should start with 0 tasks."
    
    # 2. Act: Add the task to the pet
    luna.add_task(feed_task)
    
    # 3. Assert: Verify the count increased to 1
    assert len(luna.tasks) == 1, "Adding a task should increase the pet's task count to 1."
    assert luna.tasks[0] == feed_task, "The task in the list should be the one we just added."

def test_sorting_correctness():
    # Arrange
    schedule = Schedule(available_minutes=60, schedule_date=date.today())
    puppy = Pet(name="Doggo", species="Dog", breed="Pug", age=1, weight=10.0)
    task1 = Task(pet=puppy, name="Late Task", description="", duration_minutes=10, priority="low", time="18:00")
    task2 = Task(pet=puppy, name="Early Task", description="", duration_minutes=10, priority="low", time="08:00")
    
    # Act
    sorted_tasks = schedule.sort_by_time([task1, task2])
    
    # Assert
    assert sorted_tasks[0].name == "Early Task", "Top sorted task should be chronologically earliest (08:00)"
    assert sorted_tasks[1].name == "Late Task", "Bottom sorted task should be chronologically latest (18:00)"

def test_recurrence_logic():
    # Arrange
    puppy = Pet(name="Doggo", species="Dog", breed="Pug", age=1, weight=10.0)
    daily_task = Task(pet=puppy, name="Feed", description="", duration_minutes=10, priority="high", frequency="daily")
    old_date = daily_task.due_date
    
    # Act
    new_task = daily_task.mark_completed()
    
    # Assert
    assert new_task is not None, "mark_completed on a recurring task must return a new cloned task"
    assert new_task.due_date == old_date + timedelta(days=1), "The new task should be scheduled for exactly 1 day later."
    assert daily_task.status == "completed", "Original task must be marked completed."

def test_conflict_detection():
    # Arrange
    schedule = Schedule(available_minutes=60, schedule_date=date.today())
    puppy = Pet(name="Doggo", species="Dog", breed="Pug", age=1, weight=10.0)
    task1 = Task(pet=puppy, name="Morning Walk", description="", duration_minutes=10, priority="low", time="09:00")
    task2 = Task(pet=puppy, name="Breakfast", description="", duration_minutes=10, priority="low", time="09:00")
    task3 = Task(pet=puppy, name="Lunch", description="", duration_minutes=10, priority="low", time="12:00")
    
    # Act & Assert
    assert schedule.detect_conflicts([task1, task2]) is True, "Two tasks at 09:00 should successfully flag a collision."
    assert schedule.detect_conflicts([task1, task3]) is False, "Tasks at 09:00 and 12:00 should NOT flag a collision."

