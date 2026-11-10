# Project rules (Jarvis Dev Factory)

<!-- Copy this section into the project's AGENTS.md (OpenCode reads AGENTS.md at the project root). -->

## Jarvis workflow
- Feature work, bug fixes and refactors that should be planned, tested and reviewed go through the **Jarvis Queen**: switch to the `jarvis-queen` agent (Tab) or run `/jarvis-feature <request>`.
- First time in this project: `/jarvis-analyze` writes `.jarvis/project.json` (build/test/lint commands, confirmed by a human).
- Task state lives in `.jarvis/tasks/<TASK-ID>/`; task worktrees live in `.jarvis/worktrees/<TASK-ID>/` on branch `jarvis/<TASK-ID>`. `.jarvis/` is local state and stays out of git.
- `/jarvis-status` lists open tasks. `/jarvis-review <TASK-ID>` and `/jarvis-gate <TASK-ID>` run the review and quality-gate stages.

## Always
- Never commit, push, merge, rebase, reset or delete branches/worktrees on your own: prepare the step and let the human run it.
- Never read or print `.env*`, keys or credentials.
- Report only what you verified: real commands, real exit codes.
