#!/usr/bin/env python3
"""
Task Tracker CLI - A simple command line task management tool.

Usage:
    python TaskTracker.py add "Task description"
    python TaskTracker.py update <id> "New description"
    python TaskTracker.py delete <id>
    python TaskTracker.py mark-in-progress <id>
    python TaskTracker.py mark-done <id>
    python TaskTracker.py list [done|todo|in-progress]
"""

import sys
import json
import os
from datetime import datetime

# Path to the JSON file in the current directory
TASKS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.json")


def load_tasks():
    """Load tasks from the JSON file. Creates the file if it doesn't exist."""
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except (json.JSONDecodeError, IOError):
        return []


def save_tasks(tasks):
    """Save tasks to the JSON file."""
    try:
        with open(TASKS_FILE, "w") as f:
            json.dump(tasks, f, indent=2)
    except IOError as e:
        print(f"Error: Could not save tasks - {e}")
        sys.exit(1)


def get_next_id(tasks):
    """Generate the next unique task ID."""
    if not tasks:
        return 1
    return max(task["id"] for task in tasks) + 1


def find_task(tasks, task_id):
    """Find a task by its ID. Returns the task dict or None."""
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None


def now_timestamp():
    """Return the current datetime as an ISO 8601 string."""
    return datetime.now().isoformat()


# ── Commands ──────────────────────────────────────────────────────────────────


def cmd_add(args):
    """Add a new task."""
    if len(args) < 1:
        print("Error: Missing task description.")
        print('Usage: task-cli add "Buy groceries"')
        sys.exit(1)

    description = args[0]
    tasks = load_tasks()
    task_id = get_next_id(tasks)
    timestamp = now_timestamp()

    task = {
        "id": task_id,
        "description": description,
        "status": "todo",
        "createdAt": timestamp,
        "updatedAt": timestamp,
    }

    tasks.append(task)
    save_tasks(tasks)
    print(f"Task added successfully (ID: {task_id})")


def cmd_update(args):
    """Update an existing task's description."""
    if len(args) < 2:
        print("Error: Missing task ID or new description.")
        print('Usage: task-cli update 1 "New description"')
        sys.exit(1)

    try:
        task_id = int(args[0])
    except ValueError:
        print(f"Error: '{args[0]}' is not a valid task ID.")
        sys.exit(1)

    new_description = args[1]
    tasks = load_tasks()
    task = find_task(tasks, task_id)

    if task is None:
        print(f"Error: Task with ID {task_id} not found.")
        sys.exit(1)

    task["description"] = new_description
    task["updatedAt"] = now_timestamp()
    save_tasks(tasks)
    print(f"Task {task_id} updated successfully.")


def cmd_delete(args):
    """Delete a task by ID."""
    if len(args) < 1:
        print("Error: Missing task ID.")
        print("Usage: task-cli delete 1")
        sys.exit(1)

    try:
        task_id = int(args[0])
    except ValueError:
        print(f"Error: '{args[0]}' is not a valid task ID.")
        sys.exit(1)

    tasks = load_tasks()
    original_count = len(tasks)
    tasks = [t for t in tasks if t["id"] != task_id]

    if len(tasks) == original_count:
        print(f"Error: Task with ID {task_id} not found.")
        sys.exit(1)

    save_tasks(tasks)
    print(f"Task {task_id} deleted successfully.")


def cmd_mark(args, status):
    """Mark a task with the given status."""
    if len(args) < 1:
        print("Error: Missing task ID.")
        print(f"Usage: task-cli mark-{status.replace(' ', '-')} 1")
        sys.exit(1)

    try:
        task_id = int(args[0])
    except ValueError:
        print(f"Error: '{args[0]}' is not a valid task ID.")
        sys.exit(1)

    tasks = load_tasks()
    task = find_task(tasks, task_id)

    if task is None:
        print(f"Error: Task with ID {task_id} not found.")
        sys.exit(1)

    task["status"] = status
    task["updatedAt"] = now_timestamp()
    save_tasks(tasks)
    print(f"Task {task_id} marked as {status}.")


def cmd_list(args):
    """List tasks, optionally filtered by status."""
    valid_statuses = {"done", "todo", "in-progress"}
    status_filter = None

    if len(args) >= 1:
        status_filter = args[0].lower()
        if status_filter not in valid_statuses:
            print(f"Error: Invalid status '{args[0]}'. Use: done, todo, or in-progress.")
            sys.exit(1)

    tasks = load_tasks()

    if status_filter:
        tasks = [t for t in tasks if t["status"] == status_filter]

    if not tasks:
        label = f" ({status_filter})" if status_filter else ""
        print(f"No tasks found{label}.")
        return

    # ── Pretty-print table ────────────────────────────────────────────────
    header_label = f"Tasks ({status_filter})" if status_filter else "All Tasks"
    print(f"\n  {header_label}")
    print("  " + "-" * 72)
    print(f"  {'ID':<5} {'Status':<14} {'Description':<35} {'Updated'}")
    print("  " + "-" * 72)

    for t in tasks:
        # Truncate long descriptions for display
        desc = t["description"]
        if len(desc) > 33:
            desc = desc[:30] + "..."

        # Format the timestamp for readability
        try:
            dt = datetime.fromisoformat(t["updatedAt"])
            updated = dt.strftime("%Y-%m-%d %H:%M")
        except (ValueError, KeyError):
            updated = "N/A"

        print(f"  {t['id']:<5} {t['status']:<14} {desc:<35} {updated}")

    print("  " + "-" * 72)
    print(f"  Total: {len(tasks)} task(s)\n")


# ── Main entry point ──────────────────────────────────────────────────────────


def print_usage():
    """Print help / usage information."""
    print(
        """
Task Tracker CLI
================

Usage:
  python TaskTracker.py <command> [arguments]

Commands:
  add <description>              Add a new task
  update <id> <description>      Update a task's description
  delete <id>                    Delete a task
  mark-in-progress <id>          Mark a task as in progress
  mark-done <id>                 Mark a task as done
  list [done|todo|in-progress]   List tasks (optionally filtered by status)
"""
    )


def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(0)

    command = sys.argv[1].lower()
    args = sys.argv[2:]

    commands = {
        "add": lambda: cmd_add(args),
        "update": lambda: cmd_update(args),
        "delete": lambda: cmd_delete(args),
        "mark-in-progress": lambda: cmd_mark(args, "in-progress"),
        "mark-done": lambda: cmd_mark(args, "done"),
        "list": lambda: cmd_list(args),
    }

    if command in commands:
        commands[command]()
    else:
        print(f"Error: Unknown command '{command}'.")
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
