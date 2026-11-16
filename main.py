
from pathlib import Path

from formatting import format_plan, format_schedule, header
from pawpal_system import Owner, Pet, Scheduler, Task

DEMO_FILE = "demo_data.json"


def build_demo_owner() -> Owner:
    """Create an owner with two pets and several tasks (all due today)."""
    owner = Owner("Naviyah")
    bella = Pet("Bella", "Dog")
    milo = Pet("Milo", "Cat")
    owner.add_pet(bella)
    owner.add_pet(milo)

    bella.add_task(Task("Walk Bella", "08:00", duration_minutes=30, priority="high"))
    bella.add_task(Task("Give Bella medicine", "09:00", frequency="daily",
                        duration_minutes=10, priority="high"))
    bella.add_task(Task("Brush Bella", "12:00", duration_minutes=20, priority="low"))
    bella.add_task(Task("Feed Bella", "18:00", duration_minutes=15, priority="high"))

    milo.add_task(Task("Play with Milo", "08:15", duration_minutes=20, priority="low"))
    milo.add_task(Task("Feed Milo", "12:00", duration_minutes=10, priority="medium"))
    milo.add_task(Task("Clean litter box", "18:00", duration_minutes=15, priority="medium"))
    return owner


def main() -> None:
    owner = build_demo_owner()
    bella = owner.get_pet("Bella")
    scheduler = Scheduler(owner)

    print(f"🐾 PawPal+ demo for {owner.name} "
          f"({', '.join(f'{p.name} the {p.species}' for p in owner.pets)})")

    print(header("1. Today's schedule (sorted by time, all pets)"))
    print(format_schedule(scheduler.get_todays_schedule()))

    print(header("2. Sorted by priority (high first, then time)"))
    print(format_schedule(scheduler.sort_by_priority(owner.get_all_tasks())))

    print(header("3. Filtering"))
    print("Bella's tasks:")
    print(format_schedule(scheduler.filter_tasks(pet_name="Bella")))

    print(header("4. Recurring task"))
    medicine = next(t for t in bella.tasks if t.description == "Give Bella medicine")
    next_task = bella.complete_task(medicine)  # next occurrence is added automatically
    print(f"Completed '{medicine.description}' dated {medicine.due_date}")
    print(f"Next occurrence automatically scheduled for {next_task.due_date}")
    print(f"Incomplete tasks remaining: {len(scheduler.filter_tasks(completed=False))}")

    print(header("5. Conflict detection (overlapping time blocks)"))
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for conflict in conflicts:
            print(f"⚠️  {conflict}")
    else:
        print("✅ No conflicts detected.")

    print(header("6. Time-blocked daily plan (incomplete tasks, no overlaps, high priority first)"))
    print(format_plan(scheduler.build_daily_plan()))

    print(header("7. Next available slot"))
    for minutes in (15, 60, 240):
        slot = scheduler.find_next_available_slot(minutes)
        shown = slot if slot else "none available between 08:00 and 20:00"
        print(f"A {minutes}-minute task fits at: {shown}")

    print(header("8. Persistence (JSON save and load)"))
    owner.save_to_json(DEMO_FILE)
    reloaded = Owner.load_from_json(DEMO_FILE)
    print(f"Saved to {DEMO_FILE} ({Path(DEMO_FILE).stat().st_size} bytes)")
    print(f"Reloaded {len(reloaded.pets)} pets and "
          f"{len(reloaded.get_all_tasks())} tasks "
          f"(original had {len(owner.get_all_tasks())} tasks)")
    print(f"Same data after reload: {reloaded.to_dict() == owner.to_dict()}")


if __name__ == "__main__":
    main()
