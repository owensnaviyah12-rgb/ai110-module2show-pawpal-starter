from datetime import date, timedelta

import pytest

from formatting import format_plan, format_schedule, status_icon
from pawpal_system import Owner, Pet, Scheduler, Task


def make_scheduler():
    owner = Owner("Sam")
    bella, milo = Pet("Bella", "Dog"), Pet("Milo", "Cat")
    owner.add_pet(bella)
    owner.add_pet(milo)
    return Scheduler(owner), bella, milo


# ---------------------------------------------------------------- Task / Pet / Owner

def test_task_completion():
    task = Task("Feed Bella", "08:00")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_task_addition():
    pet = Pet("Bella", "Dog")
    task = Task("Feed Bella", "08:00")
    assert len(pet.tasks) == 0
    pet.add_task(task)
    assert len(pet.tasks) == 1
    assert task.pet_name == "Bella"


def test_remove_task():
    pet = Pet("Bella", "Dog")
    task = Task("Feed Bella", "08:00")
    pet.add_task(task)
    pet.remove_task(task)
    assert pet.get_tasks() == []


def test_owner_collects_tasks_from_all_pets():
    s, bella, milo = make_scheduler()
    bella.add_task(Task("Walk", "08:00"))
    milo.add_task(Task("Feed", "09:00"))
    assert len(s.owner.get_all_tasks()) == 2


def test_duplicate_pet_name_rejected():
    owner = Owner("Sam")
    owner.add_pet(Pet("Bella", "Dog"))
    with pytest.raises(ValueError):
        owner.add_pet(Pet("bella", "Cat"))


def test_invalid_task_inputs_rejected():
    with pytest.raises(ValueError):
        Task("Bad time", "25:99")
    with pytest.raises(ValueError):
        Task("Bad time", "noon")
    with pytest.raises(ValueError):
        Task("Bad priority", "08:00", priority="urgent")
    with pytest.raises(ValueError):
        Task("Bad duration", "08:00", duration_minutes=0)
    with pytest.raises(ValueError):
        Task("Runs past midnight", "23:45", duration_minutes=30)


# ---------------------------------------------------------------- sorting

def test_sort_by_time_orders_across_pets():
    s, bella, milo = make_scheduler()
    bella.add_task(Task("Dinner", "18:00"))
    milo.add_task(Task("Walk", "08:00"))
    assert [t.time for t in s.get_todays_schedule()] == ["08:00", "18:00"]


def test_sort_handles_unpadded_times():
    s, _, _ = make_scheduler()
    tasks = [Task("a", "10:00"), Task("b", "9:00")]
    assert [t.time for t in s.sort_by_time(tasks)] == ["9:00", "10:00"]


def test_sort_by_priority_high_first_then_time():
    s, bella, milo = make_scheduler()
    bella.add_task(Task("low early", "07:00", priority="low"))
    bella.add_task(Task("high late", "20:00", priority="high"))
    milo.add_task(Task("high early", "09:00", priority="high"))
    milo.add_task(Task("medium", "08:00", priority="medium"))
    ordered = [t.description for t in s.sort_by_priority(s.owner.get_all_tasks())]
    assert ordered == ["high early", "high late", "medium", "low early"]


# ---------------------------------------------------------------- filtering

def test_filter_by_pet_and_completion():
    s, bella, milo = make_scheduler()
    done = Task("Feed", "08:00")
    bella.add_task(done)
    milo.add_task(Task("Feed", "09:00"))
    done.mark_complete()
    assert [t.pet_name for t in s.filter_tasks(pet_name="Bella")] == ["Bella"]
    assert len(s.filter_tasks(completed=False)) == 1
    assert len(s.filter_tasks(pet_name="Bella", completed=False)) == 0


# ---------------------------------------------------------------- recurring tasks

def test_daily_recurrence_creates_next_day():
    task = Task("Meds", "09:00", frequency="daily")
    nxt = task.mark_complete()
    assert nxt.due_date == task.due_date + timedelta(days=1)
    assert nxt.completed is False


def test_weekly_recurrence_creates_next_week():
    task = Task("Groom", "10:00", frequency="weekly")
    nxt = task.mark_complete()
    assert nxt.due_date == task.due_date + timedelta(weeks=1)


def test_one_time_task_does_not_recur():
    assert Task("Vet visit", "10:00").mark_complete() is None


def test_complete_task_adds_next_occurrence_to_pet():
    pet = Pet("Bella", "Dog")
    task = Task("Meds", "09:00", frequency="daily", priority="high", duration_minutes=10)
    pet.add_task(task)
    nxt = pet.complete_task(task)
    assert len(pet.tasks) == 2
    assert nxt.priority == "high" and nxt.duration_minutes == 10
    assert nxt.pet_name == "Bella"


# ---------------------------------------------------------------- conflicts

def test_conflict_detected_for_same_time_across_pets():
    s, bella, milo = make_scheduler()
    bella.add_task(Task("Meds", "12:00"))
    milo.add_task(Task("Meds", "12:00"))
    assert len(s.detect_conflicts()) == 1


