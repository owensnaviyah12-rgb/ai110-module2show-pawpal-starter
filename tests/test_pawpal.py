from pawpal_system import Task, Pet


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