import sys
import os

# Add the parent directory to sys.path so we can import pawpal_system
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pawpal_system import Pet, Task

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

