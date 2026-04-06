---
name: java25-coding-conventions-training
description: >
  Training skill that generates and validates the java25-coding-conventions skill.
  Run this skill to regenerate the conventions from reference material and verify
  them against test cases. Use when updating or re-tuning Java 25 coding conventions.
user-invocable: true
model: haiku-4.5
---

# Java 25 Coding Conventions Training

This skill regenerates the `java25-coding-conventions` skill from reference material and validates it against test cases.

## What it produces

A SKILL.md at `plugins/conventions/skills/java25-coding-conventions/SKILL.md` that teaches Claude to write and review modern Java 25 code. This skill layers Java 25-specific conventions on top of the general `java-coding-conventions` skill.

## Step 1: Regenerate the skill

Read `references/conventions.md` for the Java 25-specific conventions. Then write the output skill:

1. **Output path:** `plugins/conventions/skills/java25-coding-conventions/SKILL.md`
2. **Frontmatter:** name `java25-coding-conventions`, `user-invocable: false`, `model: haiku-4.5`
3. **Scope:** Modern Java (up to Java 25). The skill must reference `plugins/conventions/skills/java-coding-conventions/SKILL.md` for general conventions and only add Java 25-specific guidance.
4. **Tone:** Explain *why* each convention matters, not just what to do. Use before/after examples. Imperative form.
5. **Length:** Under 500 lines. Dense and practical — no filler.
6. **Structure:** Start with inclusion of general skill, then: records, sealed classes, pattern matching (instanceof + switch), switch expressions, text blocks, var, modern collections, modern stream/Optional operations.

Key things the skill must make very clear:
- Records for all data-carrying classes (not manual immutable classes)
- Sealed interfaces for closed type hierarchies
- Switch expressions with pattern matching for type dispatch
- `List.copyOf` / `List.of` instead of `Collections.unmodifiable*`
- `final var` (never bare `var`)
- `Stream.toList()` instead of `Collectors.toList()`
- Text blocks for multi-line strings

## Step 2: Validate with test cases

After regenerating, validate the skill using the test cases in `evals/evals.json`.

For each test case, spawn a subagent that:
1. Reads the general skill from `plugins/conventions/skills/java-coding-conventions/SKILL.md`
2. Reads the generated Java 25 skill from `plugins/conventions/skills/java25-coding-conventions/SKILL.md`
3. Reads any input files specified in the test case
4. Completes the task described in the prompt, following both skills' conventions
5. Writes output Java files to a workspace directory

Then run the shared grading script against the outputs:

```bash
cd plugins/training
python -m shared.grade <workspace-dir>
```

The script checks Java 25-specific assertions:
- Uses records for data classes
- Uses sealed interfaces for type hierarchies
- Uses pattern matching (not instanceof + cast)
- Uses switch expressions with arrows
- Uses modern collection factories (List.of, List.copyOf)
- No outdated Java 8 patterns (Collections.unmodifiable*, Collectors.toList)
- Uses final var where appropriate

Plus general assertions (final vars, immutable fields, small methods, etc.).

### Expected results

All assertions should pass for all test cases. If any fail, the conventions in the skill need strengthening in that area.

### Test cases

The test cases in `evals/evals.json` cover:
1. **Refactor ShapeCalculator** — old-style instanceof, abstract hierarchy, manual string building, old collections
2. **Refactor ApiResponse** — manually-written immutable class, string concatenation, old collections, if-else chains
3. **Greenfield Event Processing** — sealed interface with record subtypes, pattern matching, streams

Input files for refactoring tests are in `evals/files/`.

## Conventions reference

The authoritative conventions are in `references/conventions.md`. Always read that file when regenerating — it is the single source of truth for what Java 25-specific rules to include.
