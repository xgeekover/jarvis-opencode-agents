---
name: prompt-engineer
description: Turn a rough request or instruction into a structured, production-ready prompt. Use when building LLM features, designing system/agent prompts, or when a prompt gives inconsistent results.
---

# Prompt Engineer

Transform the user's rough intent into a clear, robust prompt.

## Structure to produce
1. Role/context: who the model is and the situation.
2. Task: the single objective, stated unambiguously.
3. Inputs: what variables/context will be provided, and their format.
4. Constraints: hard rules, tone, and what NOT to do.
5. Output format: the exact shape (JSON schema, sections, length). Give an example if format matters.
6. Edge cases: how to handle missing, ambiguous, or invalid input.

## Techniques to apply when relevant
- Prefer explicit instructions over vague adjectives ("return 3 bullet points" beats "be concise").
- Add few-shot examples for format-sensitive tasks.
- For reasoning tasks, ask for step-by-step before the final answer; for extraction, ask for the answer directly.
- Remove ambiguity: define terms, specify units, state defaults.

## Output
Return the finished prompt in a code block, plus a short note on what you changed and why.
