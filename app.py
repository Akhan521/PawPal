import streamlit as st
from pawpal_system import Owner, Pet, Task, Priority, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

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

    if st.button("Add task"):
        selected_pet = next(
            p for p in st.session_state.owner.pets if p.name == selected_pet_name
        )
        new_task = Task(
            title=task_title,
            duration_minutes=int(duration),
            priority=Priority[priority],
        )
        selected_pet.add_task(new_task)
        st.success(f"Added '{task_title}' to {selected_pet_name}!")

    # Show all tasks across all pets
    all_tasks = []
    for p in st.session_state.owner.pets:
        for t in p.tasks:
            all_tasks.append({
                "Pet": t.pet_name,
                "Task": t.title,
                "Duration": f"{t.duration_minutes} min",
                "Priority": t.priority.name,
                "Done": t.completed,
            })
    if all_tasks:
        st.write("All tasks:")
        st.table(all_tasks)
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
        else:
            st.info("No tasks to schedule. Add some tasks first.")
