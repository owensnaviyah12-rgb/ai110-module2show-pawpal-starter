import json
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

PRIORITIES = ("high", "medium", "low")
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}
DEFAULT_DURATION = 30  # minutes


# ----------------------------------------------------------------------
# Time helpers
# ----------------------------------------------------------------------

def to_minutes(time_str: str) -> int:
    """Convert 'H:MM' or 'HH:MM' into minutes after midnight.

    Raises ValueError for anything that is not a valid 24-hour time.
    """
    try:
        hour_str, minute_str = time_str.strip().split(":")
        hour, minute = int(hour_str), int(minute_str)
    except (ValueError, AttributeError):
        raise ValueError(f"Invalid time '{time_str}'. Use HH:MM (24-hour).") from None
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError(f"Invalid time '{time_str}'. Use HH:MM (24-hour).")
    return hour * 60 + minute


def to_hhmm(minutes: int) -> str:
    """Convert minutes after midnight into a zero-padded 'HH:MM' string."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


# ----------------------------------------------------------------------
# Task
# ----------------------------------------------------------------------

@dataclass
class Task:
    """A single pet care activity."""

    description: str
    time: str
    frequency: str = "once"
    due_date: date = field(default_factory=date.today)
    completed: bool = False
    pet_name: str = ""
    duration_minutes: int = DEFAULT_DURATION
    priority: str = "medium"

    def __post_init__(self) -> None:
        """Validate the time, priority, frequency and duration."""
        to_minutes(self.time)  # raises ValueError if the time is invalid
        if self.priority not in PRIORITIES:
            raise ValueError(f"Priority must be one of {PRIORITIES}.")
        if self.frequency not in ("once", "daily", "weekly"):
            raise ValueError("Frequency must be 'once', 'daily' or 'weekly'.")
        if self.duration_minutes <= 0:
            raise ValueError("Duration must be a positive number of minutes.")
        if self.start_minutes + self.duration_minutes > 24 * 60:
            raise ValueError("A task cannot run past midnight; shorten it or start it earlier.")

    @property
    def start_minutes(self) -> int:
        """Start time as minutes after midnight."""
        return to_minutes(self.time)

    @property
    def end_time(self) -> str:
        """End time as 'HH:MM' (start plus duration)."""
        return to_hhmm(self.start_minutes + self.duration_minutes)

    def mark_complete(self) -> Optional["Task"]:
        """Mark the task complete and return its next occurrence if recurring."""
        self.completed = True
        if self.frequency == "daily":
            delta = timedelta(days=1)
        elif self.frequency == "weekly":
            delta = timedelta(weeks=1)
        else:
            return None
        return Task(
            description=self.description,
            time=self.time,
            frequency=self.frequency,
            due_date=self.due_date + delta,
            pet_name=self.pet_name,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
        )

    def to_dict(self) -> dict:
        """Return a JSON-friendly dictionary for saving."""
        return {
            "description": self.description,
            "time": self.time,
            "frequency": self.frequency,
            "due_date": self.due_date.isoformat(),
            "completed": self.completed,
            "pet_name": self.pet_name,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Rebuild a Task from a dictionary created by to_dict()."""
        return cls(
            description=data["description"],
            time=data["time"],
            frequency=data.get("frequency", "once"),
            due_date=date.fromisoformat(data["due_date"]),
            completed=data.get("completed", False),
            pet_name=data.get("pet_name", ""),
            duration_minutes=data.get("duration_minutes", DEFAULT_DURATION),
            priority=data.get("priority", "medium"),
        )


# ----------------------------------------------------------------------
# Pet
# ----------------------------------------------------------------------

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

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet."""
        self.tasks.remove(task)

    def complete_task(self, task: Task) -> Optional[Task]:
        """Complete a task and automatically add its next occurrence, if any."""
        next_task = task.mark_complete()
        if next_task is not None:
            self.add_task(next_task)
        return next_task

    def to_dict(self) -> dict:
        """Return a JSON-friendly dictionary for saving."""
        return {
            "name": self.name,
            "species": self.species,
            "tasks": [task.to_dict() for task in self.tasks],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Pet":
        """Rebuild a Pet (and its tasks) from a dictionary."""
        pet = cls(name=data["name"], species=data["species"])
        for task_data in data.get("tasks", []):
            pet.add_task(Task.from_dict(task_data))
        return pet


# ----------------------------------------------------------------------
# Owner
# ----------------------------------------------------------------------

class Owner:
    """A pet owner who manages one or more pets."""

    def __init__(self, name: str) -> None:
        """Create an owner with an empty pet list."""
        self.name: str = name
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner (pet names must be unique)."""
        if self.get_pet(pet.name) is not None:
            raise ValueError(f"{pet.name} is already one of {self.name}'s pets.")
        self.pets.append(pet)

    def get_pet(self, name: str) -> Optional[Pet]:
        """Return the pet with this name (case-insensitive), or None."""
        for pet in self.pets:
            if pet.name.lower() == name.lower():
                return pet
        return None

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.get_tasks()]

    # --- persistence -------------------------------------------------

    def to_dict(self) -> dict:
        """Return a JSON-friendly dictionary of the owner, pets and tasks."""
        return {"name": self.name, "pets": [pet.to_dict() for pet in self.pets]}

    @classmethod
    def from_dict(cls, data: dict) -> "Owner":
        """Rebuild an Owner from a dictionary created by to_dict()."""
        owner = cls(data["name"])
        for pet_data in data.get("pets", []):
            owner.add_pet(Pet.from_dict(pet_data))
        return owner

    def save_to_json(self, path: str = "data.json") -> None:
        """Write the owner, pets and tasks to a JSON file."""
        Path(path).write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load_from_json(cls, path: str = "data.json") -> "Owner":
        """Load an owner from a JSON file (raises FileNotFoundError if missing)."""
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.from_dict(data)

    @classmethod
    def load_or_create(cls, name: str, path: str = "data.json") -> "Owner":
        """Load saved data if the file exists and is valid, else start fresh."""
        try:
            return cls.load_from_json(path)
        except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError):
            return cls(name)


