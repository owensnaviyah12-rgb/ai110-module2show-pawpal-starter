from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional


@dataclass
class Task:
    """A single pet care activity."""

    description: str
    time: str
    frequency: str = "once"
    due_date: date = field(default_factory=date.today)
    completed: bool = False
    pet_name: str = ""

    def mark_complete(self) -> Optional["Task"]:
        """Mark the task complete and create its next occurrence if recurring."""
        self.completed = True

        if self.frequency == "daily":
            return Task(
                description=self.description,
                time=self.time,
                frequency=self.frequency,
                due_date=self.due_date + timedelta(days=1),
                pet_name=self.pet_name,
            )

        if self.frequency == "weekly":
            return Task(
                description=self.description,
                time=self.time,
                frequency=self.frequency,
                due_date=self.due_date + timedelta(weeks=1),
                pet_name=self.pet_name,
            )

        return None


@dataclass
class Pet:
    """A pet and the care tasks assigned to it."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet and tag it with the pet's name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def get_tasks(self) -> list[Task]:
        """Return all tasks for this pet."""
        return self.tasks


class Owner:
    """A pet owner who manages one or more pets."""

    def __init__(self, name: str) -> None:
        """Create an owner with an empty pet list."""
        self.name: str = name
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.get_tasks()]


class Scheduler:
    """The brain that organizes tasks across all of an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        """Create a scheduler for the given owner."""
        self.owner: Owner = owner

    def get_todays_schedule(self) -> list[Task]:
        """Return today's tasks sorted by time."""
        today = date.today()
        todays = [
            task
            for task in self.owner.get_all_tasks()
            if task.due_date == today
        ]
        return self.sort_by_time(todays)

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted by their HH:MM time."""
        return sorted(tasks, key=lambda task: task.time)

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> list[Task]:
        """Return tasks filtered by pet name and/or completion status."""
        tasks = self.owner.get_all_tasks()

        if pet_name is not None:
            tasks = [
                task for task in tasks
                if task.pet_name == pet_name
            ]

        if completed is not None:
            tasks = [
                task for task in tasks
                if task.completed == completed
            ]

        return tasks

    def detect_conflicts(self) -> list[str]:
        """Return warnings for tasks scheduled at the same time."""
        tasks = self.owner.get_all_tasks()
        conflicts = []

        for i in range(len(tasks)):
            for j in range(i + 1, len(tasks)):
                if tasks[i].time == tasks[j].time:
                    conflicts.append(
                        f"Conflict: {tasks[i].pet_name} and "
                        f"{tasks[j].pet_name} both have tasks at "
                        f"{tasks[i].time}."
                    )

        return conflicts