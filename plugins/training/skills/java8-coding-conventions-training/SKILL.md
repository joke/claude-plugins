---
name: java8-coding-conventions-training
description: >
  Training skill that generates and validates the java8-coding-conventions skill.
  Run this skill to regenerate the conventions from reference material and verify
  them against test cases. Use when updating or re-tuning Java 8 coding conventions.
user-invocable: true
model: haiku-4.5
---

# Java 8 Coding Conventions Training

This skill regenerates the `java8-coding-conventions` skill from reference material and validates it against test cases.

## What it produces

A SKILL.md at `plugins/conventions/skills/java8-coding-conventions/SKILL.md` that teaches Claude to write and review Java 8 code following functional, immutable conventions.

## Step 1: Regenerate the skill

Read `references/conventions.md` for the full set of conventions. Then write the output skill:

1. **Output path:** `plugins/conventions/skills/java8-coding-conventions/SKILL.md`
2. **Frontmatter:** name `java8-coding-conventions`, `user-invocable: false`, `model: haiku-4.5`
3. **Scope:** Java 8 only. No features from Java 9+ (`var`, records, sealed classes, `List.of`, `Map.of`, modules, text blocks).
4. **Tone:** Explain *why* each convention matters, not just what to do. Use before/after examples. Imperative form.
5. **Length:** Under 500 lines. Dense and practical — no filler.
6. **Structure:** Group by theme: variables/parameters, immutability, functional style & streams, Optional, small methods, functional interfaces, exceptions, design, java.time, imports, naming.

Key things the skill must make very clear (these are the conventions models don't follow without explicit instruction):
- **Every** variable and parameter is `final` — this is the single most important convention
- Direct constructor with all fields, not Builder pattern
- `Collections.unmodifiableList(new ArrayList<>(input))` for defensive copy + unmodifiable (not `List.of`)
- Extract complex predicates/mappers into named private methods rather than multi-line inline lambdas
- Method references (`Customer::isActive`) over lambdas (`c -> c.isActive()`) when the lambda just delegates

## Step 2: Validate with test cases

After regenerating, validate the skill using the test cases in `evals/evals.json`.

For each test case, spawn a subagent that:
1. Reads the generated skill from `plugins/conventions/skills/java8-coding-conventions/SKILL.md`
2. Reads any input files specified in the test case
3. Completes the task described in the prompt, following the skill's conventions
4. Writes output Java files to a workspace directory

Then run the grading script `scripts/grade.py` against the outputs. The script checks:
- All variables and parameters use `final`
- No checked exceptions
- Streams over loops (no for/while)
- Optional for find methods
- Immutable fields (`private final`)
- Small methods (under ~15 lines)
- No Java 9+ features
- No setters
- Constructor sets all fields
- Unmodifiable collection returns
- Constructor injection

### Expected results

All assertions should pass for all test cases. If any fail, the conventions in the skill need strengthening in that area.

### Test cases

The test cases in `evals/evals.json` cover:
1. **Refactor OrderService** — mutable state, loops, checked exceptions, null returns, long methods
2. **Refactor UserProfile** — mutable JavaBean with getters/setters, imperative collection code
3. **Greenfield InventoryService** — write a new service class from scratch

Input files for refactoring tests are in `evals/files/`.

## Conventions reference

The authoritative conventions are in `references/conventions.md`. Always read that file when regenerating — it is the single source of truth for what rules to include.
