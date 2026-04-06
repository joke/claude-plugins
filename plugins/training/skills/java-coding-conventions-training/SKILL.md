---
name: java-coding-conventions-training
description: >
  Training skill that generates and validates the java-coding-conventions skill.
  Run this skill to regenerate the conventions from reference material and verify
  them against test cases. Use when updating or re-tuning general Java coding conventions.
user-invocable: true
model: haiku-4.5
---

# Java Coding Conventions Training

This skill regenerates the `java-coding-conventions` skill from reference material and validates it against test cases.

## What it produces

A SKILL.md at `plugins/conventions/skills/java-coding-conventions/SKILL.md` that teaches Claude to write and review Java code following immutable, clean-design conventions — independent of any specific Java version.

## Step 1: Regenerate the skill

Read `references/conventions.md` for the full set of conventions. Then write the output skill:

1. **Output path:** `plugins/conventions/skills/java-coding-conventions/SKILL.md`
2. **Frontmatter:** name `java-coding-conventions`, `user-invocable: false`, `model: haiku-4.5`
3. **Scope:** Version-agnostic Java. No version-specific features or APIs. The skill should work equally well whether the target is Java 8 or Java 25.
4. **Tone:** Explain *why* each convention matters, not just what to do. Use before/after examples. Imperative form.
5. **Length:** Under 500 lines. Dense and practical — no filler.
6. **Structure:** Group by theme: variables/parameters, immutability, small methods, exceptions, design, imports, naming.

Key things the skill must make very clear:
- **Every** variable and parameter is `final` — this is the single most important convention
- Direct constructor with all fields, not Builder pattern
- Constructor injection — no field injection, no setter injection
- No setters ever — immutable by default
- Extract complex logic into named private methods
- Most restrictive visibility

## Step 2: Validate with test cases

After regenerating, validate the skill using the test cases in `evals/evals.json`.

For each test case, spawn a subagent that:
1. Reads the generated skill from `plugins/conventions/skills/java-coding-conventions/SKILL.md`
2. Reads any input files specified in the test case
3. Completes the task described in the prompt, following the skill's conventions
4. Writes output Java files to a workspace directory

Then run the shared grading script against the outputs:

```bash
cd plugins/training
python -m shared.grade <workspace-dir>
```

The script checks:
- All variables and parameters use `final`
- No checked exceptions
- Immutable fields (`private final`)
- Small methods (under ~20 lines)
- No setters
- Constructor sets all fields
- Constructor injection

### Expected results

All assertions should pass for all test cases. If any fail, the conventions in the skill need strengthening in that area.

### Test cases

The test cases in `evals/evals.json` cover:
1. **Refactor PaymentProcessor** — setter injection, mutable state, checked exceptions, long methods
2. **Refactor NotificationConfig** — mutable JavaBean with getters/setters, exposed mutable collections
3. **Greenfield TaskScheduler** — write a new class from scratch following all general conventions

Input files for refactoring tests are in `evals/files/`.

## Conventions reference

The authoritative conventions are in `references/conventions.md`. Always read that file when regenerating — it is the single source of truth for what rules to include.
