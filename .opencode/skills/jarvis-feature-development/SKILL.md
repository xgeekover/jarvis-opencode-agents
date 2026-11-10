---
name: jarvis-feature-development
description: Checklist for running one development request (feature, fix, refactor) through the full Jarvis Dev Factory workflow - triage, requirements, plan, isolated worktree, developer, tester, fresh reviewer, integrator, quality gate, report. Use when the user asks the Jarvis Queen to build, fix or change something in a project that has .jarvis/project.json.
license: MIT
---

# jarvis-feature-development

**Entry point:** `/jarvis-feature <what to build or fix> [--track simple|standard|parallel]`

You are the Queen. Follow the `jarvis-queen` agent instructions exactly; this skill is the checklist. Load `jarvis-factory` first for the file formats.

## 0. Preflight
- [ ] `.jarvis/project.json` exists. If not, run `/jarvis-analyze` first.
- [ ] Note mandatory gate commands that are missing (build, test, lint). They will BLOCK the gate — tell the human now, not at the end.
- [ ] No open task in `.jarvis/tasks/*/task.md` touches the same files.

## 1. Triage and create
- [ ] Choose the track (table in the Queen instructions). When unsure, `standard`. If the human passed `--track`, use it unless it is unsafe, and say why if you override it.
- [ ] Create `.jarvis/tasks/<TASK-ID>/task.md` with the request verbatim → status `REQUEST`, then `REQUIREMENTS_ANALYSIS`.

## 2. Requirements and plan
- simple: write `requirements.json` and `plan.json` yourself (schemas in `jarvis-factory`).
- standard / parallel: delegate to `jarvis-planner` with the envelope; save its `requirements` and `plan` parts.
- [ ] Resolve `open_questions` with the human; if the answers change the requirements, update them.
- [ ] → `PLANNING`: check the plan's claims against the code. → `TASK_ASSIGNMENT`.
- parallel: create one sibling task per independent plan task and run each through steps 3–6; at most 2 developers at once; the parent becomes the umbrella you report on (or `CANCELLED` with the note "split into siblings …").

## 3. Assignment
- [ ] `git worktree add .jarvis/worktrees/<TASK-ID> -b jarvis/<TASK-ID> <base>` (the human approves).
- [ ] Record `workdir` (absolute) and `base_ref` (`git -C <wd> rev-parse HEAD`) in `task.md` → `DEVELOPMENT`.

## 4. Development → testing → review → integration
For each stage: delegate (or do it yourself on the simple track), save the JSON, verify it, then move forward or record a failure.
- DEVELOPMENT: `jarvis-developer` → `development-c<N>.json` → compare `files_changed` with `git -C <wd> status --porcelain -uall` → `TESTING`.
- TESTING: `jarvis-tester` (simple: run build + test yourself) → `testing-c<N>.json` → `CODE_REVIEW`.
- CODE_REVIEW: `/jarvis-review <TASK-ID>` → `INTEGRATION`.
- INTEGRATION: `jarvis-integrator` (simple: merge check + scope check yourself) → `integration-c<N>.json` → `QUALITY_GATE`.
- On failure: record it; back to DEVELOPMENT for at most 2 automatic retries with `previous_failures` filled in; after that ESCALATED — stop and ask the human.

## 5. Quality gate
- [ ] `/jarvis-gate <TASK-ID>`. All mandatory gates PASSED → `COMPLETED`; otherwise record the failure with the failing gate ids.

## 6. Report
- [ ] Write `REPORT.md` and give the human the summary from the Queen instructions. Changes stay **uncommitted** on branch `jarvis/<TASK-ID>` in the worktree. Offer the proposed commit message and the merge commands; the human runs them.

## Never
Commit, push or merge. Skip a stage. Save an artifact you did not receive or observe. Mark COMPLETED without a PASSED gate.
