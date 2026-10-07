"""PawPal+ logic layer: core classes for pets, tasks, owners, and scheduling."""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class Task:
    """A single pet care activity."""

    description: str
    time: str  # "HH:MM" (zero-padded, 24-hour)
    frequency: str = "once"  # "once", "daily", or "weekly"
    due_date: date = field(default_factory=date.today)
    completed: bool = False
    pet_name: str = ""

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True


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
        self.name: str = name
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.get_tasks()]


class Scheduler:
    """The 'brain' that organizes tasks across all of an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        self.owner: Owner = owner

    def get_todays_schedule(self) -> list[Task]:
        """Return today's tasks, sorted by time."""
        today = date.today()
        todays = [t for t in self.owner.get_all_tasks() if t.due_date == today]
        return self.sort_by_time(todays)

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return the given tasks sorted by their HH:MM time."""
        return sorted(tasks, key=lambda t: t.time)

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> list[Task]:
        """Return tasks filtered by pet name and/or completion status."""
        pass

    def detect_conflicts(self) -> list[str]:
        """Return warning messages for tasks scheduled at the same time."""
        pass