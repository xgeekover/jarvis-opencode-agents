---
name: design-pattern-advisor
description: Recommend an appropriate GoF design pattern for a described problem, or review existing code for pattern misuse, missing patterns, and over-engineering. Use when designing new functionality with a recurring structural problem (branching logic, object creation sprawl, tangled notifications), or when reviewing code that feels overly complex or suspiciously pattern-heavy.
---

# Design Pattern Advisor

Match code smells to GoF patterns — and just as importantly, flag pattern overuse.

## When recommending a pattern
1. Identify the concrete symptom, not the pattern name first:
   - Growing if/switch branching on type or behavior → Strategy
   - Object creation logic scattered or conditional → Factory Method
   - One shared instance needed app-wide → Singleton (or just use the framework's DI container — see below)
   - One change must notify several unrelated parts → Observer
   - Incompatible interface from a library/legacy code → Adapter
   - A controller/service coordinates too many subsystems → Facade
   - Need to add optional behavior in any combination without subclass explosion → Decorator
   - Many optional fields make constructors unreadable → Builder
   - Need to intercept calls transparently (logging, caching, tx) → Proxy
   - Individual items and groups of items must be treated identically → Composite
   - Need to queue, log, or undo an action → Command
   - Need to traverse a collection without exposing its internals → Iterator
   - Behavior legitimately changes based on object state → State
   - Multiple candidate handlers, only one (or a chain) should act → Chain of Responsibility
   - Fixed algorithm skeleton with swappable steps → Template Method
2. Propose the pattern with a short code sketch in the project's language, and name the concrete smell it fixes.
3. If the codebase's framework already provides this, point to the framework feature instead of hand-rolling the pattern.

## When reviewing existing code
1. Check for missing patterns: repeated type-checking branches, constructors with 5+ parameters, duplicated notification/callback wiring.
2. Check for overuse/over-engineering with equal weight: unnecessary pattern for 2-3 branches, hand-rolled Singleton/Factory/Proxy where DI already provides it, Builder for small rarely-changing objects, single-implementation abstractions.
3. For each finding: pattern name (or lack of it), symptom, file:line, fix.

## Output
List findings grouped as "Missing pattern opportunities" and "Over-engineering / unnecessary indirection." If code is already well-fitted, say so.
