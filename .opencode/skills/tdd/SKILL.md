---
name: tdd
description: Write code test-first using red-green-refactor. Use when implementing a new feature or fixing a bug with tests, or when adding test coverage to existing code.
---

# Test-Driven Development

## Red-Green-Refactor
1. Red: write the smallest failing test that describes the next bit of desired behavior. Run it and confirm it fails for the expected reason.
2. Green: write the minimum code to make the test pass. Nothing more.
3. Refactor: clean up code and tests while keeping them green.
4. Repeat for the next behavior.

## Coverage guidance
- Cover the happy path, boundary/edge cases (empty, null, max, off-by-one), and failure paths (invalid input, errors).
- Prefer fast unit tests; add integration/E2E tests for cross-boundary behavior (DB, HTTP, filesystem).
- Aim for meaningful coverage of new or changed code, not a blanket percentage.

## Rules
- Detect and match the project's existing test framework and conventions before writing.
- One behavior per test; name each test by the behavior it asserts.
- Never delete or weaken a test just to make it pass.
