from dataclasses import dataclass, field
from typing import List, Optional
from datetime import date

@dataclass
class Pet:
    """Represents a pet."""
    name: str
    species: str
    breed: str
    age: int
    weight: float
    tasks: List['Task'] = field(default_factory=list, repr=False)

    def update_info(self, **kwargs) -> None:
        """Update pet information."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def add_task(self, task: 'Task') -> None:
        """Assign a task directly to the pet."""
        if task not in self.tasks:
            self.tasks.append(task)


@dataclass
class Task:
    """Represents a care task for a specific pet."""
    pet: Pet
    name: str
    description: str
    duration_minutes: int
    priority: str
    status: str = "pending"

    @property
    def priority_weight(self) -> int:
        """Returns an integer weight for sorting priorities."""
        weights = {"high": 3, "medium": 2, "low": 1}
        return weights.get(self.priority.lower(), 0)

    def update_task(self, **kwargs) -> None:
        """Update task information."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def mark_completed(self) -> None:
        """Mark the task as completed."""
        self.status = "completed"


class Owner:
    """Represents the owner who manages pets."""
    def __init__(self, name: str):
        """Initialize the Owner with a specific name and empty lists."""
        self.name: str = name
        self.pets: List[Pet] = []
        self.schedules: List['Schedule'] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's list."""
        if pet not in self.pets:
            self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from the owner's list."""
        if pet in self.pets:
            self.pets.remove(pet)


class Schedule:
    """Handles logic for generating a daily task plan."""
    def __init__(self, available_minutes: int, schedule_date: Optional[date] = None):
        """Initialize the Schedule with available daily minutes and an optional date."""
        self.schedule_date: Optional[date] = schedule_date
        self.pending_tasks: List[Task] = []
        self.available_minutes: int = available_minutes
        self.final_schedule: List[Task] = []
        self.reasoning_log: dict[int, str] = {}

    def add_task(self, task: Task) -> None:
        """Add a task to the pending tasks list."""
        self.pending_tasks.append(task)

    def generate_daily_schedule(self) -> None:
        """Generate a schedule based on available time and priorities using a Greedy Algorithm."""
        self.final_schedule = []
        self.reasoning_log.clear()

        # Sort tasks: highest priority first, then shortest duration
        sorted_tasks = sorted(
            self.pending_tasks, 
            key=lambda t: (t.priority_weight, -t.duration_minutes), 
            reverse=True
        )

        time_remaining = self.available_minutes

        for task in sorted_tasks:
            if task.duration_minutes <= time_remaining:
                self.final_schedule.append(task)
                time_remaining -= task.duration_minutes
                self.reasoning_log[id(task)] = f"Included: Fit into remaining time ({task.priority} priority, needs {task.duration_minutes}m)."
            else:
                self.reasoning_log[id(task)] = f"Skipped: Not enough time (needs {task.duration_minutes}m, only {time_remaining}m left)."

    def get_reasoning(self, task: Task) -> str:
        """Explain the reasoning for scheduling or skipping a task."""
        return self.reasoning_log.get(id(task), "No reasoning available. Schedule was not generated with this task.")

    def display_plan(self) -> None:
        """Format and print the final schedule."""
        print("\n=== Daily Schedule ===")
        if self.schedule_date:
            print(f"Date: {self.schedule_date}")
        print(f"Total Available Time: {self.available_minutes} minutes")
        print("Scheduled Tasks:")
        total_time_used = 0
        if not self.final_schedule:
            print("  (No tasks scheduled)")
        for t in self.final_schedule:
            print(f"  - [{t.priority.upper()}] {t.name} for {t.pet.name} ({t.duration_minutes}m)")
            total_time_used += t.duration_minutes
        print(f"Time Remaining: {self.available_minutes - total_time_used} minutes")
        print("======================\n")
