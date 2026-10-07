from pawpal_system import Owner, Pet, Task, Scheduler
from datetime import date

# Create an owner
owner = Owner("Naviyah")

# Create two pets
bella = Pet("Bella", "Dog")
milo = Pet("Milo", "Cat")

# Add pets to owner
owner.add_pet(bella)
owner.add_pet(milo)

# Create three tasks with different times
task1 = Task("Feed Bella", "08:00", due_date=date.today())
task2 = Task("Walk Bella", "10:00", due_date=date.today())
task3 = Task("Feed Milo", "18:00", due_date=date.today())

# Add tasks to pets
bella.add_task(task1)
bella.add_task(task2)
milo.add_task(task3)

# Create the scheduler
scheduler = Scheduler(owner)

# Get today's schedule
schedule = scheduler.get_todays_schedule()

# Print today's schedule
print("Today's Schedule")
print("----------------")

for task in schedule:
    print(f"{task.time} - {task.pet_name}: {task.description}")