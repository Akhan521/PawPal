from datetime import date
from pawpal_system import Owner, Pet, Task, Priority, Scheduler


# --- Create owner ---
owner = Owner(name="Jordan", available_minutes=120)

# --- Create pets ---
mochi = Pet(name="Mochi", species="dog", age=3)
whiskers = Pet(name="Whiskers", species="cat", age=5)

owner.add_pet(mochi)
owner.add_pet(whiskers)

today = date.today()

# --- Add tasks OUT OF ORDER to test sorting ---
mochi.add_task(Task(title="Brush coat", duration_minutes=15, priority=Priority.LOW,
                     time="09:00", scheduled_date=today))
mochi.add_task(Task(title="Evening walk", duration_minutes=25, priority=Priority.HIGH,
                     time="18:00", recurring=True, recurrence_interval="daily",
                     scheduled_date=today))
mochi.add_task(Task(title="Morning walk", duration_minutes=30, priority=Priority.HIGH,
                     time="07:00", recurring=True, recurrence_interval="daily",
                     scheduled_date=today))
mochi.add_task(Task(title="Flea medication", duration_minutes=10, priority=Priority.HIGH,
                     time="08:00", scheduled_date=today))

whiskers.add_task(Task(title="Play with feather toy", duration_minutes=20,
                        priority=Priority.MEDIUM, time="08:05", scheduled_date=today))
whiskers.add_task(Task(title="Feed breakfast", duration_minutes=10, priority=Priority.HIGH,
                        time="07:00", recurring=True, recurrence_interval="daily",
                        scheduled_date=today))
whiskers.add_task(Task(title="Clean litter box", duration_minutes=10, priority=Priority.MEDIUM,
                        time="08:00", recurring=True, recurrence_interval="weekly",
                        scheduled_date=today))

# --- Generate and display today's schedule ---
scheduler = Scheduler()
schedule = scheduler.generate_schedule(owner)
schedule = scheduler.sort_by_time(schedule)

print("=" * 58)
print(f"  PawPal+ Daily Schedule for {owner.name}")
print(f"  Time budget: {owner.available_minutes} minutes")
print("=" * 58)

print(f"\n--- Today's Schedule ({today}) ---")
print(scheduler.explain_schedule(schedule))

# --- Complete recurring tasks and watch next occurrences appear ---
print("\n--- Completing Recurring Tasks ---")
for pet in owner.pets:
    for task in list(pet.tasks):  # iterate a copy since list may grow
        if task.recurring and not task.completed:
            next_task = pet.complete_task(task)
            if next_task:
                print(f"  Done: '{task.title}' ({pet.name}) on {task.scheduled_date}")
                print(f"    -> Next occurrence auto-scheduled for {next_task.scheduled_date}")

# --- Show all tasks after completing today's recurring ones ---
all_tasks = [t for pet in owner.pets for t in pet.tasks]

print(f"\n--- Completed Tasks ---")
completed = scheduler.filter_by_status(all_tasks, completed=True)
print(scheduler.explain_schedule(completed))

print(f"\n--- Upcoming Incomplete Tasks ---")
incomplete = scheduler.filter_by_status(all_tasks, completed=False)
incomplete = scheduler.sort_by_time(incomplete)
print(scheduler.explain_schedule(incomplete))

# --- Filter by pet ---
print("\n--- Mochi's Full Task List ---")
mochi_all = scheduler.filter_by_pet(all_tasks, "Mochi")
print(scheduler.explain_schedule(mochi_all))

print("\n--- Whiskers' Full Task List ---")
whiskers_all = scheduler.filter_by_pet(all_tasks, "Whiskers")
print(scheduler.explain_schedule(whiskers_all))

# --- Conflict detection ---
print("\n--- Conflict Detection ---")
conflicts = scheduler.detect_conflicts(incomplete)
if conflicts:
    for msg in conflicts:
        print(msg)
else:
    print("  No scheduling conflicts detected.")

print("\n" + "=" * 58)
