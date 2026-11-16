# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

Using an AI agent such as Claude taught me how to write better prompts. Before I ask for anything, I work out what I am trying to do and what I need from the answer. Once I know that, I write a request tailored to those needs and give Claude the real material, such as the rubric and my files. After Claude responds, I check the result by hand to make sure it understood my project correctly and that the information is accurate.

**Agent / tool:** Claude (Claude app with file and shell tools), used in agent mode to make multi-step changes and run code.

**What task did you give the agent?**

I gave it the full project rubric and my repository and worked in three steps:

1. "grade my project" against the rubric.
2. "give me the code" (the fixes).
3. "make sure all the files match for rubric. Extra point should be included as well", which meant all five stretch features. For this Agent Mode stretch I asked for a third algorithmic capability beyond the basic requirements, and the agent built "next available slot" and a priority-based daily plan.

After that I attached my updated files and asked it to grade them again. Each round found something new to fix: the README did not match the starter's format, the UML was still the template, and this log was incomplete.

**Files modified or created:**

| File | Change |
| --- | --- |
| `pawpal_system.py` | Added `duration_minutes` and `priority` to `Task`, input validation, `Pet.complete_task()`, `Pet.remove_task()`, `Owner.get_pet()`, a duplicate pet-name check, JSON save/load, `PlanItem`, and the Scheduler features `sort_by_priority()`, overlap-based `detect_conflicts()`, `find_next_available_slot()` and `build_daily_plan()`. Fixed time sorting (text to minutes). |
| `formatting.py` (new) | Emoji badges, ANSI colors and box-drawn tables. |
| `main.py` | Rewritten as an 8-step demo of every feature, using the formatting module. |
| `app.py` | Priority, duration, "Done" buttons, daily plan, free-slot finder, filters, and automatic load/save to `data.json`. |
| `tests/test_pawpal.py` | Grew from 2 tests to 28. |
| `diagrams/uml.mmd` | Replaced the unedited template with the real class diagram. |
| `README.md` | Rewritten in the starter's section format, with real pasted output. |
| `reflection.md` | Rewritten to match the final code, with concrete accepted/rejected examples. |
| `ai_interactions.md` | This file. |
| `pytest.ini`, `requirements.txt`, `.gitignore` (new/updated) | `python -m pytest` and plain `pytest` both work; dependencies listed; runtime JSON files ignored. |

**What did the agent do?**

1. Read the repo and graded it against the rubric. It found four bugs (conflicts ignoring dates, `9:00` sorting after `10:00`, recurring tasks not stored, same-pet "Bella and Bella" conflict messages) and that the UML was an unedited template.
2. Rebuilt the classes in a sandbox and ran them to confirm those bugs before changing anything.
3. Wrote the fixed system, the stretch features, the demo, the app and the tests.
4. Ran `python -m pytest` (28 passed) and `python main.py`, and pasted that real output into the README.
5. Ran `app.py` with a stand-in `streamlit` module (Streamlit was not installed in its environment), once with empty data and once with seeded data while simulating every button click, to make sure it runs without errors.
6. Checked the UML against the code and scanned the docs for leftover template text.
7. Rebuilt the README in the starter's section order after I pointed out the format did not match.
8. Graded my updated files by running them together: 28 tests passed and the README output matched a fresh run of `main.py`.

**What did you have to verify or fix manually?**

Corrections that were needed during the work:

- The first draft of `build_daily_plan()` had a leftover no-op condition and a confusing limit. It was rewritten with a clear rule (try the first gap at or after the requested time that ends by the window end; a free task outside the window keeps its time) and a helper `_is_free()`.
- The first table output was misaligned on the "moved from" column because the `↪` arrow was counted as a wide character. `_visible_len()` now uses `unicodedata.east_asian_width`, and `⚠️` inside tables was swapped for `❌` because its width varies between terminals.
- A first conflict fix (group by exact start time) was replaced by overlap-based detection once tasks had durations, with new tests for overlapping blocks and back-to-back tasks.
- The original README listed tests that did not exist and had placeholder test output. Both were replaced with real output, and the README was later rebuilt to match the starter's format.
- While regrading, a leftover `return conflicts` line was found after the real `return` at the end of `build_daily_plan()`. It never ran, but I deleted it.

**The logic behind the code (so I can explain it myself)**

