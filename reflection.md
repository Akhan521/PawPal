# PawPal+ Project Reflection

## 1. System Design

Three core actions include:
1. Adding a pet
2. Viewing the current day's schedule
3. Adding or editing tasks for the current day

**a. Initial design**

- Briefly describe your initial UML design.

Our initial UML design will include four core classes: Owner, Pet, Task, and Scheduler. The owner class will contain all information regarding the owner and their pets. The pet class will contain all information regarding the pet, such as their name, species, and age. The task class will contain all information regarding the task, such as the task name, duration, and priority. The scheduler class will contain the logic for scheduling the tasks for the current day.

- What classes did you include, and what responsibilities did you assign to each?

As mentioned above, our UML design will include four core classes: Owner, Pet, Task, and Scheduler. The owner should be able to add or edit pets and view the pets they have. Pets should be able to have tasks assigned to them and view the tasks they have. We should be able to edit tasks to change the duration or priority. Lastly, we should be able to specify the logic for scheduling the tasks for the current day.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, our design changed in three ways during implementation:

1. **Scheduler became stateless.** Originally it stored `owner`, `pet`, and `available_minutes` as attributes. We removed those and made `generate_schedule(owner)` accept the Owner as a parameter instead, since the Scheduler doesn't need to hold state; it just processes inputs and returns a plan.

2. **Priority changed from `str` to `IntEnum`.** A free-form string like `"high"` can't be sorted or compared directly. Using `IntEnum` (LOW=1, MEDIUM=2, HIGH=3) gives natural ordering, which keeps the scheduling logic clean.

3. **Added `pet_name` to Task.** The scheduler collects tasks across all pets into a flat list. Without a back-reference, there's no way to tell which pet a task belongs to when displaying the schedule. Adding `pet_name` solves this without introducing a circular reference.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

Our scheduler considers three primary constraints:

1. **Priority**: Each task carries a `Priority` value (`HIGH=3`, `MEDIUM=2`, `LOW=1`) implemented as an `IntEnum`. The scheduler sorts all incomplete tasks by priority in descending order so that the most critical tasks (feeding, medication) are always scheduled first.

2. **Time budget**: The owner sets an `available_minutes` value representing how much time they have for pet care that day. The scheduler greedily packs tasks into this budget, skipping any task whose duration would exceed the remaining minutes.

3. **Completion status**: Only incomplete tasks (`completed=False`) are considered for scheduling. This prevents already-finished tasks from consuming budget and ensures the schedule reflects what still needs to be done.

Beyond the core scheduling algorithm, we also layered in two supporting constraints:

4. **Scheduled time and conflicts**: Tasks can optionally carry a `time` field in `HH:MM` format. The `detect_conflicts` method checks every pair of timed tasks for overlapping windows and labels them as same-pet or cross-pet (owner) conflicts, giving the user visibility into double-bookings.

5. **Recurrence**: Recurring tasks automatically generate a next occurrence when completed, so they are never lost from future schedules.

We decided priority and time budget mattered most because a pet owner's primary concern is ensuring the highest-impact tasks always happen, even on a tight schedule. Completion status was a natural filter to avoid redundant work. Conflict detection and recurrence were added as second-order constraints because they improve the quality of the schedule without affecting which tasks get selected; they help the owner execute the plan, not build it.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

Our scheduler uses a greedy algorithm: it sorts all incomplete tasks by priority (highest first) and packs them into the owner's time budget one by one until there is no room left. This means it may leave time on the table. For example, if the budget has 10 minutes remaining and the next task in priority order takes 15 minutes, it skips that task entirely, even if a lower-priority 10-minute task would fit perfectly. An optimal knapsack algorithm could find the combination of tasks that fills the budget most efficiently, but it would add significant complexity for a marginal benefit.

This tradeoff is reasonable for a pet-care scenario because an owner's top concern is that the most important tasks, like feeding or a medical routine, always get scheduled first. Squeezing in an extra low-priority task at the cost of more complex, harder-to-debug logic is not worth it when the user base is a single pet owner managing a handful of daily tasks.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I utilized AI coding tools like Claude Code throughout this project for design, brainstorming, debugging, refactoring, as well as even challenging my own ideas. The most helpful prompts and questions were those targeting clarifying details about the project, including going against my own ideas or thoughts so as to uncover any of my hidden assumptions or details that could lead to future bottlenecks in logic. I noticed that the most helpful conversations I've had with my AI coding tools came from deeply analyzing the work that I've already done in order to uncover whether it had any logic errors or concerns. Another great use case of AI tools in this project came from updating my documentation to be more accurate and concise.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

