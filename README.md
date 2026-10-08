# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
Today's Schedule
----------------
08:00 - Bella: Walk Bella
12:00 - Milo: Feed Milo
18:00 - Bella: Feed Bella

Bella's Tasks
-------------
18:00 - Feed Bella
08:00 - Walk Bella

Incomplete Tasks
----------------
18:00 - Bella: Feed Bella
08:00 - Bella: Walk Bella
12:00 - Milo: Feed Milo

Recurring Task Test
-------------------
Original date: 2026-10-07
Next occurrence: 2026-10-08

Task Conflicts
--------------
Conflict: Bella and Milo both have tasks at 12:00.

## 🧪 Testing PawPal+

PawPal+ uses automated tests with pytest to make sure the main scheduling features work correctly.

Run Tests

Use the following command in the terminal:

python -m pytest
What the Tests Cover

The test suite checks several core behaviors of PawPal+:

Task completion: Verifies that tasks can be marked as completed.
Task addition: Verifies that tasks can be added to a pet.
Sorting: Checks that tasks are organized in chronological order.
Recurring tasks: Verifies that daily and weekly tasks create the correct next occurrence.
Filtering: Checks that tasks can be filtered by pet.
Conflict detection: Checks that scheduling conflicts are identified when tasks have the same time.
Sample test output:

# Run the full test suite:
python -m pytest

# Run with coverage:
python -m pytest --cov
```
# Paste your pytest output here
```
============================= test session starts =============================
collected 5 items

tests/test_pawpal.py .....                                             [100%]

============================== 5 passed in 0.XXs ===============================

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature            | Method(s)                            | Notes                                                                             |
| ------------------ | ------------------------------------ | --------------------------------------------------------------------------------- |
| Task sorting       | `Scheduler.sort_by_time()`           | Sorts tasks chronologically using their `HH:MM` time.                             |
| Daily schedule     | `Scheduler.get_todays_schedule()`    | Finds tasks due today and sorts them by time.                                     |
| Filtering          | `Scheduler.filter_tasks()`           | Filters tasks by pet name and/or completion status.                               |
| Conflict handling  | `Scheduler.detect_conflicts()`       | Detects multiple tasks scheduled at the exact same time and displays a warning.   |
| Recurring tasks    | `Task.mark_complete()`               | Creates a new task for the next occurrence of a daily or weekly task.             |
| Task completion    | `Task.mark_complete()`               | Changes the task's `completed` status to `True`.                                  |
| Pet management     | `Owner.add_pet()` / `Pet.add_task()` | Connects pets and their assigned care tasks.                                      |
| Application memory | `st.session_state`                   | Keeps the owner, pets, and tasks available when Streamlit reruns the application. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1Open PawPal+
The Streamlit application opens with the PawPal+ dashboard and allows the owner to manage their pets and care tasks.
Add a pet
Enter the pet's name and species, then select Add Pet. The new Pet object is stored in the owner's pet list.
Schedule a task
Select a pet and enter a task description, time, and frequency. PawPal+ creates a Task object and assigns it to the selected pet.
View the daily schedule
The application displays the pet's tasks for the current day in chronological order, making it easier for the owner to follow their care routine.
Check scheduling conflicts
PawPal+ compares task times and displays a warning when multiple tasks are scheduled at the same time.
Manage recurring tasks
When a daily or weekly task is completed, PawPal+ creates a new task for its next scheduled occurrence.
Review filtered tasks
The scheduler can filter tasks by pet or completion status, allowing the owner to quickly find specific tasks.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
