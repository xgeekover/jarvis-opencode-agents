---
name: queen-orchestration
description: Run a Queen-led multi-agent workflow — a coordinator (the Queen) decomposes a goal, delegates to specialized worker agents in parallel, verifies each result with an independent adversarial reviewer, then synthesizes. Use when a task is large or multi-faceted enough to benefit from parallel specialized agents (big features, broad code reviews, research sweeps, migrations, multi-section design docs) OR when the user asks for orchestration / hive-mind / queen / swarm / multi-agent coordination. Do NOT use for small, single-file, or trivial tasks.
---

# Queen Orchestration

Coordinate a task as a **Queen (orchestrator)** directing specialized **worker** agents, then verify and synthesize their output. This is the "hive-mind" / orchestrator-worker pattern.

**Use only when the task is large or multi-faceted.** Orchestration has real token and latency cost — small or single-file tasks should be done directly, not delegated.

## Roles
- **Queen (you):** plan → decompose → delegate → verify → synthesize. Own the plan and the integration; do NOT write the bulk of the deliverable yourself.
- **Workers (isolated context each):** architect/planner, researcher (read-only), coder, tester, reviewer. Each worker gets ONE scoped sub-task, only the context it needs, its allowed tools, and the exact output shape it must return.

## Procedure
1. **Restate goal + success criteria** in one line. If the goal is ambiguous, ask the user BEFORE spawning any worker.
2. **Decompose** into independent sub-tasks. Label each as parallel-safe (touches disjoint files) or sequential.
3. **Plan gate (human-in-the-loop):** for large or risky work, show the decomposition to the user for approval before spawning workers.
4. **Delegate** each sub-task with: role, scoped input, allowed tools, and required return format. Run parallel-safe workers concurrently; give file-mutating parallel workers isolated git worktrees.
5. **Verify adversarially:** pass each worker's output to an independent reviewer worker prompted to REFUTE it (not confirm). Drop or re-task anything that fails verification. Default to "unverified" when the reviewer is unsure.
6. **Synthesize:** integrate only verified results into the final deliverable. Resolve conflicts yourself; explicitly flag anything left unverified.
7. **Report** what each worker did, what was verified, and what remains open.

## Topology
- **Hive (hierarchical) — default:** Queen → workers → back to Queen. Best for most work.
- **Swarm (mesh):** lightweight peer coordination for a quick single task; skip the full hierarchy.
- For multi-step work, keep a shared scratchpad/memory file so workers can read prior state.

## Guardrails
- **Scale the fleet to the task:** 2–3 workers for a focused job; more only for genuinely broad work. If you cap coverage, say so.
- **Verify before merge:** every worker output passes a verification step before entering the deliverable. Plausible ≠ correct.
- **No parallel file conflicts:** parallel workers must touch disjoint files; isolate with worktrees. The Queen owns the merge and final review.
- **Watch cost:** each worker is a full context window. Stop when marginal value < token/latency cost.

## Tool mapping
- **Claude Code:** use the **Workflow** tool for fan-out (pipeline / parallel, judge-panel, adversarial-verify, loop-until-dry) or the **Agent** tool for individual workers. The main loop is the Queen.
- **OpenCode:** the primary `build` agent (or a custom `queen` primary) is the Queen; define worker subagents in `.opencode/agents/*.md` (architect / coder / tester / reviewer / researcher) and invoke them with `@mention`. Keep shared model/MCP config in `opencode.json`.

## Presets
Ready-made worker rosters + flows for common jobs (files in this skill's `presets/` folder). Load the matching one when the task fits; otherwise compose workers ad hoc per Roles/Procedure above.
- **Design document (English)** — `presets/design-doc.md`: outliner → parallel section-writers → per-section terminology + english editors → whole-doc consistency reviewer. Draft and edit are separate passes; a shared glossary/template is the main quality lever.
- **Code review** — `presets/code-review.md`: parallel dimension reviewers (correctness / security / performance / convention / test-coverage) → adversarial verifier that refutes each finding → severity-ranked, file:line report. No edits unless asked.
- **Code development (feature)** — `presets/code-development.md`: architect plan (plan gate) → parallel coders in isolated worktrees → tester (fix loop) → adversarial reviewer. Test-driven done-gate; chains into the code-review preset.
