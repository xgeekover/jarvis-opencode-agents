---
name: jarvis-quality-gate
description: Run the Jarvis Dev Factory quality gates for a task in QUALITY_GATE - requirements, build, unit and integration tests, static analysis, security review, code review and git diff inspection - with the project's real commands, record exit codes and a worktree fingerprint, then complete the task or send it back. Use when a Jarvis task reaches QUALITY_GATE or the user asks whether a task can be completed.
license: MIT
---

# jarvis-quality-gate

**Entry point:** `/jarvis-gate <TASK-ID>`

## Steps
1. Read `.jarvis/tasks/<TASK-ID>/task.md`. The status must be `QUALITY_GATE`; if it is not, tell the user which stage the task is in and what it is waiting for.
2. Check that no other full test suite is running on this machine for another task (one gate at a time). Then take `fingerprint_before`: `git -C <wd> status --porcelain -uall` and `git -C <wd> diff HEAD --stat`.
3. Run the gates in this order, each command **once**, in the worktree, using the commands in `.jarvis/project.json`:

| Gate | Type | Mandatory |
|---|---|---|
| requirements_completeness | artifact: `requirements.json` has ≥1 acceptance criterion and 0 open questions | yes |
| build | command `build` | yes |
| unit_tests | command `test` | yes |
| integration_tests | command `integration_test` | when configured |
| static_analysis | command `lint` | yes |
| security_review | artifact: latest-cycle review `security_verdict` PASS, no critical/high security finding | yes |
| code_review | artifact: latest-cycle review `APPROVE`, no critical/high finding | yes |
| git_diff_inspection | diff vs `base_ref` non-empty; no conflict markers; no secret-like files or credentials | yes |

   Record for each command: `cmd`, the real `exit_code`, `duration_s` and the last ~40 lines of output.
4. Take `fingerprint_after` and write `gate-c<N>.json` (format in the `jarvis-factory` skill).
5. Interpret each status:
   - `PASSED`: the command ran and exited 0, or the artifact check was satisfied.
   - `FAILED`: non-zero exit, timeout, a no-op command, or a failed artifact check.
   - `BLOCKED`: a mandatory gate has no command configured. This is **not** a pass. The human must set the command, or declare `not_applicable` with a reason in `.jarvis/project.json`.
   - `NOT_APPLICABLE`: declared by the human; show the reason in your report.
   - `SKIPPED`: an optional gate that is not configured.
6. Decide:
   - Overall `PASSED` and identical fingerprints → `COMPLETED`, then write `REPORT.md`.
   - Fingerprints differ (something changed while the gate ran) → run the gate **once** more. If they differ again, the commands themselves change files git sees: mark `git_diff_inspection` FAILED with the differing paths and ask the human to fix `.gitignore` or the commands. Never loop.
   - Any FAILED gate → record a QUALITY_GATE failure naming the failing gates and include the failing command's output tail in the next developer envelope.
   - Only BLOCKED gates → stop and ask the human to configure them. Do not fail the task for a missing configuration unless the human says so.
7. Report the gate table exactly as recorded: commands, exit codes and statuses. Never summarise a FAILED or BLOCKED gate as passed. Never estimate a score.

## Diagnostics
Running a subset (for debugging) is allowed, but a partial run never counts toward COMPLETED: mark it `"partial": true` in the record.
