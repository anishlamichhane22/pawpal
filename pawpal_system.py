PRIORITY_RANK = {"high": 3, "medium": 2, "low": 1}

START_HOUR = 8  # schedule begins at 8:00 AM


def _format_time(minutes_from_midnight: int) -> str:
    h = minutes_from_midnight // 60
    m = minutes_from_midnight % 60
    period = "AM" if h < 12 else "PM"
    h12 = h % 12 or 12
    return f"{h12}:{m:02d} {period}"


class Task:
    def __init__(self, title: str, duration_minutes: int, priority: str = "medium"):
        if priority not in PRIORITY_RANK:
            raise ValueError(f"priority must be one of {list(PRIORITY_RANK)}")
        if duration_minutes < 1:
            raise ValueError("duration_minutes must be at least 1")
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority

    def __repr__(self):
        return f"Task({self.title!r}, {self.duration_minutes}min, {self.priority})"


class Pet:
    def __init__(self, name: str, species: str):
        self.name = name
        self.species = species

    def __repr__(self):
        return f"Pet({self.name!r}, {self.species!r})"


class Owner:
    def __init__(self, name: str, available_minutes: int = 120):
        if available_minutes < 0:
            raise ValueError("available_minutes cannot be negative")
        self.name = name
        self.available_minutes = available_minutes

    def __repr__(self):
        return f"Owner({self.name!r}, {self.available_minutes}min available)"


class ScheduledTask:
    def __init__(self, task: Task, start_minutes: int, reason: str):
        self.task = task
        self.start_minutes = start_minutes  # minutes from midnight
        self.reason = reason

    @property
    def start_time_str(self) -> str:
        return _format_time(self.start_minutes)

    @property
    def end_time_str(self) -> str:
        return _format_time(self.start_minutes + self.task.duration_minutes)

    def __repr__(self):
        return f"ScheduledTask({self.task.title!r} @ {self.start_time_str})"


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet):
        self.owner = owner
        self.pet = pet
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def generate_plan(self) -> tuple[list[ScheduledTask], list[tuple[Task, str]]]:
        """Return (scheduled, skipped).

        scheduled: list of ScheduledTask in time order
        skipped:   list of (Task, reason_string) for tasks that didn't fit
        """
        sorted_tasks = sorted(
            self.tasks,
            key=lambda t: PRIORITY_RANK.get(t.priority, 0),
            reverse=True,
        )

        scheduled: list[ScheduledTask] = []
        skipped: list[tuple[Task, str]] = []
        time_remaining = self.owner.available_minutes
        current_minutes = START_HOUR * 60

        for task in sorted_tasks:
            if task.duration_minutes <= time_remaining:
                reason = (
                    f"{task.priority.capitalize()} priority — fits in remaining time "
                    f"({time_remaining} min left)."
                )
                scheduled.append(ScheduledTask(task, current_minutes, reason))
                current_minutes += task.duration_minutes
                time_remaining -= task.duration_minutes
            else:
                reason = (
                    f"Skipped — needs {task.duration_minutes} min but only "
                    f"{time_remaining} min remain."
                )
                skipped.append((task, reason))

        return scheduled, skipped