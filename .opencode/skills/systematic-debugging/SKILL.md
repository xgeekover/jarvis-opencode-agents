---
name: systematic-debugging
description: Debug using the scientific method instead of guessing. Use when investigating a crash, failing test, incorrect output, or intermittent/hard-to-reproduce issue — especially when initial fixes have not worked.
---

# Systematic Debugging

Do NOT try random fixes. Follow this loop until the root cause is proven.

## Loop
1. Reproduce: establish a reliable, minimal reproduction. If you cannot reproduce it, gather more evidence first (logs, inputs, environment).
2. Observe: collect concrete evidence — error message, stack trace, actual vs expected values, and recent changes (`git log` / `git blame` on the failing area).
3. Hypothesize: state ONE specific, falsifiable hypothesis about the root cause. Write it down.
4. Test the hypothesis: design the smallest experiment (a log line, breakpoint, unit test, or `git bisect`) that would confirm or refute it. Run it.
5. Decide: if refuted, discard and form the next hypothesis (back to 3). If confirmed, you have the root cause.
6. Fix and verify: fix the root cause (not the symptom), re-run the reproduction to confirm it is gone, and add a regression test.

## Rules
- Change ONE variable at a time.
- Never claim a fix works without re-running the reproduction.
- Distinguish symptom from cause. If the fix is "add a null check", ask why it was null.
