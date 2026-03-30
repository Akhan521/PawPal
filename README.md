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

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
