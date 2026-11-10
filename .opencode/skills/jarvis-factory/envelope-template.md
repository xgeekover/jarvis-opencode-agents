# Delegation prompt template

Fill the `<…>` parts and pass the result as the `task` tool prompt (subagent `jarvis-<role>`). Save a copy as `.jarvis/tasks/<TASK_ID>/envelope-<role>-c<N>.md`, so the human can also run it by mention: `@jarvis-<role> Read .jarvis/tasks/<TASK_ID>/envelope-<role>-c<N>.md and follow it.`

````markdown
You are the Jarvis <ROLE> for task <TASK_ID>. Follow your agent definition strictly.

## Task envelope
```json
{
  "task_id": "<TASK_ID>",
  "project_id": "<PROJECT_ID>",
  "role": "<planner|developer|tester|reviewer|integrator>",
  "stage": "<CURRENT STAGE>",
  "objective": "<what this agent must achieve — for the planner: the request verbatim>",
  "attempt": <retry_count>,
  "workdir": "<ABSOLUTE path of the task worktree, or null for the planner>",
  "base_ref": "<base commit sha from task.md>",
  "acceptance_criteria": ["<copied from requirements.json>"],
  "constraints": [
    "Work only inside workdir; use absolute paths and `git -C <workdir>`.",
    "Do not commit, push, merge, reset, delete branches or remove worktrees.",
    "Do not edit .jarvis/tasks/, opencode.json, .opencode/ or AGENTS.md.",
    "<task-specific constraints, e.g. 'do not add dependencies', sibling task boundaries>"
  ],
  "context_files": ["<files the agent should read first>"],
  "artifacts": {
    "requirements": ".jarvis/tasks/<TASK_ID>/requirements.json",
    "plan": ".jarvis/tasks/<TASK_ID>/plan.json",
    "development": ".jarvis/tasks/<TASK_ID>/development-c<N>.json",
    "testing": ".jarvis/tasks/<TASK_ID>/testing-c<N>.json",
    "review": ".jarvis/tasks/<TASK_ID>/review-c<N>.json"
  },
  "previous_failures": [
    {"stage": "<TESTING|CODE_REVIEW|…>", "reason": "<from task.md>", "details": "<defects / findings / failing gates to fix>"}
  ],
  "commands": {"build": "<…>", "test": "<…>", "lint": "<…>", "integration_test": "<… or null>"}
}
```

## Notes from the Queen
<anything specific: risky areas, what the previous attempt got wrong, what NOT to change>

## Output
End your final message with exactly one ```json block that matches <role>-output.schema.json from the jarvis-factory skill (task_id must be "<TASK_ID>"). It is saved verbatim — invalid or incomplete JSON is sent back to you.
````
