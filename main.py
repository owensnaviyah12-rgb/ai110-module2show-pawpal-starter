from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler


# Create an owner
owner = Owner("Naviyah")

# Create two pets
bella = Pet("Bella", "Dog")
milo = Pet("Milo", "Cat")

# Add pets to the owner
owner.add_pet(bella)
owner.add_pet(milo)


# Create tasks with different times
task1 = Task(
    "Feed Bella",
    "18:00",
    due_date=date.today()
)

task2 = Task(
    "Walk Bella",
    "08:00",
    due_date=date.today()
)

task3 = Task(
    "Feed Milo",
    "12:00",
    due_date=date.today()
)

# Add tasks to pets
bella.add_task(task1)
bella.add_task(task2)
milo.add_task(task3)


# Create scheduler
scheduler = Scheduler(owner)


# Today's Schedule
print("Today's Schedule")
print("----------------")

schedule = scheduler.get_todays_schedule()

for task in schedule:
    print(
        f"{task.time} - "
        f"{task.pet_name}: "
        f"{task.description}"
    )


# Filtering
print("\nBella's Tasks")
print("-------------")

bella_tasks = scheduler.filter_tasks(pet_name="Bella")

for task in bella_tasks:
    print(
        f"{task.time} - "
        f"{task.description}"
    )


# Completion filtering
print("\nIncomplete Tasks")
print("----------------")

incomplete_tasks = scheduler.filter_tasks(completed=False)

for task in incomplete_tasks:
    print(
        f"{task.time} - "
        f"{task.pet_name}: "
        f"{task.description}"
    )


# Test recurring task
print("\nRecurring Task Test")
print("-------------------")

daily_task = Task(
    "Give Bella medicine",
    "09:00",
    frequency="daily",
    due_date=date.today()
)

bella.add_task(daily_task)

print(f"Original date: {daily_task.due_date}")

next_task = daily_task.mark_complete()

if next_task is not None:
    print(f"Next occurrence: {next_task.due_date}")


# Add the next recurring task
if next_task is not None:
    bella.add_task(next_task)


# Conflict detection
print("\nTask Conflicts")
print("--------------")

conflict_task1 = Task(
    "Give Bella medicine",
    "12:00",
    due_date=date.today()
)

conflict_task2 = Task(
    "Give Milo medicine",
    "12:00",
    due_date=date.today()
)

bella.add_task(conflict_task1)
milo.add_task(conflict_task2)

conflicts = scheduler.detect_conflicts()

if conflicts:
    for conflict in conflicts:
        print(conflict)
else:
    print("No conflicts detected.")