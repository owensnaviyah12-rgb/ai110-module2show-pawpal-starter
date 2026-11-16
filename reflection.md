# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My initial UML design included four main classes: Owner, Pet, Task, and Scheduler. The Owner class manages the user's pets, while the Pet class stores information about each pet and its tasks. The Task class represents individual care activities, including the description, time, frequency, due date, and completion status. The Scheduler manages the tasks by sorting, filtering, finding today's schedule, and detecting conflicts.The final UML (diagrams/uml.mmd, Mermaid source) keeps those four classes and adds a small PlanItem class that holds one slot of a daily plan. It shows Owner → Pet(s), Pet → Task(s), Scheduler → Owner, and I checked that every attribute and method in it exists in pawpal_system.py.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

The design changed during implementation. I added the pet_name attribute to the Task class so that tasks could be connected to the correct pet when displayed or filtered. I also added recurring-task logic to mark_complete() so daily and weekly tasks can create a new task for their next occurrence.
Later changes came from fixing problems I found when reviewing my own code:

Pet.complete_task() now adds the next recurring task automatically. Before, mark_complete() returned the new task but nothing stored it, so the owner had to add it by hand.Tasks gained duration_minutes and priority. Conflicts used to mean "same start time", which misses a 08:00-08:30 walk overlapping an 08:15 play session, so conflicts are now based on time blocks. Durations also made the next-available-slot and daily-plan features possible.Tasks, pets and owners validate their input (bad times, unknown priority, duplicate pet names, tasks running past midnight) and can save/load themselves as JSON.
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

I used AI throughout the project to help brainstorm system designs, understand how the classes should work together, develop scheduling algorithms, debug errors, and improve the readability of my code. I also used AI to help create ideas for sorting tasks by time, filtering tasks by pet and completion status, detecting scheduling conflicts, and handling recurring tasks. The most helpful prompts were specific questions about how to implement individual requirements and how to test whether each feature worked correctly.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

I did not accept every AI suggestion without checking it. When working on the project, I compared suggested code with the assignment requirements and tested the implementation using pytest. I also checked that the methods matched the actual classes in pawpal_system.py. This helped me catch issues and make sure the final code actually worked instead of assuming the AI-generated code was automatically correct.
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested task completion, adding tasks to pets, sorting tasks by time, daily and weekly recurring tasks, filtering tasks by pet, and scheduling conflicts. These tests were important because they cover the main behaviors of the PawPal+ scheduling system. Testing each feature separately helped make sure that changes to one part of the system did not break another part.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I am confident that the main scheduling features work correctly because I tested the core behaviors using automated tests and verified that the tests passed. I would rate my confidence as 4 out of 5 stars. If I had more time, I would test edge cases such as multiple tasks with the same time, empty task lists, invalid time formats, duplicate pet names, and recurring tasks that are completed multiple times.
---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am most satisfied with how the different classes work together to create a complete scheduling system. The Owner, Pet, Task, and Scheduler classes each have separate responsibilities, which makes the code easier to understand and modify. I also successfully connected the system to Streamlit so users can add pets and schedule tasks through the interface.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

If I had another iteration, I would improve the Streamlit interface by adding buttons that allow users to mark tasks as completed directly from the app. I would also improve recurring-task handling so that the next occurrence is automatically added to the pet's schedule instead of requiring it to be added separately. Finally, I would add stronger input validation for task times and duplicate pet names.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

One important thing I learned is that designing a system before coding makes implementation easier because each class has a clear responsibility. I also learned that AI is most useful when I use it as a tool for brainstorming, explaining concepts, and debugging rather than simply copying its suggestions. Testing the code myself helped me understand why the solution worked and gave me more confidence in the final system.