def test_overlapping_blocks_conflict_even_with_different_start_times():
    s, bella, milo = make_scheduler()
    bella.add_task(Task("Walk", "08:00", duration_minutes=30))
    milo.add_task(Task("Play", "08:15", duration_minutes=20))
    assert len(s.detect_conflicts()) == 1


def test_back_to_back_tasks_are_not_a_conflict():
    s, bella, milo = make_scheduler()
    bella.add_task(Task("Walk", "08:00", duration_minutes=30))
    milo.add_task(Task("Feed", "08:30", duration_minutes=10))
    assert s.detect_conflicts() == []


def test_no_conflict_on_different_days():
    s, bella, _ = make_scheduler()
    bella.add_task(Task("Walk", "08:00"))
    tomorrow = Task("Walk", "08:00")
    tomorrow.due_date += timedelta(days=1)
    bella.add_task(tomorrow)
    assert s.detect_conflicts() == []


def test_completed_tasks_do_not_conflict():
    s, bella, milo = make_scheduler()
    first = Task("Meds", "12:00")
    bella.add_task(first)
    milo.add_task(Task("Meds", "12:00"))
    first.mark_complete()
    assert s.detect_conflicts() == []


# ---------------------------------------------------------------- next slot / plan

def test_next_available_slot_skips_busy_blocks_across_pets():
    s, bella, milo = make_scheduler()
    bella.add_task(Task("Walk", "08:00", duration_minutes=60))
    milo.add_task(Task("Feed", "09:00", duration_minutes=30))
    assert s.find_next_available_slot(15) == "09:30"


def test_next_available_slot_uses_a_gap_when_it_fits():
    s, bella, milo = make_scheduler()
    bella.add_task(Task("Walk", "08:00", duration_minutes=30))
    milo.add_task(Task("Feed", "10:00", duration_minutes=30))
    assert s.find_next_available_slot(60) == "08:30"
    assert s.find_next_available_slot(120) == "10:30"


def test_next_available_slot_returns_none_when_day_is_full():
    s, bella, _ = make_scheduler()
    bella.add_task(Task("All day", "08:00", duration_minutes=720))
    assert s.find_next_available_slot(30) is None


def test_daily_plan_has_no_overlaps_and_moves_lower_priority():
    s, bella, milo = make_scheduler()
    bella.add_task(Task("High", "12:00", duration_minutes=30, priority="high"))
    milo.add_task(Task("Low", "12:00", duration_minutes=30, priority="low"))
    plan = s.build_daily_plan()
    by_name = {item.task.description: item for item in plan}
    assert by_name["High"].start == "12:00" and not by_name["High"].moved
    assert by_name["Low"].start == "12:30" and by_name["Low"].moved
    blocks = sorted((i.start, i.end) for i in plan)
    assert all(blocks[i][1] <= blocks[i + 1][0] for i in range(len(blocks) - 1))


def test_daily_plan_reports_tasks_that_do_not_fit():
    s, bella, milo = make_scheduler()
    bella.add_task(Task("Huge", "08:00", duration_minutes=720, priority="high"))
    milo.add_task(Task("Squeezed out", "09:00", duration_minutes=30, priority="low"))
    plan = {item.task.description: item for item in s.build_daily_plan()}
    assert plan["Squeezed out"].start is None


# ---------------------------------------------------------------- persistence

def test_save_and_load_round_trip(tmp_path):
    owner = Owner("Sam")
    bella = Pet("Bella", "Dog")
    owner.add_pet(bella)
    bella.add_task(Task("Meds", "09:00", frequency="daily", priority="high",
                        duration_minutes=10, due_date=date(2030, 1, 2)))
    done = Task("Walk", "08:00")
    bella.add_task(done)
    done.mark_complete()

    path = tmp_path / "data.json"
    owner.save_to_json(str(path))
    loaded = Owner.load_from_json(str(path))

    assert loaded.to_dict() == owner.to_dict()
    assert loaded.get_pet("Bella").tasks[0].due_date == date(2030, 1, 2)
    assert loaded.get_pet("Bella").tasks[1].completed is True


def test_load_or_create_handles_missing_and_corrupt_files(tmp_path):
    missing = Owner.load_or_create("Sam", str(tmp_path / "nope.json"))
    assert missing.name == "Sam" and missing.pets == []

    corrupt = tmp_path / "bad.json"
    corrupt.write_text("{not json", encoding="utf-8")
    assert Owner.load_or_create("Sam", str(corrupt)).pets == []


# ---------------------------------------------------------------- formatting

def test_status_icon():
    assert status_icon(True) == "✅"
    assert status_icon(False) == "⬜"


def test_format_schedule_and_plan_include_task_details():
    s, bella, _ = make_scheduler()
    bella.add_task(Task("Walk Bella", "08:00", priority="high"))
    assert "Walk Bella" in format_schedule(s.owner.get_all_tasks())
    assert "08:00" in format_plan(s.build_daily_plan())
    assert format_schedule([]) == "(no tasks)"
