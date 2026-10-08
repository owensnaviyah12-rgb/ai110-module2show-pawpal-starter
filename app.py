import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler


# --------------------------------------------------
# Session State
# --------------------------------------------------

if "owner" not in st.session_state:
    st.session_state.owner = Owner("Naviyah")

owner = st.session_state.owner

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(owner)

scheduler = st.session_state.scheduler


# --------------------------------------------------
# Page
# --------------------------------------------------

st.title("🐾 PawPal+")

st.write("Manage your pets and their care tasks.")


# --------------------------------------------------
# Add a Pet
# --------------------------------------------------

st.header("Add a Pet")

pet_name = st.text_input("Pet Name")
pet_species = st.text_input("Species")

if st.button("Add Pet"):
    if pet_name and pet_species:
        new_pet = Pet(pet_name, pet_species)
        owner.add_pet(new_pet)

        st.success(f"{pet_name} was added!")
    else:
        st.warning("Please enter both a pet name and species.")


# --------------------------------------------------
# Display Pets
# --------------------------------------------------

st.header("My Pets")

if owner.pets:
    for pet in owner.pets:
        st.write(f"🐾 **{pet.name}** — {pet.species}")
else:
    st.info("No pets have been added yet.")


# --------------------------------------------------
# Add a Task
# --------------------------------------------------

st.header("Schedule a Task")

if owner.pets:

    pet_names = [pet.name for pet in owner.pets]

    selected_pet = st.selectbox(
        "Choose a pet",
        pet_names
    )

    description = st.text_input("Task Description")

    task_time = st.text_input(
        "Time",
        placeholder="HH:MM"
    )

    frequency = st.selectbox(
        "Frequency",
        ["once", "daily", "weekly"]
    )

    if st.button("Add Task"):

        if description and task_time:

            selected_pet_object = next(
                pet
                for pet in owner.pets
                if pet.name == selected_pet
            )

            new_task = Task(
                description=description,
                time=task_time,
                frequency=frequency
            )

            selected_pet_object.add_task(new_task)

            st.success(
                f"Task added for {selected_pet}!"
            )

        else:
            st.warning(
                "Please enter a description and time."
            )

else:
    st.info("Add a pet before scheduling a task.")


# --------------------------------------------------
# Today's Schedule
# --------------------------------------------------

st.header("Today's Schedule")

schedule = scheduler.get_todays_schedule()

if schedule:

    for task in schedule:

        status = "✅" if task.completed else "⬜"

        st.write(
            f"{status} **{task.time}** — "
            f"{task.pet_name}: "
            f"{task.description}"
        )

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