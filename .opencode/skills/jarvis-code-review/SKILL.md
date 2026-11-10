---
name: jarvis-code-review
description: Jarvis Dev Factory code-review stage - dispatch a fresh read-only jarvis-reviewer on a task's git diff (code, security and architecture review), save its verdict as the task's review artifact, and move the task forward or back. Use when a Jarvis task is in CODE_REVIEW, or for an ad-hoc review of a worktree or branch.
license: MIT
---

# jarvis-code-review

**Entry points:** `/jarvis-review <TASK-ID>` (task in CODE_REVIEW) or `/jarvis-review <path-or-branch>` (ad-hoc: nothing is saved, report the verdict only).

## For a task in CODE_REVIEW
1. Read `.jarvis/tasks/<TASK-ID>/task.md`: status must be `CODE_REVIEW`. Collect `workdir`, `base_ref`, the cycle, the artifact paths, earlier failures and the acceptance criteria from `requirements.json`.
2. Delegate to **`jarvis-reviewer`**: a fresh subagent that has not seen the development conversation. Build the prompt from the envelope template with `role: "reviewer"`, `stage: "CODE_REVIEW"`, and include:
   - the scope: `git -C <workdir> diff <base_ref>` plus untracked files;
   - the developer and tester artifact paths, so claims can be checked against the diff;
   - on a retry, the previous review findings, so it verifies each one was fixed;
   - for large or high-risk diffs (authentication, data model, concurrency), optionally a second reviewer with a different focus — A: data, contracts and security; B: requirements, tests and architecture. Run them one after the other (never two agents in one worktree at the same time).
3. Save the JSON exactly as returned as `review-c<N>.json`. Reject (send back) an incomplete review, e.g. an empty `scope.files_reviewed`.
4. Decide:
   - `APPROVE` with security `PASS` and no critical or high findings → `INTEGRATION`.
   - `REQUEST_CHANGES` → record a CODE_REVIEW failure listing the finding ids; the findings go into the next developer envelope's `previous_failures`.
   - `BLOCK` → record the failure the same way and tell the human: it usually needs a re-plan or a human decision.
5. Tell the human the verdict, the finding counts by severity and the top issues.

## Rules
- The reviewer is read-only. Do not "quickly fix" findings yourself during review; fixes go through DEVELOPMENT.
- Never downgrade or drop a finding without reading the code yourself and writing why in the next envelope.
- Low or info findings do not block. If the human wants them fixed before delivery, record a failure with those ids so they go through DEVELOPMENT like any other change.
