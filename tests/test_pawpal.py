from datetime import date, timedelta

from pawpal_system import Task, Pet, Owner, Priority, Scheduler


# ── Sorting ──────────────────────────────────────────────────────

def test_sort_by_time_chronological_order():
    """Tasks added out of order are returned sorted by HH:MM."""
    scheduler = Scheduler()
    tasks = [
        Task(title="Evening walk", duration_minutes=25, priority=Priority.HIGH, time="18:00"),
        Task(title="Morning walk", duration_minutes=30, priority=Priority.HIGH, time="07:00"),
        Task(title="Lunch feed", duration_minutes=10, priority=Priority.MEDIUM, time="12:00"),
    ]
    result = scheduler.sort_by_time(tasks)
    times = [t.time for t in result]
    assert times == ["07:00", "12:00", "18:00"]


def test_sort_by_time_no_time_goes_last():
    """Tasks without a time attribute are pushed to the end."""
    scheduler = Scheduler()
    tasks = [
        Task(title="No time task", duration_minutes=10, priority=Priority.LOW, time=""),
        Task(title="Morning walk", duration_minutes=30, priority=Priority.HIGH, time="07:00"),
    ]
    result = scheduler.sort_by_time(tasks)
    assert result[0].title == "Morning walk"
    assert result[1].title == "No time task"


# ── Recurring Tasks ──────────────────────────────────────────────

def test_recurring_daily_creates_next_day():
    """Completing a daily recurring task creates a new instance for tomorrow."""
    today = date.today()
    task = Task(
        title="Morning walk", duration_minutes=30, priority=Priority.HIGH,
        recurring=True, recurrence_interval="daily", scheduled_date=today,
    )
    next_task = task.mark_completed()

    assert task.completed is True
    assert next_task is not None
    assert next_task.completed is False
    assert next_task.scheduled_date == today + timedelta(days=1)
    assert next_task.title == "Morning walk"
    assert next_task.recurring is True


def test_recurring_weekly_creates_next_week():
    """Completing a weekly recurring task creates a new instance 7 days later."""
    today = date.today()
    task = Task(
        title="Clean litter box", duration_minutes=10, priority=Priority.MEDIUM,
        recurring=True, recurrence_interval="weekly", scheduled_date=today,
    )
    next_task = task.mark_completed()

    assert next_task is not None
    assert next_task.scheduled_date == today + timedelta(days=7)


def test_non_recurring_returns_none():
    """Completing a non-recurring task returns None (no next occurrence)."""
    task = Task(title="Vet visit", duration_minutes=60, priority=Priority.HIGH)
    result = task.mark_completed()

    assert task.completed is True
    assert result is None


def test_complete_task_adds_next_to_pet():
    """Pet.complete_task auto-appends the next occurrence to the pet's task list."""
    pet = Pet(name="Mochi", species="dog", age=3)
    task = Task(
        title="Morning walk", duration_minutes=30, priority=Priority.HIGH,
        recurring=True, recurrence_interval="daily", scheduled_date=date.today(),
    )
    pet.add_task(task)
    assert len(pet.tasks) == 1

    pet.complete_task(task)
    assert len(pet.tasks) == 2
    assert pet.tasks[0].completed is True
    assert pet.tasks[1].completed is False


# ── Conflict Detection ───────────────────────────────────────────

def test_same_pet_conflict_detected():
    """Two overlapping tasks for the same pet produce a same-pet conflict."""
    scheduler = Scheduler()
    tasks = [
        Task(title="Clean litter box", duration_minutes=10, priority=Priority.MEDIUM,
             time="08:00", pet_name="Whiskers"),
        Task(title="Play with feather", duration_minutes=20, priority=Priority.LOW,
             time="08:05", pet_name="Whiskers"),
    ]
    conflicts = scheduler.detect_conflicts(tasks)

    assert len(conflicts) == 1
    assert "Same-pet conflict" in conflicts[0]


def test_cross_pet_conflict_detected():
    """Two overlapping tasks for different pets produce an owner conflict."""
    scheduler = Scheduler()
    tasks = [
        Task(title="Morning walk", duration_minutes=30, priority=Priority.HIGH,
             time="07:00", pet_name="Mochi"),
        Task(title="Feed breakfast", duration_minutes=10, priority=Priority.HIGH,
             time="07:00", pet_name="Whiskers"),
    ]
    conflicts = scheduler.detect_conflicts(tasks)

    assert len(conflicts) == 1
    assert "Owner conflict" in conflicts[0]


