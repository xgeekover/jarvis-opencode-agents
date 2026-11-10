---
name: env-doctor
description: Diagnose and fix a broken local development environment — failing installs, build errors, version mismatches, missing dependencies, misconfigured tooling. Use when setup/build/run commands fail with environment errors.
---

# Environment Doctor

Diagnose the broken environment methodically, then fix it.

## Steps
1. Read the error: capture the exact failing command and full error output. Do not guess from the summary.
2. Identify the layer: language runtime/version, package manager, dependencies/lockfile, system libraries, env vars, or tool config.
3. Check versions: compare installed versions against what the project requires (`.nvmrc`, `.tool-versions`, `engines`, `pyproject.toml`, `go.mod`, Dockerfile, README).
4. Inspect config: env files, PATH, virtualenv/SDK activation, credentials.
5. Form the smallest fix: e.g. switch runtime version, reinstall from lockfile, install a missing system lib, set a missing env var.
6. Apply and verify: run the originally failing command again to confirm it now works.

## Rules
- Prefer reproducible fixes (pin versions, use the lockfile) over ad-hoc installs.
- Explain the root cause, not just the fix, so it does not recur.
- Never delete lockfiles or wipe node_modules/caches wholesale unless you have confirmed that is the actual cause.
