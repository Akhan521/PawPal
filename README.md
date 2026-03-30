# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Smarter Scheduling

The Scheduler in `pawpal_system.py` goes beyond basic priority sorting with these features:

- **Sort by time** (`sort_by_time`) — Orders tasks chronologically by HH:MM using a lambda key; tasks without a time slot are pushed to the end.
- **Filter by pet or status** (`filter_by_pet`, `filter_by_status`) — Narrow a task list by pet name or completion state using list comprehensions.
- **Recurring tasks** (`mark_completed`, `complete_task`) — When a recurring task is completed, `timedelta` calculates the next occurrence date (daily, weekly, biweekly, or monthly) and a new Task instance is auto-added to the pet's list.
- **Conflict detection** (`detect_conflicts`) — Compares every pair of timed tasks using precomputed start/end minutes. Labels overlaps as "Same-pet conflict" or "Owner conflict" (cross-pet). An early break on the sorted list avoids unnecessary comparisons. Malformed times are skipped gracefully.

### Testing PawPal+

Activate the virtual environment and run the test suite:

```bash
source venv/Scripts/activate   # Windows
# source venv/bin/activate     # macOS / Linux
python -m pytest tests/test_pawpal.py -v
```

#### Sorting (Confidence: 5/5)

| Test | What it covers |
|------|---------------|
| `test_sort_by_time_chronological_order` | Tasks added out of order are returned in correct HH:MM sequence |
| `test_sort_by_time_no_time_goes_last` | Tasks with no scheduled time are placed at the end of the sorted list |

Both tests are deterministic with no external dependencies. The lambda key logic is straightforward to verify.

#### Recurring Tasks (Confidence: 5/5)

| Test | What it covers |
|------|---------------|
| `test_recurring_daily_creates_next_day` | Completing a daily task creates a new instance dated tomorrow via `timedelta(days=1)` |
| `test_recurring_weekly_creates_next_week` | Completing a weekly task creates a new instance dated 7 days later |
| `test_non_recurring_returns_none` | Completing a non-recurring task returns `None` (no next occurrence) |
| `test_complete_task_adds_next_to_pet` | `Pet.complete_task` appends the next occurrence to the pet's task list automatically |

Date arithmetic is handled entirely by `timedelta`, which is well-tested in the Python standard library. Each interval mapping is verified independently.

#### Conflict Detection (Confidence: 4/5)

| Test | What it covers |
|------|---------------|
| `test_same_pet_conflict_detected` | Two overlapping tasks for the same pet are flagged as "Same-pet conflict" |
| `test_cross_pet_conflict_detected` | Two overlapping tasks for different pets are flagged as "Owner conflict" |
| `test_no_conflict_when_times_dont_overlap` | Non-overlapping tasks produce zero conflicts |

Scored 4/5 because the current tests cover two-task pairs. More complex scenarios (three-way overlaps, tasks that share an exact end/start boundary) would raise confidence further.

#### Edge Cases (Confidence: 5/5)

| Test | What it covers |
|------|---------------|
| `test_schedule_with_no_tasks` | A pet with no tasks produces an empty schedule |
| `test_schedule_skips_completed_tasks` | Completed tasks are excluded from the generated schedule |
| `test_schedule_respects_time_budget` | Tasks that would exceed the remaining time budget are skipped |
| `test_conflict_detection_skips_malformed_time` | Malformed time strings (e.g. `"not-a-time"`) are skipped without crashing |

These guard against the most common failure modes: empty inputs, stale data, and bad user input.

#### Filtering (Confidence: 5/5)

| Test | What it covers |
|------|---------------|
| `test_filter_by_pet` | `filter_by_pet` returns only tasks matching the given pet name |
| `test_filter_by_status` | `filter_by_status` correctly splits tasks by completed vs. pending |

Simple list comprehension logic with clear inputs and outputs.

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
