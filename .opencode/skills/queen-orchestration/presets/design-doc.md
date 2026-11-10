# Preset: Design Document (English)

Queen-worker roster for producing an English technical design document from a Korean brief. Tuned for a possibly-weaker in-house LLM: heavy on template + glossary, and separated draft/edit passes.

## Workers
- **outliner (architect):** Turn the brief into a standard section outline — Overview / Goals & Non-Goals / Architecture / API / Data Model / Sequence & Flows / Trade-offs & Alternatives / Risks / Rollout. Output the outline + a one-line intent per section. Read-only.
- **section-writer (×N, one per section, parallel):** Write the English draft for ONE assigned section only, following the template and the glossary. Rules: clear US technical English, active voice, short sentences, no invented facts. Return the section markdown only.
- **terminology-checker:** Enforce the Korean→English glossary across a draft. Flag every term rendered inconsistently or off-glossary with a suggested fix. Read-only.
- **english-editor:** Proofread a section for grammar, tone, and clarity (US technical English). Do NOT change technical meaning. Return the edited section + a short list of changes. Read-only.
- **consistency-reviewer:** Read the FULL assembled doc. Flag cross-section contradictions, duplicated content, terminology drift, and gaps vs the outline. Read-only.

## Flow (Queen)
1. Confirm scope + audience + which glossary/template to use. If missing, ask before spawning.
2. outliner → section outline. Show it to the user for approval (plan gate).
3. Spawn section-writers in PARALLEL (one per section; disjoint output).
4. Per section: terminology-checker + english-editor (parallel). Apply fixes.
5. Assemble the full doc → consistency-reviewer (whole-doc pass). Apply fixes.
6. Queen integrates into the final document; list any unresolved TODOs.

## Notes
- Keep draft and edit as SEPARATE passes — weaker models are more stable that way.
- Glossary + template are the biggest quality levers; put them in a shared file every worker reads.
- Small doc (1–2 sections)? Skip the fleet and write it directly.
