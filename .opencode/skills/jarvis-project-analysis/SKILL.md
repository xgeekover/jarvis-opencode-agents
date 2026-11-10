---
name: jarvis-project-analysis
description: Analyse a repository for the Jarvis Dev Factory - stack, layout, build/test/lint commands verified by running them, risks - and write .jarvis/analysis.md and .jarvis/project.json after the human confirms the commands. Use before the first Jarvis task in a project, when .jarvis/project.json is missing, or when the user asks to onboard or re-analyse a codebase.
license: MIT
---

# jarvis-project-analysis

**Entry point:** `/jarvis-analyze [path]` (default: the current project root).

## Goal
Know the project well enough that later quality gates run **real** commands. Analysis is read-only; writing `.jarvis/project.json` needs the human's confirmation.

## Steps
1. **Preconditions**
   - The path is a git repository: `git -C <path> rev-parse --show-toplevel`. If not, stop and ask the human. Never run `git init` for them.
   - `git -C <path> status --short`: report whether the tree is dirty. Task worktrees start from a commit, so uncommitted changes would not be in them.
   - If `.jarvis/project.json` already exists, show it and ask whether to re-analyse.
2. **Survey** (read, grep, glob, read-only git; delegate to `jarvis-planner` if the repository is large):
   - languages, frameworks and versions; the build or package manager (`package.json`, `pyproject.toml`, `pom.xml`, `build.gradle*`, `*.csproj`/`*.sln`, `Cargo.toml`, `go.mod`, `Makefile`, …);
   - directory layout, entry points, where the tests live, the test framework;
   - existing CI configuration (`.github/workflows/*`, `azure-pipelines.yml`, `Jenkinsfile`, `.gitlab-ci.yml`): the best source for the canonical build, test and lint commands;
   - risks: no tests, generated code, monorepo, required services (database, Docker), secrets handling (only note that `.env` exists — **never read it**).
3. **Derive commands** for `build`, `test`, `lint` and optional `integration_test`. Prefer what CI runs. Write them so they run from the **repository root** in the shell OpenCode uses on this machine (on Windows prefer commands that work in both Git Bash and PowerShell, e.g. `mvn -f backend/pom.xml test` or `npm --prefix frontend test` instead of `cd backend && …`).
4. **Verify each command by running it once** at the repository root, preferably in a throw-away worktree so the main tree is untouched:
   `git worktree add --detach .jarvis/worktrees/_analysis HEAD` (the human approves), run the commands there in order build → test → lint, note exit code and duration, then ask the human to remove it (`git worktree remove .jarvis/worktrees/_analysis`).
   - A command that fails now is reported as-is. Do not "fix" it by choosing a no-op (`true`, `exit 0`, `echo …` are rejected as gate evidence).
   - If a stage genuinely does not exist (e.g. no build step, no linter), leave it empty and say so. Only the human may declare it `not_applicable` with a reason.
   - Do not install dependencies unless the human agrees. If a command fails because dependencies are missing, say so.
   - After build and test, run `git -C .jarvis/worktrees/_analysis status --porcelain -uall`. Anything listed is output the commands write into the tree without it being git-ignored; it would make every quality-gate fingerprint differ. Report those paths and propose `.gitignore` entries.
5. **Write `.jarvis/analysis.md`**: stack, layout, the commands with their observed exit codes and durations, test coverage notes, risks, recommended default track.
6. **Show the proposed `.jarvis/project.json`** (format: `project.example.json` in the `jarvis-factory` skill) and ask the human to confirm or edit the commands. Write it only after they confirm; record who confirmed in `confirmed_by`.
7. **Report**: the commands and their observed results, which gates will be BLOCKED until configured, and the paths of the two files.

## Rules
- Do not modify the target repository's tracked files.
- Record only what you observed. Commands you could not run are reported as not run.
