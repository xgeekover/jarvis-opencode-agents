# Preset: Code Review

Queen-worker roster for a multi-dimension code review of a diff, with adversarial verification to kill false positives.

## Workers (read-only; each reviews the SAME diff through ONE lens)
- **correctness-reviewer:** bugs, logic errors, edge cases, error handling, concurrency. Cite file:line.
- **security-reviewer:** OWASP-class issues — injection, authz/authn, secrets, unsafe deserialization, input validation. Cite file:line.
- **performance-reviewer:** N+1 queries, needless allocations, blocking calls, complexity hotspots. Cite file:line.
- **convention-reviewer:** naming, layering, DTO boundaries, project conventions (align to the repo's CLAUDE.md / AGENTS.md). Cite file:line.
- **test-coverage-reviewer:** untested branches/paths the diff introduces; propose the missing test cases.
- **verifier (adversarial):** For EACH finding, try to REFUTE it. Confirm only when the failing input/state is concrete and real. Default to "not a real issue" when unsure.

## Flow (Queen)
1. Scope the diff (`git diff`); if huge, split by file/module.
2. Spawn the 5 dimension reviewers in PARALLEL on the same diff (read-only).
3. Collect findings; dedup by (file, line, claim).
4. Send each surviving finding to the verifier. Drop the refuted ones.
5. Queen ranks confirmed findings by severity, groups by file:line, and reports. No code edits unless the user asks.

## Notes
- Map lenses to the repo's existing reviewer skills where available (e.g. spring-boot-reviewer, react-typescript-reviewer, security-reviewer, design-pattern-advisor).
- The verifier is what makes this better than N parallel reviewers: it removes plausible-but-wrong findings.
- Small diff (a few lines)? One reviewer pass is enough; skip the fleet.
