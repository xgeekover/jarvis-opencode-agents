# Preset: Code Development (Feature)

Queen-worker roster for building a feature end to end. This is the explore -> plan -> implement -> verify loop scaled to multiple agents. Chains into the code-review preset for the final gate.

## Workers
- **architect (planner, read-only):** Decompose the feature into an implementation plan — files/modules to touch, interfaces & contracts, data changes, sequence, and a test strategy. Output the plan + a task breakdown (one task = one coder), marking parallel-safe vs sequential tasks. NO edits.
- **coder (×N, one per task):** Implement ONE scoped task per the plan, inside the given file/module boundary only. Isolated git worktree when running in parallel. Return the changed files + key decisions + anything that deviated from the plan. No out-of-scope refactors.
- **tester:** Write/extend tests for the implemented code and RUN them. Report pass/fail with the failing output. Feed failures back to the OWNING coder (fix loop), not a fresh agent.
- **reviewer (adversarial):** Review the integrated diff for correctness/security/convention and try to REFUTE. Confirm only concrete, real issues. This is the done-gate.

## Flow (Queen)
1. Restate the feature + acceptance criteria in one line. If ambiguous, ask before planning.
2. architect -> implementation plan + task breakdown. PLAN GATE: get user approval before any code.
3. Spawn coders per task. Parallel ONLY for disjoint files (isolated worktrees); sequential where tasks depend on each other. The Queen owns the merge.
4. tester writes + runs tests per module. Any failure -> back to the owning coder. Loop until green.
5. reviewer adversarially reviews the integrated diff (or run the code-review preset here).
6. Queen integrates, runs the FULL test/build, and reports. Not "done" until tests pass AND review is clean.

## Notes
- The #1 risk is parallel coders editing the same file -> conflicts. Enforce disjoint boundaries + worktrees; the Queen merges and re-runs tests.
- Test-driven gate: nothing ships until tests pass and the adversarial review is clean.
- Map workers to existing skills where available: codex-grade-coding (implement), tdd (tests), code-reviewer / systematic-debugging (review & fix).
- Small change (a few lines, one file)? Skip the fleet and implement directly.
