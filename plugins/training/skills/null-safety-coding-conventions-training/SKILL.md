---
name: null-safety-coding-conventions-training
description: >
  Training skill that generates and validates the null-safety-coding-conventions skill.
  Run this skill to regenerate the conventions from reference material and verify
  them against test cases. Use when updating or re-tuning null safety conventions.
user-invocable: true
---

# Null Safety Coding Conventions Training

This skill regenerates the `null-safety-coding-conventions` skill from reference material and validates it against test cases.

## What it produces

A SKILL.md at `plugins/conventions/skills/null-safety-coding-conventions/SKILL.md` that teaches Claude to write null-safe Java code using NullAway and JSpecify annotations.

## Step 1: Regenerate the skill

Read `references/conventions.md` for the full set of conventions. Then write the output skill:

1. **Output path:** `plugins/conventions/skills/null-safety-coding-conventions/SKILL.md`
2. **Frontmatter:** name `null-safety-coding-conventions`, `user-invocable: false`, `model: haiku-4.5`
3. **Scope:** Null safety with NullAway + JSpecify. Version-agnostic — works with any Java version.
4. **Tone:** Explain *why* each convention matters. Use before/after examples. Imperative form.
5. **Length:** Under 500 lines. Dense and practical.
6. **Structure:** Never suppress NullAway, package-info.java with @NullMarked, @Nullable annotations, null-safe handling patterns, import rules.

Key things the skill must make very clear:
- **Never** use `@SuppressWarnings("NullAway")` — this is the single most important rule
- Every package needs `package-info.java` with `@NullMarked`
- Only use `org.jspecify.annotations.Nullable` — not javax, jetbrains, findbugs, etc.
- `@NonNull` is redundant under `@NullMarked` — don't use it
- Every nullable access must be guarded

## Step 2: Validate with test cases

After regenerating, validate the skill using the test cases in `evals/evals.json`.

For each test case, spawn a subagent that:
1. Reads the generated skill from `plugins/conventions/skills/null-safety-coding-conventions/SKILL.md`
2. Reads any input files specified in the test case
3. Completes the task described in the prompt, following the skill's conventions
4. Writes output Java files to a workspace directory

Then run the shared grading script against the outputs:

```bash
cd plugins/training
python -m shared.grade <workspace-dir>
```

The script checks:
- No @SuppressWarnings("NullAway")
- @NullMarked in package-info.java
- @Nullable from JSpecify on nullable references
- Null-safe handling of nullable values
- No redundant @NonNull

### Test cases

1. **Refactor UserService** — has @SuppressWarnings("NullAway"), no package-info.java, unsafe null handling
2. **Refactor ProductCatalog** — uses wrong @Nullable import (javax.annotation), missing package-info.java, returns null
3. **Greenfield NotificationDispatcher** — new class with nullable fields, needs full null-safety setup

Input files for refactoring tests are in `evals/files/`.

## Conventions reference

The authoritative conventions are in `references/conventions.md`.
