from pawpal_system import Task, Pet, Priority


def test_mark_completed():
    task = Task(title="Morning walk", duration_minutes=30, priority=Priority.HIGH)
    assert task.completed is False
    task.mark_completed()
    assert task.completed is True


def test_add_task_increases_count():
    pet = Pet(name="Mochi", species="dog", age=3)
    assert len(pet.tasks) == 0

    pet.add_task(Task(title="Morning walk", duration_minutes=30, priority=Priority.HIGH))
    assert len(pet.tasks) == 1

    pet.add_task(Task(title="Feed dinner", duration_minutes=10, priority=Priority.MEDIUM))
    assert len(pet.tasks) == 2
