---
description: "Jarvis: list open Jarvis tasks with their status, cycle and next step"
agent: jarvis-queen
---
Read every `.jarvis/tasks/*/task.md` in this project. List the tasks that are not COMPLETED, FAILED or CANCELLED: id, title, status, cycle, retries, workdir and the next action. Then check each open worktree with `git -C <workdir> status --short`. Do not change anything.

Filter (optional): $ARGUMENTS
