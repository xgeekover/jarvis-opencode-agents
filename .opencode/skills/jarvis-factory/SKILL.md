---
name: jarvis-factory
description: Reference for the Jarvis Dev Factory workflow in OpenCode - the .jarvis/ task-state layout, task.md format, task-envelope template, project.json format, gate record format and the JSON output schemas of the jarvis-* subagents. Load it at the start of any Jarvis task (jarvis-queen does) or when writing/reading files under .jarvis/.
license: MIT
---

# Jarvis Dev Factory — reference

Supporting files in this skill's directory:

| File | Use |
|---|---|
| `envelope-template.md` | Prompt template for delegating to a `jarvis-*` subagent |
| `project.example.json` | Example `.jarvis/project.json` |
| `schemas/task-envelope.schema.json` | Queen → agent input |
| `schemas/planner-output.schema.json` | Planner output (= requirements + plan) |
| `schemas/requirements.schema.json`, `schemas/plan.schema.json` | Parts of the planner output |
| `schemas/developer-output.schema.json` | Developer output |
| `schemas/tester-output.schema.json` | Tester output (`role: "queen"` when the Queen runs the tests on the simple track) |
| `schemas/reviewer-output.schema.json` | Reviewer output |
| `schemas/integrator-output.schema.json` | Integrator output (`role: "queen"` on the simple track) |

## State layout (in the target project root)

```
.jarvis/
├── project.json                  # commands + default branch (human-confirmed; see project.example.json)
├── analysis.md                   # written by /jarvis-analyze
├── worktrees/<TASK-ID>/          # isolated git worktree per task (branch jarvis/<TASK-ID>)
└── tasks/<TASK-ID>/
    ├── task.md                   # status, track, cycle, retries, workdir, base_ref, history
    ├── envelope-<role>-c<N>.md   # what each subagent was told
    ├── requirements.json         # cycle-independent
    ├── plan.json
    ├── development-c<N>.json     # one per cycle
    ├── testing-c<N>.json
    ├── review-c<N>.json
    ├── integration-c<N>.json
    ├── gate-c<N>.json
    ├── failure-<n>.md            # details for each recorded failure
    └── REPORT.md                 # final report (COMPLETED / FAILED / ESCALATED / CANCELLED)
```

Propose adding `.jarvis/` to the project's `.gitignore` (the human decides). Task ids: `T-YYYYMMDD-HHMMSS` in local time.

## task.md format

```markdown
# T-20261110-093000 — <short title>

- **Project:** <name> · **Track:** standard · **Status:** DEVELOPMENT
- **Cycle:** 1 · **Retries:** 0/2
- **Workdir:** C:/work/app/.jarvis/worktrees/T-20261110-093000 · **Branch:** jarvis/T-20261110-093000
- **Base:** 3f2a9c1 (main)

## Request (verbatim)
> <the human's request>

## History
| Time | From → To | By | Note |
|---|---|---|---|
| 2026-11-10 09:30 | REQUEST → REQUIREMENTS_ANALYSIS | queen | track standard |

## Failures
| # | Stage | Cycle | Reason | Details |
|---|---|---|---|---|
```

Allowed states: `REQUEST`, `REQUIREMENTS_ANALYSIS`, `PLANNING`, `TASK_ASSIGNMENT`, `DEVELOPMENT`, `TESTING`, `CODE_REVIEW`, `INTEGRATION`, `QUALITY_GATE`, `COMPLETED`, plus `ESCALATED`, `FAILED`, `CANCELLED`. Move only one step forward at a time; failures go back to `DEVELOPMENT` (cycle + 1) while retries < 2, otherwise to `ESCALATED`.

## Artifacts

Save each subagent's final JSON block **exactly as returned** under the name in the layout above. Check it against the matching schema (required fields, enums, `task_id`). If it is invalid, send it back to the same agent to fix; never edit an agent's output yourself. On the simple track the Queen writes `requirements.json`, `plan.json`, `testing-c<N>.json` (`role: "queen"`, from real exit codes) and `integration-c<N>.json` (`role: "queen"`).

## Gate record (`gate-c<N>.json`)

```json
{
  "task_id": "T-...", "cycle": 1, "ran_at": "2026-11-10T11:02:00+09:00",
  "workdir": "C:/work/app/.jarvis/worktrees/T-...", "base_ref": "3f2a9c1",
  "fingerprint_before": "<git status --porcelain -uall output + git diff HEAD --stat>",
  "fingerprint_after": "<same, taken after the last command>",
  "results": [
    {"id": "build", "mandatory": true, "status": "PASSED", "cmd": "mvn -B -DskipTests package", "exit_code": 0, "duration_s": 41.2, "output_tail": "..."},
    {"id": "integration_tests", "mandatory": "when_configured", "status": "SKIPPED", "details": "no integration_test configured"}
  ],
  "overall": "PASSED",
  "failing_gates": []
}
```

Statuses: `PASSED`, `FAILED` (non-zero exit, timeout, no-op command or failed artifact check), `BLOCKED` (mandatory command missing), `NOT_APPLICABLE` (declared by the human in `project.json` with a reason), `SKIPPED` (optional gate not configured). `overall` is `PASSED` only when no mandatory gate is FAILED or BLOCKED and the two fingerprints are identical.
