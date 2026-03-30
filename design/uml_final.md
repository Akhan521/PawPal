# PawPal+ Final UML Class Diagram

## Changes from Phase 1

| Area | Phase 1 (Initial) | Final Implementation |
|---|---|---|
| **Task fields** | `title`, `duration_minutes`, `priority` (str), `completed` | Added `pet_name`, `time`, `recurring`, `recurrence_interval`, `scheduled_date` |
| **Task.mark_completed()** | Returns `void` | Returns `Task` or `None` (creates next occurrence for recurring tasks) |
| **Priority** | Plain string attribute on Task | Dedicated `IntEnum` class (`LOW=1`, `MEDIUM=2`, `HIGH=3`) |
| **Pet methods** | `add_task`, `remove_task` | Added `complete_task()` for recurring auto-scheduling |
| **Scheduler methods** | `generate_schedule`, `explain_schedule` | Added `sort_by_time`, `filter_by_pet`, `filter_by_status`, `detect_conflicts`, `get_recurring_tasks`, plus private helpers |
| **Module constants** | None | `INTERVAL_DAYS` dict mapping recurrence strings to day counts |

```mermaid
classDiagram
    class Priority {
        <<IntEnum>>
        LOW = 1
        MEDIUM = 2
        HIGH = 3
    }

    class Task {
        +String title
        +int duration_minutes
        +Priority priority
        +String pet_name
        +bool completed
        +String time
        +bool recurring
        +String recurrence_interval
        +date scheduled_date
        +mark_completed() Task?
    }

    class Pet {
        +String name
        +String species
        +int age
        +list~Task~ tasks
        +add_task(task: Task) void
        +remove_task(task: Task) void
        +complete_task(task: Task) Task?
    }

    class Owner {
        +String name
        +int available_minutes
        +list~Pet~ pets
        +add_pet(pet: Pet) void
        +remove_pet(pet: Pet) void
    }

    class Scheduler {
        +generate_schedule(owner: Owner) list~Task~
        +sort_by_time(tasks: list~Task~) list~Task~
        +filter_by_pet(tasks: list~Task~, pet_name: String) list~Task~
        +filter_by_status(tasks: list~Task~, completed: bool) list~Task~
        +detect_conflicts(tasks: list~Task~) list~String~
        +get_recurring_tasks(tasks: list~Task~) list~Task~
        +explain_schedule(schedule: list~Task~) String
        -_time_to_minutes(time_str: String) int?
        -_tasks_overlap(a: Task, b: Task) bool
    }

    Owner "1" --> "0..*" Pet : owns
    Pet "1" --> "0..*" Task : has
    Task --> Priority : uses
    Scheduler ..> Owner : schedules for
    Scheduler ..> Task : sorts, filters, detects conflicts
    Pet ..> Task : completes and auto-reschedules
```
