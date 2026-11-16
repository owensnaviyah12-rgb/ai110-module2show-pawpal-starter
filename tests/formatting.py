import os
import sys
import unicodedata
from typing import Iterable

from pawpal_system import PlanItem, Task

ANSI = {
    "red": "\033[91m",
    "yellow": "\033[93m",
    "green": "\033[92m",
    "cyan": "\033[96m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "reset": "\033[0m",
}

PRIORITY_BADGE = {"high": "🔴 high", "medium": "🟡 medium", "low": "🟢 low"}
PRIORITY_COLOR = {"high": "red", "medium": "yellow", "low": "green"}


def color_enabled() -> bool:
    """Return True if ANSI colors should be printed."""
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("PAWPAL_COLOR"):
        return True
    return sys.stdout.isatty()


def colorize(text: str, color: str) -> str:
    """Wrap text in an ANSI color if colors are enabled."""
    if not color_enabled():
        return text
    return f"{ANSI[color]}{text}{ANSI['reset']}"


def status_icon(completed: bool) -> str:
    """Return a checkmark or an empty box."""
    return "✅" if completed else "⬜"


def priority_badge(priority: str) -> str:
    """Return a colored emoji badge such as '🔴 high'."""
    return colorize(PRIORITY_BADGE[priority], PRIORITY_COLOR[priority])


def header(title: str) -> str:
    """Return a bold section title with an underline."""
    return f"\n{colorize(title, 'bold')}\n{'-' * len(title)}"


def _visible_len(text: str) -> int:
    """On-screen width of text: ANSI codes are 0, wide emoji are 2."""
    for code in ANSI.values():
        text = text.replace(code, "")
    width = 0
    for ch in text:
        if unicodedata.category(ch) in ("Mn", "Me", "Cf"):
            continue  # combining marks / variation selectors take no space
        width += 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
    return width


def _pad(text: str, width: int) -> str:
    return text + " " * (width - _visible_len(text))


def format_table(headers: list[str], rows: list[list[str]]) -> str:
    """Return a box-drawn table as a string."""
    widths = [
        max(_visible_len(str(cell)) for cell in [h] + [r[i] for r in rows])
        for i, h in enumerate(headers)
    ]
    line = lambda l, m, r: l + m.join("─" * (w + 2) for w in widths) + r  # noqa: E731
    out = [line("┌", "┬", "┐")]
    out.append("│ " + " │ ".join(_pad(h, w) for h, w in zip(headers, widths)) + " │")
    out.append(line("├", "┼", "┤"))
    for row in rows:
        out.append("│ " + " │ ".join(_pad(str(c), w) for c, w in zip(row, widths)) + " │")
    out.append(line("└", "┴", "┘"))
    return "\n".join(out)


def format_schedule(tasks: Iterable[Task]) -> str:
    """Return a table of tasks: status, time, pet, task, priority, duration."""
    rows = [
        [
            status_icon(t.completed),
            f"{t.time}-{t.end_time}",
            t.pet_name,
            t.description,
            priority_badge(t.priority),
            f"{t.duration_minutes} min",
        ]
        for t in tasks
    ]
    if not rows:
        return "(no tasks)"
    return format_table(["", "Time", "Pet", "Task", "Priority", "Length"], rows)


def format_plan(plan: Iterable[PlanItem]) -> str:
    """Return a table of a time-blocked plan, marking moved/unplaced tasks."""
    rows = []
    for item in plan:
        task = item.task
        if item.start is None:
            when, note = "--", colorize("❌ no room today", "red")
        elif item.moved:
            when, note = f"{item.start}-{item.end}", colorize(f"↪ moved from {task.time}", "cyan")
        else:
            when, note = f"{item.start}-{item.end}", "on time"
        rows.append(
            [when, task.pet_name, task.description, priority_badge(task.priority), note]
        )
    if not rows:
        return "(nothing to plan)"
    return format_table(["Time", "Pet", "Task", "Priority", "Note"], rows)
