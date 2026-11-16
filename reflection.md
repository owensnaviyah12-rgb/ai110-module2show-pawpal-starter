# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My initial UML design included four main classes: Owner, Pet, Task, and Scheduler. The Owner class manages the user's pets, while the Pet class stores information about each pet and its tasks. The Task class represents individual care activities, including the description, time, frequency, due date, and completion status. The Scheduler manages the tasks by sorting, filtering, finding today's schedule, and detecting conflicts.

The final UML (`diagrams/uml.mmd`, Mermaid source) keeps those four classes and adds a small `PlanItem` class that holds one slot of a daily plan. It shows Owner → Pet(s), Pet → Task(s), Scheduler → Owner, and I checked that every attribute and method in it exists in `pawpal_system.py`.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

The design changed during implementation. I added the pet_name attribute to the Task class so that tasks could be connected to the correct pet when displayed or filtered. I also added recurring-task logic to mark_complete() so daily and weekly tasks can create a new task for their next occurrence.

Later changes came from fixing problems I found when reviewing my own code:

- `Pet.complete_task()` now adds the next recurring task automatically. Before, `mark_complete()` returned the new task but nothing stored it, so the owner had to add it by hand.
- Tasks gained `duration_minutes` and `priority`. Conflicts used to mean "same start time", which misses a 08:00-08:30 walk overlapping an 08:15 play session, so conflicts are now based on time blocks. Durations also made the next-available-slot and daily-plan features possible.
- Tasks, pets and owners validate their input (bad times, unknown priority, duplicate pet names, tasks running past midnight) and can save/load themselves as JSON.
- Output formatting lives in a separate `formatting.py` so the system classes stay free of print code.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers task time, duration, priority, due date, pet, completion status, and task frequency. Time is still the most important constraint because the main purpose of PawPal+ is to help owners organize their pet-care activities in the correct order. Priority decides who wins when two tasks want the same time (medicine and feeding should beat grooming). Due dates and recurring schedules determine when tasks appear.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

My first version only detected conflicts and left the decision to the owner. The daily plan now decides for them: it is greedy, placing high-priority tasks first and shifting lower-priority tasks to the next free gap. The tradeoff is that this is simple and predictable but not optimal: it can move more tasks than a smarter arrangement would, and it never splits or reorders a task around the owner's own preferences. That is reasonable for a daily pet-care plan because the rules are easy to explain ("important things keep their time"), and the plain conflict warnings are still shown so the owner can override the suggestion.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI throughout the project to help brainstorm system designs, understand how the classes should work together, develop scheduling algorithms, debug errors, and improve the readability of my code. The most helpful prompts were specific questions about how to implement individual requirements and how to test whether each feature worked correctly.

In the final stage I gave an AI assistant the assignment rubric and my repository and asked it to grade the project. It found real bugs: conflicts ignored dates, times were sorted as text so `9:00` came after `10:00`, the README claimed tests that did not exist, and the UML file was still the unedited template. I then asked it to fix everything and add the stretch features. The prompts that worked best included the rubric and my actual files. A short prompt like "give me the code" was too vague on its own. The full comparison is in `ai_interactions.md`.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

One suggestion I did not keep was the first conflict fix. It grouped tasks by exact start time and added the date check, which fixed the original bug, but once tasks had durations it was too narrow: a walk from 08:00 to 08:30 and a play session at 08:15 would not have been flagged. It was replaced with an overlap check on time blocks, and I added tests for overlapping blocks, back-to-back tasks (not a conflict), different days, and completed tasks.

I also did not accept the README at face value. It listed six tested behaviors and showed an unfinished placeholder instead of a real test result, but the test file only had two tests. I replaced it with the real output of `python -m pytest`.

To verify correctness, I compared the code against each rubric line, ran the 28 pytest tests, ran `python main.py` and pasted its real output into the README, and checked that every attribute and method in the UML exists in the code. One limit: the AI's environment did not have Streamlit installed, so `app.py` was only run with a stand-in module that executes it top to bottom, including simulated button clicks. Launching it for real with `python -m streamlit run app.py` is still something I need to do myself.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

The 28 tests cover task completion, adding and removing tasks, input validation, sorting by time and by priority (including unpadded times), filtering by pet and completion, daily and weekly recurring tasks, conflict detection (same start, overlapping blocks, back-to-back, different days, completed tasks), the next available slot, the time-blocked daily plan, JSON save/load (including missing and corrupt files), and the output formatting helpers. These tests matter because they cover every scheduling feature, and the edge cases are exactly the ones that were wrong before (dates, text sorting, overlaps).

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I am confident that the scheduling features work correctly because every one is tested and the tests pass, and I would rate my confidence as 4 out of 5 stars. The missing star is the Streamlit UI, which has not been tested in a real browser. With more time I would test tasks added for past or future dates, a daily plan with many tasks competing for a very full day, a corrupt or hand-edited `data.json`, and recurring tasks that are completed several times in a row.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am most satisfied with how the different classes work together to create a complete scheduling system. The Owner, Pet, Task, and Scheduler classes each have separate responsibilities, which makes the code easier to understand and modify, and that made it easy to add priorities, a daily plan, and JSON persistence later without rewriting anything. I also connected the system to Streamlit so users can add pets and schedule tasks through the interface.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

If I had another iteration, I would let users edit and delete tasks and pets in the Streamlit app, add real multi-day planning instead of only today, and support time zones and tasks that cross midnight. I would also try a smarter planner that moves the fewest tasks instead of the simple greedy approach.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

One important thing I learned is that designing a system before coding makes implementation easier because each class has a clear responsibility. I also learned that AI is most useful when I give it the real requirements and my real files, and that its output has to be checked: running the tests and the demo caught problems that reading the code did not, and the README and UML had drifted away from what the code actually did until I compared them line by line.