def test_no_conflict_when_times_dont_overlap():
    """Non-overlapping tasks produce no conflicts."""
    scheduler = Scheduler()
    tasks = [
        Task(title="Morning walk", duration_minutes=30, priority=Priority.HIGH,
             time="07:00", pet_name="Mochi"),
        Task(title="Feed breakfast", duration_minutes=10, priority=Priority.HIGH,
             time="08:00", pet_name="Whiskers"),
    ]
    conflicts = scheduler.detect_conflicts(tasks)
    assert conflicts == []


# ── Edge Cases ───────────────────────────────────────────────────

def test_schedule_with_no_tasks():
    """A pet with no tasks produces an empty schedule."""
    owner = Owner(name="Jordan", available_minutes=60)
    owner.add_pet(Pet(name="Mochi", species="dog", age=3))

    scheduler = Scheduler()
    schedule = scheduler.generate_schedule(owner)
    assert schedule == []


def test_schedule_skips_completed_tasks():
    """Completed tasks are excluded from the generated schedule."""
    pet = Pet(name="Mochi", species="dog", age=3)
    done_task = Task(title="Morning walk", duration_minutes=30, priority=Priority.HIGH, completed=True)
    open_task = Task(title="Brush coat", duration_minutes=15, priority=Priority.LOW)
    pet.add_task(done_task)
    pet.add_task(open_task)

    owner = Owner(name="Jordan", available_minutes=60)
    owner.add_pet(pet)

    scheduler = Scheduler()
    schedule = scheduler.generate_schedule(owner)
    assert len(schedule) == 1
    assert schedule[0].title == "Brush coat"


def test_schedule_respects_time_budget():
    """Tasks that exceed the remaining budget are skipped."""
    pet = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(Task(title="Long walk", duration_minutes=50, priority=Priority.HIGH))
    pet.add_task(Task(title="Short feed", duration_minutes=10, priority=Priority.MEDIUM))
    pet.add_task(Task(title="Grooming", duration_minutes=45, priority=Priority.LOW))

    owner = Owner(name="Jordan", available_minutes=60)
    owner.add_pet(pet)

    scheduler = Scheduler()
    schedule = scheduler.generate_schedule(owner)
    titles = [t.title for t in schedule]
    assert "Long walk" in titles
    assert "Short feed" in titles
    assert "Grooming" not in titles


def test_conflict_detection_skips_malformed_time():
    """Tasks with malformed times are skipped without crashing."""
    scheduler = Scheduler()
    tasks = [
        Task(title="Good task", duration_minutes=10, priority=Priority.HIGH,
             time="08:00", pet_name="Mochi"),
        Task(title="Bad task", duration_minutes=10, priority=Priority.LOW,
             time="not-a-time", pet_name="Mochi"),
    ]
    conflicts = scheduler.detect_conflicts(tasks)
    assert conflicts == []


def test_filter_by_pet():
    """filter_by_pet returns only tasks for the specified pet."""
    scheduler = Scheduler()
    tasks = [
        Task(title="Walk", duration_minutes=30, priority=Priority.HIGH, pet_name="Mochi"),
        Task(title="Feed", duration_minutes=10, priority=Priority.HIGH, pet_name="Whiskers"),
        Task(title="Brush", duration_minutes=15, priority=Priority.LOW, pet_name="Mochi"),
    ]
    result = scheduler.filter_by_pet(tasks, "Mochi")
    assert len(result) == 2
    assert all(t.pet_name == "Mochi" for t in result)


def test_filter_by_status():
    """filter_by_status splits tasks correctly by completion state."""
    scheduler = Scheduler()
    tasks = [
        Task(title="Walk", duration_minutes=30, priority=Priority.HIGH, completed=True),
        Task(title="Feed", duration_minutes=10, priority=Priority.HIGH, completed=False),
    ]
    done = scheduler.filter_by_status(tasks, completed=True)
    pending = scheduler.filter_by_status(tasks, completed=False)
    assert len(done) == 1 and done[0].title == "Walk"
    assert len(pending) == 1 and pending[0].title == "Feed"
