from pawpal_system import Owner, Pet, Task, Priority, Scheduler


# --- Create owner ---
owner = Owner(name="Jordan", available_minutes=90)

# --- Create pets ---
mochi = Pet(name="Mochi", species="dog", age=3)
whiskers = Pet(name="Whiskers", species="cat", age=5)

owner.add_pet(mochi)
owner.add_pet(whiskers)

# --- Add tasks to Mochi ---
mochi.add_task(Task(title="Morning walk", duration_minutes=30, priority=Priority.HIGH))
mochi.add_task(Task(title="Brush coat", duration_minutes=15, priority=Priority.LOW))

# --- Add tasks to Whiskers ---
whiskers.add_task(Task(title="Feed breakfast", duration_minutes=10, priority=Priority.HIGH))
whiskers.add_task(Task(title="Clean litter box", duration_minutes=10, priority=Priority.MEDIUM))
whiskers.add_task(Task(title="Play with feather toy", duration_minutes=20, priority=Priority.MEDIUM))

# --- Generate and display schedule ---
scheduler = Scheduler()
schedule = scheduler.generate_schedule(owner)

print("=" * 44)
print(f"  PawPal+ Daily Schedule for {owner.name}")
print(f"  Time budget: {owner.available_minutes} minutes")
print("=" * 44)
print()
print(scheduler.explain_schedule(schedule))
print()
print("=" * 44)
