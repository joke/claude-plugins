---
name: java8-coding-conventions-training
description: >
  Training skill that generates and validates the java8-coding-conventions skill.
  Run this skill to regenerate the conventions from reference material and verify
  them against test cases. Use when updating or re-tuning Java 8 coding conventions.
user-invocable: true
---

# Java 8 Coding Conventions Training

This skill regenerates the `java8-coding-conventions` skill from reference material and validates it against test cases.

## What it produces

A SKILL.md at `plugins/conventions/skills/java8-coding-conventions/SKILL.md` that teaches Claude to write and review Java 8 code. This skill layers Java 8-specific conventions on top of the general `java-coding-conventions` skill.

## Step 1: Regenerate the skill

Read `references/conventions.md` for the Java 8-specific conventions. Then write the output skill:

1. **Output path:** `plugins/conventions/skills/java8-coding-conventions/SKILL.md`
2. **Frontmatter:** name `java8-coding-conventions`, `user-invocable: false`, `model: haiku-4.5`
3. **Scope:** Java 8 only. No features from Java 9+. The skill must reference `plugins/conventions/skills/java-coding-conventions/SKILL.md` for general conventions and only add Java 8-specific guidance.
4. **Tone:** Explain *why* each convention matters, not just what to do. Use before/after examples. Imperative form.
5. **Length:** Under 500 lines. Dense and practical — no filler.
6. **Structure:** Start with inclusion of general skill, then: version boundary, immutable collections (Java 8 style), streams over loops, Optional, functional interfaces, java.time.

Key things the skill must make very clear (these are the conventions models don't follow without explicit instruction):
- `Collections.unmodifiableList(new ArrayList<>(input))` for defensive copy + unmodifiable (not `List.of`)
- Extract complex predicates/mappers into named private methods rather than multi-line inline lambdas
- Method references (`Customer::isActive`) over lambdas (`c -> c.isActive()`) when the lambda just delegates
- `Collectors.toList()` not `Stream.toList()`
- No Java 9+ features

## Step 2: Validate with test cases

After regenerating, validate the skill using the test cases in `evals/evals.json`.

For each test case, spawn a subagent that:
1. Reads the general skill from `plugins/conventions/skills/java-coding-conventions/SKILL.md`
2. Reads the generated Java 8 skill from `plugins/conventions/skills/java8-coding-conventions/SKILL.md`
3. Reads any input files specified in the test case
4. Completes the task described in the prompt, following both skills' conventions
5. Writes output Java files to a workspace directory

Then run the shared grading script against the outputs:

```bash
cd plugins/training
python -m shared.grade <workspace-dir>
```

The script checks Java 8-specific assertions:
- Streams over loops (no for/while)
- Optional for find methods
- No Java 9+ features
- Unmodifiable collections (Java 8 style)

Plus general assertions (final vars, immutable fields, small methods, etc.) to verify the general skill inclusion works correctly.

### Expected results

All assertions should pass for all test cases. If any fail, the conventions in the skill need strengthening in that area.

### Test cases

The test cases in `evals/evals.json` cover:
1. **Refactor OrderService** — mutable state, loops, checked exceptions, null returns, long methods
2. **Refactor UserProfile** — mutable JavaBean with getters/setters, imperative collection code
3. **Greenfield InventoryService** — write a new service class from scratch

Input files for refactoring tests are in `evals/files/`.

## Conventions reference

The authoritative conventions are in `references/conventions.md`. Always read that file when regenerating — it is the single source of truth for what Java 8-specific rules to include.
