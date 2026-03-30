import streamlit as st
from pawpal_system import Owner, Pet, Task, Priority, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("A pet care planning assistant — schedule, sort, filter, and detect conflicts.")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="", available_minutes=60)

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler()

st.divider()

# --- Owner setup ---
st.subheader("Owner Info")
owner_name = st.text_input("Owner name", value="Jordan")
available_minutes = st.number_input(
    "Available minutes today", min_value=1, max_value=480, value=60
)
st.session_state.owner.name = owner_name
st.session_state.owner.available_minutes = available_minutes

# --- Add a pet ---
st.subheader("Add a Pet")
col_pet1, col_pet2, col_pet3 = st.columns(3)
with col_pet1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col_pet2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col_pet3:
    pet_age = st.number_input("Age", min_value=0, max_value=30, value=3)

if st.button("Add pet"):
    existing_names = [p.name for p in st.session_state.owner.pets]
    if pet_name in existing_names:
        st.warning(f"{pet_name} is already added.")
    else:
        new_pet = Pet(name=pet_name, species=species, age=pet_age)
        st.session_state.owner.add_pet(new_pet)
        st.success(f"Added {pet_name} the {species}!")

if st.session_state.owner.pets:
    st.write("Current pets:")
    st.table([
        {"Name": p.name, "Species": p.species, "Age": p.age, "Tasks": len(p.tasks)}
        for p in st.session_state.owner.pets
    ])

st.divider()

# --- Add a task to a pet ---
st.subheader("Add a Task")

if st.session_state.owner.pets:
    pet_options = [p.name for p in st.session_state.owner.pets]
    selected_pet_name = st.selectbox("Assign to pet", pet_options)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["HIGH", "MEDIUM", "LOW"], index=0)

    col_time, col_recur, col_interval = st.columns(3)
    with col_time:
        task_time = st.text_input("Scheduled time (HH:MM)", value="", placeholder="e.g. 08:30")
    with col_recur:
        recurring = st.checkbox("Recurring task")
    with col_interval:
        recurrence_interval = st.selectbox(
            "Recurrence interval",
            ["daily", "weekly", "biweekly", "monthly"],
            disabled=not recurring,
        )

    if st.button("Add task"):
        selected_pet = next(
            p for p in st.session_state.owner.pets if p.name == selected_pet_name
        )
        new_task = Task(
            title=task_title,
            duration_minutes=int(duration),
            priority=Priority[priority],
            time=task_time,
            recurring=recurring,
            recurrence_interval=recurrence_interval if recurring else "",
        )
        selected_pet.add_task(new_task)
        st.success(f"Added '{task_title}' to {selected_pet_name}!")

    # --- Task display with sorting and filtering ---
    all_tasks = [t for p in st.session_state.owner.pets for t in p.tasks]

    if all_tasks:
        st.divider()
        st.subheader("All Tasks")

        scheduler = st.session_state.scheduler

        # Filtering controls
        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            filter_pet = st.selectbox(
                "Filter by pet", ["All pets"] + pet_options, key="filter_pet"
            )
        with filter_col2:
            filter_status = st.selectbox(
                "Filter by status", ["All", "Pending", "Completed"], key="filter_status"
            )

        # Apply filters
        filtered_tasks = all_tasks
        if filter_pet != "All pets":
            filtered_tasks = scheduler.filter_by_pet(filtered_tasks, filter_pet)
        if filter_status == "Pending":
            filtered_tasks = scheduler.filter_by_status(filtered_tasks, completed=False)
        elif filter_status == "Completed":
            filtered_tasks = scheduler.filter_by_status(filtered_tasks, completed=True)

        # Sort by time
        sorted_tasks = scheduler.sort_by_time(filtered_tasks)

        if sorted_tasks:
            st.table([
                {
                    "Pet": t.pet_name,
                    "Task": t.title,
                    "Time": t.time if t.time else "—",
                    "Duration": f"{t.duration_minutes} min",
                    "Priority": t.priority.name,
                    "Recurring": t.recurrence_interval if t.recurring else "—",
                    "Done": "Yes" if t.completed else "No",
                }
                for t in sorted_tasks
            ])
            st.caption(
                f"Showing {len(sorted_tasks)} of {len(all_tasks)} task(s), sorted by scheduled time."
            )
        else:
            st.info("No tasks match the current filters.")

        # --- Conflict detection ---
        timed_tasks = [t for t in all_tasks if t.time]
        if timed_tasks:
            conflicts = scheduler.detect_conflicts(all_tasks)
            if conflicts:
                st.warning(
                    f"**{len(conflicts)} scheduling conflict(s) detected:**\n\n"
                    + "\n".join(conflicts)
                )
            else:
                st.success("No scheduling conflicts detected.")

        # --- Recurring tasks summary ---
        recurring_tasks = scheduler.get_recurring_tasks(all_tasks)
        if recurring_tasks:
            with st.expander(f"Recurring Tasks ({len(recurring_tasks)})"):
                st.table([
                    {
                        "Pet": t.pet_name,
                        "Task": t.title,
                        "Interval": t.recurrence_interval,
                        "Next Date": str(t.scheduled_date) if t.scheduled_date else "—",
                    }
                    for t in recurring_tasks
                ])
    else:
        st.info("No tasks yet. Add one above.")
else:
    st.info("Add a pet first before creating tasks.")

st.divider()

# --- Generate schedule ---
st.subheader("Daily Schedule")

if st.button("Generate schedule"):
    owner = st.session_state.owner
    scheduler = st.session_state.scheduler

    if not owner.pets:
        st.warning("Add at least one pet first.")
    else:
        schedule = scheduler.generate_schedule(owner)
        if schedule:
            st.write(scheduler.explain_schedule(schedule))

            # Show conflict warnings for the generated schedule
            conflicts = scheduler.detect_conflicts(schedule)
            if conflicts:
                st.warning(
                    f"**{len(conflicts)} conflict(s) in your schedule:**\n\n"
                    + "\n".join(conflicts)
                )
            else:
                st.success("Schedule is conflict-free!")
        else:
            st.info("No tasks to schedule. Add some tasks first.")
