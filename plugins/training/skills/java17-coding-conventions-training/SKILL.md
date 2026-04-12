---
name: java17-coding-conventions-training
description: >
  Training skill that generates and validates the java17-coding-conventions skill.
  Run this skill to regenerate the conventions from reference material and verify
  them against test cases. Use when updating or re-tuning Java 17 coding conventions.
user-invocable: true
---

# Java 17 Coding Conventions Training

This skill regenerates the `java17-coding-conventions` skill from reference material and validates it against test cases.

## What it produces

A SKILL.md at `plugins/conventions/skills/java17-coding-conventions/SKILL.md` that teaches Claude to write and review Java 17 code. This skill layers Java 17-specific conventions on top of the general `java-coding-conventions` skill.

## Step 1: Regenerate the skill

Read `references/conventions.md` for the Java 17-specific conventions. Then write the output skill:

1. **Output path:** `plugins/conventions/skills/java17-coding-conventions/SKILL.md`
2. **Frontmatter:** name `java17-coding-conventions`, `user-invocable: false`, `model: haiku-4.5`
3. **Scope:** Java 17 (LTS). Features from Java 12 through 17 are allowed and preferred over older equivalents. Features from Java 18+ must not appear. The skill must reference `plugins/conventions/skills/java-coding-conventions/SKILL.md` for general conventions and only add Java 17-specific guidance.
4. **Tone:** Explain *why* each convention matters. Use before/after examples. Imperative form.
5. **Length:** Under 500 lines. Dense and practical.
6. **Structure:** Start with inclusion of general skill, then: version boundary, `var`, records, sealed types, pattern matching for `instanceof`, switch expressions with `->`, text blocks, immutable collections + `Stream.toList()`, stream/Optional additions, helpful NPEs, new String methods, Files/HTTP, java.time.

Key things the skill must make very clear:
- Prefer **records** for pure data carriers; use the compact constructor for validation and `List.copyOf` defensive copies
- Use **sealed** interfaces/classes for closed hierarchies; permitted subtypes must be `final`, `sealed`, or `non-sealed`
- Use **`instanceof` pattern matching** with a `final` pattern variable instead of cast-after-check
- Use **switch expressions** with `->`; never use the old `case X:` + `break` form
- Pattern matching for `switch` is **NOT** in Java 17 — it's preview there, stable in 21
- Use **text blocks** (`"""`) for multi-line strings instead of concatenation with `\n`
- Prefer **`Stream.toList()`** over `Collectors.toUnmodifiableList()` / `Collectors.toList()`
- Use `final var` for locals when the type is obvious
- No pattern matching for `switch`, record patterns, virtual threads, or sequenced collections (all Java 21)

## Step 2: Validate with test cases

After regenerating, validate the skill using the test cases in `evals/evals.json`.

For each test case, spawn a subagent that:
1. Reads the general skill from `plugins/conventions/skills/java-coding-conventions/SKILL.md`
2. Reads the generated Java 17 skill from `plugins/conventions/skills/java17-coding-conventions/SKILL.md`
3. Reads any input files specified in the test case
4. Completes the task described in the prompt, following both skills' conventions
5. Writes output Java files to a workspace directory

Then run the shared grading script against the outputs:

```bash
cd plugins/training
python -m shared.grade <workspace-dir>
```

The script checks Java 17-specific assertions:
- `no-post-java17-features` — no pattern matching for `switch`, record patterns, virtual threads, sequenced collections
- `uses-records` — data carriers should be records
- `uses-pattern-matching` — `instanceof` should use pattern matching with final pattern variables
- `uses-switch-expressions` — switch uses arrow form
- `uses-text-blocks` — multi-line strings use `"""`
- `modern-collections` — `Stream.toList()` / `List.of` / `List.copyOf`

Plus general assertions (immutable fields, small methods, streams over loops, etc.).

### Test cases

1. **Refactor OrderService** — mutable state, loops, checked exceptions, null returns, string concatenation for report
2. **Refactor UserProfile** — mutable JavaBean with getters/setters; should become a record
3. **Greenfield PaymentProcessing** — write a sealed `PaymentResult` hierarchy with a dispatcher that uses pattern matching

Input files for refactoring tests are in `evals/files/`.

## Conventions reference

The authoritative conventions are in `references/conventions.md`.
