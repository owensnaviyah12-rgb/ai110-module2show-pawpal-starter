from datetime import time

import streamlit as st

from pawpal_system import PRIORITIES, Owner, Pet, Scheduler, Task

DATA_FILE = "data.json"
PRIORITY_ICON = {"high": "🔴 high", "medium": "🟡 medium", "low": "🟢 low"}


def save() -> None:
    """Persist the owner, pets and tasks to JSON."""
    st.session_state.owner.save_to_json(DATA_FILE)


def task_rows(tasks) -> list[dict]:
    """Turn tasks into rows for st.table."""
    return [
        {
            "": "✅" if t.completed else "⬜",
            "Date": str(t.due_date),
            "Time": f"{t.time}-{t.end_time}",
            "Pet": t.pet_name,
            "Task": t.description,
            "Priority": PRIORITY_ICON[t.priority],
            "Repeats": t.frequency,
        }
        for t in tasks
    ]


# --------------------------------------------------
# Session state (loads saved data once per session)
# --------------------------------------------------

if "owner" not in st.session_state:
    st.session_state.owner = Owner.load_or_create("Naviyah", DATA_FILE)

owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)  # always looks at the current owner

# --------------------------------------------------
# Page
# --------------------------------------------------

st.title("🐾 PawPal+")
st.write(f"Manage {owner.name}'s pets and care tasks. Everything is saved automatically.")

# --------------------------------------------------
# Add a pet
# --------------------------------------------------

st.header("Add a Pet")

pet_name = st.text_input("Pet Name")
pet_species = st.text_input("Species")

if st.button("Add Pet"):
    if pet_name.strip() and pet_species.strip():
        try:
            owner.add_pet(Pet(pet_name.strip(), pet_species.strip()))
            save()
            st.success(f"{pet_name.strip()} was added!")
        except ValueError as error:
            st.error(str(error))
    else:
        st.warning("Please enter both a pet name and species.")

st.header("My Pets")

if owner.pets:
    for pet in owner.pets:
        st.write(f"🐾 **{pet.name}** — {pet.species} ({len(pet.tasks)} tasks)")
else:
    st.info("No pets have been added yet.")

# --------------------------------------------------
# Schedule a task
# --------------------------------------------------

st.header("Schedule a Task")

if owner.pets:
    selected_pet = st.selectbox("Choose a pet", [pet.name for pet in owner.pets])
    description = st.text_input("Task Description")
    task_time = st.time_input("Time", value=time(8, 0))
    duration = st.number_input("Duration (minutes)", min_value=5, max_value=480, value=30, step=5)
    priority = st.selectbox("Priority", list(PRIORITIES), index=1)
    frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])

    if st.button("Add Task"):
        if description.strip():
            try:
                owner.get_pet(selected_pet).add_task(
                    Task(
                        description=description.strip(),
                        time=task_time.strftime("%H:%M"),
                        frequency=frequency,
                        duration_minutes=int(duration),
                        priority=priority,
                    )
                )
                save()
                st.success(f"Task added for {selected_pet}!")
            except ValueError as error:
                st.error(str(error))
        else:
            st.warning("Please enter a task description.")
else:
    st.info("Add a pet before scheduling a task.")

# --------------------------------------------------
# Today's schedule
# --------------------------------------------------

st.header("Today's Schedule")

todays = scheduler.get_todays_schedule()

if todays:
    st.table(task_rows(todays))
    pending = [t for t in todays if not t.completed]
    if pending:
        st.subheader("Mark a task complete")
        for index, task in enumerate(pending):
            label_col, button_col = st.columns([4, 1])
            label_col.write(f"**{task.time}** — {task.pet_name}: {task.description}")
            if button_col.button("Done", key=f"done-{index}-{task.pet_name}-{task.time}-{task.description}"):
                owner.get_pet(task.pet_name).complete_task(task)  # adds the next repeat, if any
                save()
                st.rerun()
else:
    st.info("No tasks scheduled for today.")

# --------------------------------------------------
# Conflicts
# --------------------------------------------------

st.header("Schedule Conflicts")

conflicts = scheduler.detect_conflicts()

if conflicts:
    for conflict in conflicts:
        st.warning(conflict)
else:
    st.success("No scheduling conflicts detected.")

# --------------------------------------------------
# Time-blocked plan
# --------------------------------------------------

st.header("Suggested Daily Plan")
st.caption("High-priority tasks keep their time; lower-priority tasks shift to avoid overlaps.")

plan = scheduler.build_daily_plan()

if plan:
    st.table(
        [
            {
                "Time": f"{item.start}-{item.end}" if item.start else "--",
                "Pet": item.task.pet_name,
                "Task": item.task.description,
                "Priority": PRIORITY_ICON[item.task.priority],
                "Note": (
                    "❌ no room today" if item.start is None
                    else f"↪ moved from {item.task.time}" if item.moved
                    else "on time"
                ),
            }
            for item in plan
        ]
    )
else:
    st.info("Nothing to plan for today.")

# --------------------------------------------------
# Next available slot
# --------------------------------------------------

st.header("Find a Free Slot")

slot_minutes = st.number_input("How many minutes do you need?", min_value=5, max_value=480, value=30, step=5, key="slot_minutes")

if st.button("Find next available slot"):
    slot = scheduler.find_next_available_slot(int(slot_minutes))
    if slot:
        st.success(f"Next free {int(slot_minutes)}-minute slot today: {slot}")
    else:
        st.warning("No free slot of that length between 08:00 and 20:00 today.")

# --------------------------------------------------
# Filter tasks
# --------------------------------------------------

st.header("Filter Tasks")

pet_choice = st.selectbox("Pet", ["All pets"] + [pet.name for pet in owner.pets], key="filter_pet")
status_choice = st.radio("Status", ["All", "Incomplete", "Completed"], horizontal=True)

filtered = scheduler.filter_tasks(
    pet_name=None if pet_choice == "All pets" else pet_choice,
    completed={"All": None, "Incomplete": False, "Completed": True}[status_choice],
)

if filtered:
    st.table(task_rows(scheduler.sort_by_time(filtered)))
else:
    st.info("No tasks match this filter.")