One moment where I did not accept an AI suggestion as is was when I asked Claude Code to produce the generate_schedule method for me in pawpal_system.py. It initially suggested that I provide only a single pet into this method, which was not practical for our scenario. I realized that it would be more beneficial to provide the owner as a parameter to this method, so that we would have indirect access to the pets' task lists. By clarifying this detail to Claude Code, I was able to revise and update our generate_schedule method to accept the Owner object as an argument, which would then aggregate information about all pets an owner has as well as their task lists. By proposing this idea and passing it along to the AI coding tool, we were able to have a discussion about why my approach would be more beneficial and practical for the PawPal project.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

We tested 15 behaviors across five categories:

1. **Sorting (2 tests)**: Verified that `sort_by_time` returns tasks in correct `HH:MM` chronological order and that tasks without a scheduled time are pushed to the end. These tests matter because the sorted task table in the UI depends on this ordering being correct.

2. **Recurring tasks (4 tests)**: Verified that completing a daily recurring task creates a new instance dated tomorrow, a weekly task creates one 7 days later, a non-recurring task returns `None`, and that `Pet.complete_task` auto-appends the next occurrence to the pet's task list. These tests matter because recurring logic involves date arithmetic with `timedelta` and automatic list mutation, two areas where off-by-one errors or missed appends could silently break future schedules.

3. **Conflict detection (3 tests)**: Verified that two overlapping tasks for the same pet produce a "Same-pet conflict," two overlapping tasks for different pets produce an "Owner conflict," and non-overlapping tasks produce zero conflicts. These tests matter because the conflict detection algorithm uses pairwise comparisons with an early break optimization; incorrect overlap math would either miss real conflicts or flag false ones.

4. **Edge cases (4 tests)**: Verified that a pet with no tasks produces an empty schedule, completed tasks are excluded from scheduling, tasks exceeding the remaining time budget are skipped, and malformed time strings (e.g., `"not-a-time"`) are skipped without crashing. These guard against the most common failure modes: empty inputs, stale data, budget overflow, and bad user input.

5. **Filtering (2 tests)**: Verified that `filter_by_pet` returns only tasks matching a given pet name and `filter_by_status` correctly splits tasks by completed vs. pending. These tests matter because the Streamlit UI exposes both filters as dropdowns, and incorrect filtering would show the user wrong data.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

We are highly confident in the scheduler's correctness. All 15 tests pass, covering the core scheduling algorithm, sorting, filtering, recurring task lifecycle, conflict detection, and common edge cases. The sorting and filtering logic scored 5/5 confidence because they rely on simple, deterministic list operations. Recurring tasks also scored 5/5 because the date arithmetic is handled entirely by Python's `timedelta`, which is well-tested in the standard library. Conflict detection scored 4/5; the current tests cover two-task pair scenarios, but more complex cases would raise confidence further.

If we had more time, we would test the following edge cases:

- **Three-way overlaps**: three tasks all overlapping at the same time to ensure every conflict pair is reported.
- **Exact boundary adjacency**: a task ending at 08:30 and another starting at 08:30 to confirm they are not flagged as conflicting.
- **All tasks exceed the budget**: every task is longer than `available_minutes`, producing an empty schedule.
- **Multiple pets with identical task names**: ensuring `filter_by_pet` distinguishes them correctly by `pet_name`, not by `title`.
- **Recurring task with no `scheduled_date`**: verifying that `mark_completed` falls back to `date.today()` when no date is set.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I'm most satisfied with just how involved I was in the process of leading my coding tools like Claude Code in developing this project. I found it a great learning experience, having my ideas tested and challenged with these AI tools and having conversations with Claude Code to improve upon the ideas that I had, which weren't as fleshed out. I also find it really fun to first start with our UML diagrams and to then transition into Python stubs, which we then flesh out throughout our project.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

If I had another iteration, I would improve the way that I approach my coding tools like Claude Code. I would try to be more specific and detailed in my prompts from the get-go, especially during our UML design, so that my AI tools could have a more targeted approach to our code implementations. I would also try to be more thorough in my testing and verification of my code, so that I can be more confident in the correctness of my code.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

One important thing I learned about designing systems or working with AI on this project is that it's important to be specific and detailed in your prompts to your AI tools. It's also important to be thorough in your testing and verification of your code, so that you can be more confident in the correctness of your code. Additionally, it's important to be open to feedback and criticism from your AI tools, and to be willing to revise and improve upon your ideas based on the feedback you receive. But it's also just as important to realize that we are also capable of challenging the AI's assumptions and suggestions. 
