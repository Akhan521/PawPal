from __future__ import annotations
from dataclasses import dataclass, field
from enum import IntEnum


class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: Priority
    pet_name: str = ""
    completed: bool = False

    def mark_completed(self) -> None:
        """Mark this task as completed."""
        self.completed = True


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task and stamp it with this pet's name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet's task list."""
        self.tasks.remove(task)


@dataclass
class Owner:
    name: str
    available_minutes: int
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's pet list."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner's pet list."""
        self.pets.remove(pet)


class Scheduler:
    def generate_schedule(self, owner: Owner) -> list[Task]:
        """Build a priority-sorted daily schedule within the owner's time budget."""
        all_tasks = []
        for pet in owner.pets:
            for task in pet.tasks:
                if not task.completed:
                    all_tasks.append(task)

        all_tasks.sort(key=lambda t: t.priority, reverse=True)

        scheduled = []
        remaining_minutes = owner.available_minutes
        for task in all_tasks:
            if task.duration_minutes <= remaining_minutes:
                scheduled.append(task)
                remaining_minutes -= task.duration_minutes

        return scheduled

    def explain_schedule(self, schedule: list[Task]) -> str:
        """Return a human-readable summary of the scheduled tasks."""
        if not schedule:
            return "No tasks scheduled for today."

        lines = []
        total_minutes = 0
        for i, task in enumerate(schedule, start=1):
            lines.append(
                f"{i}. {task.title} ({task.pet_name}) - "
                f"{task.duration_minutes} min [{task.priority.name}]"
            )
            total_minutes += task.duration_minutes

        lines.append(f"\nTotal: {total_minutes} minutes")
        return "\n".join(lines)
