import json
from pathlib import Path


class UserAccount:
    def __init__(self, username, tasks=None):
        if not username.strip():
            raise ValueError("Username cannot be empty.")
        self.username = username.strip()
        self.tasks = tasks if tasks is not None else []

    def add_task(self, title):
        if not title.strip():
            raise ValueError("Task title cannot be empty.")
        task = {
            "id": max((task["id"] for task in self.tasks), default=0) + 1,
            "title": title.strip(),
            "completed": False,
        }
        self.tasks.append(task)
        return task

    def complete_task(self, task_id):
        for task in self.tasks:
            if task["id"] == task_id:
                if task["completed"]:
                    raise ValueError("Task is already complete.")
                task["completed"] = True
                return task
        raise ValueError(f"Task {task_id} was not found for {self.username}.")


def load_accounts(filename):
    path = Path(filename)
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as file:
        accounts = json.load(file)
    if not isinstance(accounts, dict):
        raise ValueError("Task file must contain user accounts.")
    for username, tasks in accounts.items():
        if not isinstance(tasks, list):
            raise ValueError(f"Invalid task list for {username}.")
        ids = set()
        for task in tasks:
            if (not isinstance(task, dict)
                    or type(task.get("id")) is not int
                    or task["id"] < 1
                    or task["id"] in ids
                    or not isinstance(task.get("title"), str)
                    or type(task.get("completed")) is not bool):
                raise ValueError(f"Invalid task data for {username}.")
            ids.add(task["id"])
    return accounts


def save_accounts(filename, accounts):
    path = Path(filename)
    # Replace the original only after the updated file has been written.
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8") as file:
        json.dump(accounts, file, indent=2, ensure_ascii=False)
        file.write("\n")
    temporary.replace(path)
