---
name: skill-creator
description: Scaffold a new agent skill (SKILL.md) from a described capability. Use when the user wants to create a new skill, package a repeatable workflow, or turn project conventions into a reusable skill.
---

# Skill Creator

Create a well-formed SKILL.md for the capability the user describes.

## Steps
1. Clarify the skill's single purpose and its trigger conditions (when should the agent use it?).
2. Choose a name: lowercase, hyphenated, matching ^[a-z0-9]+(-[a-z0-9]+)*$.
3. Write a description that states BOTH what the skill does AND when to use it — the agent selects skills by description, so include trigger phrases.
4. Write concise, imperative instructions: numbered steps, rules, and the expected output.
5. Keep SKILL.md focused; move long reference material into separate files under the skill folder and link them.

## Output
Produce the folder layout and the full SKILL.md, ready to paste. Remind the user of install locations:
- opencode / Claude Code (project): .claude/skills/<name>/SKILL.md  (or .opencode/skills/<name>/SKILL.md)
- Global: ~/.claude/skills/<name>/SKILL.md  (or ~/.config/opencode/skills/<name>/SKILL.md)

## Validate before finishing
- File is named SKILL.md (uppercase), frontmatter has valid name + description, and the name is unique across existing skills.
