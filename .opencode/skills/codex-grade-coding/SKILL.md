---
name: codex-grade-coding
description: Apply production-grade engineering standards while writing or generating new code. Use whenever implementing non-trivial features so the first draft is production-ready, not a prototype.
---

# Production-Grade Coding

Hold generated code to production standards from the first draft.

## Standards
- Match the codebase: detect and follow existing patterns, naming, formatting, and libraries. Read neighboring files before writing.
- Errors: handle failure paths explicitly. No silently swallowed exceptions; fail loudly with actionable messages.
- Inputs: validate external input at boundaries. Never trust user/network/file input.
- Types and contracts: use the project's typing; make function contracts explicit; avoid untyped escapes like `any`.
- Naming: intention-revealing names; no `data`, `tmp`, `foo` in shipped code.
- Size: small, single-responsibility functions; avoid deep nesting (prefer early returns).
- No dead code: no commented-out blocks, unused variables, or leftover TODO stubs.
- Security and secrets: never hardcode secrets; do not log sensitive data.
- Tests: add or update tests for the new behavior.

## Before finishing
Self-review the diff against this list and fix anything that would not pass a senior review.