# ----------------------------------------------------------------------
# Scheduler
# ----------------------------------------------------------------------

@dataclass
class PlanItem:
    """One entry in a time-blocked daily plan."""

    task: Task
    start: Optional[str]  # None if there was no room left in the day
    end: Optional[str]
    moved: bool = False  # True if the scheduler had to shift it from its requested time


class Scheduler:
    """The brain that organizes tasks across all of an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        """Create a scheduler for the given owner."""
        self.owner: Owner = owner

    # --- basic organizing --------------------------------------------

    def get_todays_schedule(self) -> list[Task]:
        """Return today's tasks sorted by time."""
        today = date.today()
        todays = [t for t in self.owner.get_all_tasks() if t.due_date == today]
        return self.sort_by_time(todays)

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted by time of day (handles '9:00' and '09:00')."""
        return sorted(tasks, key=lambda task: task.start_minutes)

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks with high priority first, then earliest time."""
        return sorted(
            tasks, key=lambda t: (PRIORITY_ORDER[t.priority], t.start_minutes)
        )

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> list[Task]:
        """Return tasks filtered by pet name and/or completion status."""
        tasks = self.owner.get_all_tasks()
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet_name == pet_name]
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        return tasks

    # --- conflict detection ------------------------------------------

    def detect_conflicts(self) -> list[str]:
        """Return a warning for every pair of incomplete tasks that overlap.

        Two tasks overlap if they are on the same date and their time blocks
        (start to start + duration) intersect. A task that starts exactly when
        another one ends is NOT a conflict.
        """
        by_day: dict[date, list[Task]] = {}
        for task in self.owner.get_all_tasks():
            if not task.completed:
                by_day.setdefault(task.due_date, []).append(task)

        warnings = []
        for day in sorted(by_day):
            tasks = self.sort_by_time(by_day[day])
            for i, first in enumerate(tasks):
                for second in tasks[i + 1:]:
                    if second.start_minutes >= first.start_minutes + first.duration_minutes:
                        break  # sorted by start, so nothing later can overlap `first`
                    warnings.append(
                        f"Conflict on {day}: {first.pet_name}: {first.description} "
                        f"({first.time}-{first.end_time}) overlaps "
                        f"{second.pet_name}: {second.description} "
                        f"({second.time}-{second.end_time})"
                    )
        return warnings

    # --- time blocking -----------------------------------------------

    @staticmethod
    def _first_gap(
        busy: list[tuple[int, int]], duration: int, earliest: int, latest: int
    ) -> Optional[int]:
        """Return the first start minute where `duration` fits, or None."""
        candidate = earliest
        for start, end in sorted(busy):
            if candidate + duration <= start:
                break
            candidate = max(candidate, end)
        if candidate + duration <= latest:
            return candidate
        return None

    @staticmethod
    def _is_free(busy: list[tuple[int, int]], start: int, end: int) -> bool:
        """Return True if [start, end) overlaps none of the busy blocks."""
        return all(end <= b_start or start >= b_end for b_start, b_end in busy)

    def _busy_blocks(self, day: date) -> list[tuple[int, int]]:
        """Return (start, end) minute blocks of incomplete tasks on a day."""
        return [
            (t.start_minutes, t.start_minutes + t.duration_minutes)
            for t in self.owner.get_all_tasks()
            if t.due_date == day and not t.completed
        ]

    def find_next_available_slot(
        self,
        duration_minutes: int,
        day: Optional[date] = None,
        earliest: str = "08:00",
        latest: str = "20:00",
    ) -> Optional[str]:
        """Return the first 'HH:MM' where a task of this length fits, or None.

        Looks at the tasks of ALL pets, because one owner cannot be in two
        places at once.
        """
        day = day or date.today()
        slot = self._first_gap(
            self._busy_blocks(day), duration_minutes,
            to_minutes(earliest), to_minutes(latest),
        )
        return None if slot is None else to_hhmm(slot)

    def build_daily_plan(
        self,
        day: Optional[date] = None,
        earliest: str = "08:00",
        latest: str = "20:00",
    ) -> list[PlanItem]:
        """Build a plan with no overlaps, placing high-priority tasks first.

        Each task keeps its requested time if that block is free. Otherwise it
        is moved to the next free gap after its requested time. Tasks that
        cannot fit before `latest` are returned with start=None.
        """
        day = day or date.today()
        todays = [
            t for t in self.owner.get_all_tasks()
            if t.due_date == day and not t.completed
        ]
        busy: list[tuple[int, int]] = []
        placed: list[PlanItem] = []
        unplaced: list[PlanItem] = []
        latest_min = to_minutes(latest)

        for task in self.sort_by_priority(todays):
            wanted = task.start_minutes
            length = task.duration_minutes
            # First gap at or after the requested time that ends by `latest`.
            slot = self._first_gap(busy, length, wanted, latest_min)
            # A task requested outside the window still keeps its time if free.
            if slot is None and self._is_free(busy, wanted, wanted + length):
                slot = wanted
            if slot is None:
                unplaced.append(PlanItem(task, None, None))
                continue
            busy.append((slot, slot + length))
            placed.append(
                PlanItem(task, to_hhmm(slot), to_hhmm(slot + length), moved=slot != wanted)
            )

        placed.sort(key=lambda item: to_minutes(item.start))
        return placed + unplaced
        return conflicts
