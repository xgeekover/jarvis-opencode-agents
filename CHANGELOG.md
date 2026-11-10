# Changelog

## v1.0.0 — 2026-11-10
- First release for OpenCode (V1 frontmatter, loads on 1.18+; V2 translates it automatically).
- Jarvis Dev Factory: `jarvis-queen` (primary) + `jarvis-planner`, `jarvis-developer`, `jarvis-tester`, `jarvis-reviewer`, `jarvis-integrator` (subagents).
- Workflow skills: `jarvis-factory` (state layout, envelope template, JSON schemas), `jarvis-project-analysis`, `jarvis-feature-development`, `jarvis-code-review`, `jarvis-quality-gate`; commands `/jarvis-analyze`, `/jarvis-feature`, `/jarvis-review`, `/jarvis-gate`, `/jarvis-status`.
- 13 general development skills.
- Installers for Windows PowerShell 5.1/7 (`install/install.ps1`) and bash (`install/install.sh`), with `-Only`, `-WithTemplates`, `-DryRun`, `-Uninstall`.
- Templates: `templates/opencode.json` (permission rules), `templates/AGENTS.md`.
- CI: static checks and an OpenCode load check on Windows and Linux.