- **Times become minutes.** `"09:00"` is converted to minutes after midnight (540) before any comparison. Comparing the text directly was the original bug: `"9:00"` sorts after `"10:00"` because `"9"` is greater than `"1"`.
- **A conflict is an overlap, not an identical time.** Each task is a block from `start` to `start + duration`. Two blocks overlap when `A.start < B.end and B.start < A.end`. Because the comparison is strict, a task starting at 08:30 right after one ending at 08:30 is *not* a conflict. Conflicts only count for the same date and for incomplete tasks.
- **Next available slot.** Collect the busy blocks of all pets for the day, sort them, and sweep a "candidate start" forward: if the new task fits before the next busy block, that is the answer; otherwise jump the candidate to the end of that block. If nothing fits before 20:00, return `None`.
- **Daily plan.** Sort tasks by priority (high first, then time). Each one keeps its requested time if that block is free; otherwise it moves to the first free gap after its requested time. This is greedy, so it is simple to explain but not guaranteed to move the fewest tasks.
- **Recurring tasks.** Completing a daily or weekly task creates a copy dated one day or one week later with the same time, duration and priority. `Pet.complete_task()` stores that copy so it isn't lost.
- **Persistence.** Every class converts itself to a dictionary (`to_dict`) and back (`from_dict`), with dates saved as ISO text. `load_or_create()` falls back to an empty owner if the file is missing or corrupt, so the app never crashes on a bad `data.json`.

**Using pytest to prove the code runs**

- `python -m pytest -v` runs all 28 tests and shows each name. All should say `PASSED`.
- `python -m pytest -k conflict -v` runs only the conflict tests. `python -m pytest tests/test_pawpal.py::test_back_to_back_tasks_are_not_a_conflict -v` runs one test.
- **Check that the tests can actually fail.** In `detect_conflicts()`, change `>=` to `>` in the line `if second.start_minutes >= first.start_minutes + first.duration_minutes:` and re-run pytest. On the agent's copy this made exactly one test fail (`test_back_to_back_tasks_are_not_a_conflict`) and the other 27 pass, which shows that test is protecting the overlap rule. Change it back afterwards and confirm 28 pass again.

**If something confuses me or breaks (what to do, in order)**

1. Run only the failing test with `python -m pytest <path>::<test_name> -v --tb=short` and read the last few lines: they show the expected value and the actual value.
2. Add a `print()` of the values involved, or run the small example in a Python shell, so I can see what the code really does.
3. `ModuleNotFoundError: pawpal_system`: I am in the wrong folder. Run commands from the project root, using `python -m pytest`.
4. Streamlit won't start: run `pip install -r requirements.txt` and use `python -m streamlit run app.py`. If the app shows strange data, delete `data.json` and restart.
5. Still stuck: ask the agent with the exact error text, the file name, and what I expected to happen. That gets a far better answer than a short "it doesn't work".

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

Task: get my PawPal+ project to a state that matches the rubric.

| | Option A | Option B |
| --- | --- | --- |
| **Model / tool used** | Claude (Claude app, file and shell tools) | Claude (same model and tools) |
| **Prompt** | "grade my project ... here the repo link", followed by the full rubric text | "give me the code" (four words, sent right after the grade) |
| **Response summary** | Read the README, `pawpal_system.py`, `main.py` and `reflection.md` from GitHub and scored each rubric line. Asked me for the files it could not open. | Interpreted it as "the fixes": returned corrected `pawpal_system.py`, `main.py`, a test file and a UML, and ran the tests before handing them over. |
| **What was useful** | A line-by-line score tied to the rubric, plus concrete bugs (dates in conflicts, text sorting, missing tests, README placeholder output). It was honest about what it could not verify. | Working, tested code I could drop into the repo, including the tests and the UML I was missing. |
| **Problems noticed** | GitHub blocked the `tests/`, `diagrams/` and `ai_interactions.md` pages, so the UML and test scores were only ranges until I pasted those files in. | The prompt was ambiguous, so the model had to guess what "the code" meant. It left the README, reflection and stretch features untouched, so I needed another prompt. |
| **Decision** | Kept: the rubric-anchored audit was the best way to find what was wrong. | Not enough on its own: a short prompt gave a partial result. |

**Which approach did you use in your final implementation and why?**

I combined them: the final prompt ("make sure all the files match for rubric ... extra point should be included") attached all my actual files and the full rubric, which is Option A's strength, and asked for the complete result, which fixed Option B's gap. It produced the most complete and verifiable outcome: every file checked against the rubric, tests that run, and real output pasted into the README. The lesson for future prompts is to include the requirements and the real files, and to say exactly which deliverables are wanted.
