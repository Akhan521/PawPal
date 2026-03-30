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

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
