import pytest
from pawpal_system import Task, Pet, Owner, Scheduler


# --- Task tests ---

def test_task_valid():
    t = Task("Walk", 30, "high")
    assert t.title == "Walk"
    assert t.duration_minutes == 30
    assert t.priority == "high"

def test_task_invalid_priority():
    with pytest.raises(ValueError):
        Task("Walk", 30, "urgent")

def test_task_invalid_duration():
    with pytest.raises(ValueError):
        Task("Walk", 0, "low")


# --- Scheduler tests ---

def make_scheduler(available_minutes=120):
    owner = Owner("Jordan", available_minutes=available_minutes)
    pet = Pet("Mochi", "dog")
    return Scheduler(owner, pet)


def test_high_priority_scheduled_first():
    s = make_scheduler(60)
    s.add_task(Task("Grooming", 30, "low"))
    s.add_task(Task("Walk", 30, "high"))
    scheduled, _ = s.generate_plan()
    assert scheduled[0].task.title == "Walk"


def test_task_skipped_when_no_time():
    s = make_scheduler(available_minutes=20)
    s.add_task(Task("Walk", 30, "high"))
    scheduled, skipped = s.generate_plan()
    assert len(scheduled) == 0
    assert len(skipped) == 1


def test_partial_fit():
    s = make_scheduler(available_minutes=40)
    s.add_task(Task("Walk", 30, "high"))
    s.add_task(Task("Feeding", 20, "medium"))
    scheduled, skipped = s.generate_plan()
    assert len(scheduled) == 1
    assert scheduled[0].task.title == "Walk"
    assert len(skipped) == 1
    assert skipped[0][0].title == "Feeding"


def test_all_tasks_fit():
    s = make_scheduler(available_minutes=60)
    s.add_task(Task("Walk", 20, "high"))
    s.add_task(Task("Feeding", 10, "medium"))
    s.add_task(Task("Playtime", 15, "low"))
    scheduled, skipped = s.generate_plan()
    assert len(scheduled) == 3
    assert len(skipped) == 0


def test_scheduled_times_are_sequential():
    s = make_scheduler(available_minutes=60)
    s.add_task(Task("Walk", 20, "high"))
    s.add_task(Task("Feeding", 10, "medium"))
    scheduled, _ = s.generate_plan()
    assert scheduled[1].start_minutes == scheduled[0].start_minutes + scheduled[0].task.duration_minutes


def test_empty_task_list():
    s = make_scheduler()
    scheduled, skipped = s.generate_plan()
    assert scheduled == []
    assert skipped == []
