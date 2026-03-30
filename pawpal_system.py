from __future__ import annotations
from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from enum import IntEnum

INTERVAL_DAYS = {
    "daily": 1,
    "weekly": 7,
    "biweekly": 14,
    "monthly": 30,
}


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
    time: str = ""              # Scheduled time in HH:MM format
    recurring: bool = False
    recurrence_interval: str = ""  # e.g. "daily", "weekly"
    scheduled_date: date | None = None

    def mark_completed(self) -> Task | None:
        """Mark this task as completed.

        If the task is recurring, returns a new Task instance scheduled
        for the next occurrence (current date + interval via timedelta).
        Returns None for non-recurring tasks.
        """
        self.completed = True

        if not self.recurring or self.recurrence_interval not in INTERVAL_DAYS:
            return None

        days = INTERVAL_DAYS[self.recurrence_interval]
        next_date = (self.scheduled_date or date.today()) + timedelta(days=days)

        return replace(self, completed=False, scheduled_date=next_date)


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

    def complete_task(self, task: Task) -> Task | None:
        """Mark a task completed and auto-schedule the next occurrence if recurring.

        Returns the newly created next-occurrence Task, or None.
        """
        next_task = task.mark_completed()
        if next_task is not None:
            self.tasks.append(next_task)
        return next_task


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
        """Build a priority-sorted daily schedule within the owner's time budget.

        Uses a greedy algorithm: collects all incomplete tasks across the
        owner's pets, sorts them by priority (HIGH first), and packs tasks
        into the available minutes until the budget is exhausted.
        """
        all_tasks = [t for p in owner.pets for t in p.tasks if not t.completed]
        all_tasks.sort(key=lambda t: t.priority, reverse=True)

        scheduled = []
        remaining_minutes = owner.available_minutes
        for task in all_tasks:
            if task.duration_minutes <= remaining_minutes:
                scheduled.append(task)
                remaining_minutes -= task.duration_minutes

        return scheduled

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks chronologically by their scheduled time in HH:MM format.

        Uses a lambda key that produces a (bool, str) tuple: the boolean
        pushes tasks with no time to the end, while the HH:MM string
        provides natural lexicographic ordering for timed tasks.
        """
        return sorted(
            tasks,
            key=lambda t: (t.time == "", t.time)
        )

    def filter_by_pet(self, tasks: list[Task], pet_name: str) -> list[Task]:
        """Filter a task list to only those assigned to the given pet name.

        Uses a list comprehension to match on the task's pet_name field.
        """
        return [t for t in tasks if t.pet_name == pet_name]

    def filter_by_status(self, tasks: list[Task], completed: bool) -> list[Task]:
        """Filter a task list by completion status.

        Pass completed=True to get finished tasks, or completed=False
        to get tasks still pending.
        """
        return [t for t in tasks if t.completed == completed]

    def _time_to_minutes(self, time_str: str) -> int | None:
        """Convert HH:MM string to total minutes. Returns None on bad input."""
        try:
            h, m = map(int, time_str.split(":"))
            return h * 60 + m
        except (ValueError, AttributeError):
            return None

    def _tasks_overlap(self, a: Task, b: Task) -> bool:
        """Check whether two timed tasks have overlapping time windows."""
        start_a = self._time_to_minutes(a.time)
        start_b = self._time_to_minutes(b.time)
        if start_a is None or start_b is None:
            return False
        end_a = start_a + a.duration_minutes
        end_b = start_b + b.duration_minutes
        return start_a < end_b and start_b < end_a

    def detect_conflicts(self, tasks: list[Task]) -> list[str]:
        """Detect all scheduling conflicts and return human-readable messages.

        Checks every pair of timed tasks — same-pet and cross-pet — and
        labels each conflict accordingly. Never raises; malformed times
        are silently skipped. Uses precomputed start/end minutes and an
        early break on the sorted list to skip unnecessary comparisons.
        """
        # Precompute minutes once per task, skip unparseable times
        timed = []
        for t in self.sort_by_time([t for t in tasks if t.time]):
            start = self._time_to_minutes(t.time)
            if start is not None:
                timed.append((t, start, start + t.duration_minutes))

        messages = []
        for i, (task_a, start_a, end_a) in enumerate(timed):
            for task_b, start_b, end_b in timed[i + 1:]:
                if start_b >= end_a:
                    break  # sorted — no later task can overlap task_a
                same_pet = task_a.pet_name == task_b.pet_name
                label = "Same-pet conflict" if same_pet else "Owner conflict"
                messages.append(
                    f"  {label}: '{task_a.title}' ({task_a.pet_name} @ {task_a.time}) "
                    f"overlaps with '{task_b.title}' ({task_b.pet_name} @ {task_b.time})"
                )
        return messages

    def get_recurring_tasks(self, tasks: list[Task]) -> list[Task]:
        """Filter a task list to only recurring tasks.

        Recurring tasks have recurring=True and a recurrence_interval
        (e.g. "daily", "weekly") used by mark_completed to auto-schedule
        the next occurrence via timedelta.
        """
        return [t for t in tasks if t.recurring]

    def explain_schedule(self, schedule: list[Task]) -> str:
        """Return a human-readable summary of the scheduled tasks."""
        if not schedule:
            return "No tasks scheduled for today."

        lines = []
        total_minutes = 0
        for i, task in enumerate(schedule, start=1):
            date_str = f" on {task.scheduled_date}" if task.scheduled_date else ""
            time_str = f" @ {task.time}" if task.time else ""
            recur_str = f" [repeats {task.recurrence_interval}]" if task.recurring else ""
            lines.append(
                f"{i}. {task.title} ({task.pet_name}){date_str}{time_str} - "
                f"{task.duration_minutes} min [{task.priority.name}]{recur_str}"
            )
            total_minutes += task.duration_minutes

        lines.append(f"\nTotal: {total_minutes} minutes")
        return "\n".join(lines)
