---
name: java21-coding-conventions-training
description: >
  Training skill that generates and validates the java21-coding-conventions skill.
  Run this skill to regenerate the conventions from reference material and verify
  them against test cases. Use when updating or re-tuning Java 21 coding conventions.
user-invocable: true
---

# Java 21 Coding Conventions Training

This skill regenerates the `java21-coding-conventions` skill from reference material and validates it against test cases.

## What it produces

A SKILL.md at `plugins/conventions/skills/java21-coding-conventions/SKILL.md` that teaches Claude to write and review Java 21 code. This skill layers Java 21-specific conventions on top of the general `java-coding-conventions` skill.

## Step 1: Regenerate the skill

Read `references/conventions.md` for the Java 21-specific conventions. Then write the output skill:

1. **Output path:** `plugins/conventions/skills/java21-coding-conventions/SKILL.md`
2. **Frontmatter:** name `java21-coding-conventions`, `user-invocable: false`, `model: haiku-4.5`
3. **Scope:** Java 21 (LTS). Features from Java 12 through 21 are allowed. Features from Java 22+ (including preview-only features such as string templates, unnamed patterns, flexible constructor bodies) must not appear. The skill must reference the general conventions skill.
4. **Tone:** Explain *why* each convention matters. Use before/after examples. Imperative form.
5. **Length:** Under 500 lines.
6. **Structure:** Version boundary, `var`, records + sealed, pattern matching for `switch`, record patterns, virtual threads, sequenced collections, streams/Optional, text blocks, helpful NPEs, java.time.

Key things the skill must make very clear:
- Use **pattern matching for `switch`** over sealed types; rely on exhaustiveness instead of `default`
- Use **record patterns** to destructure records; compose them with switch pattern matching
- Use **virtual threads** (`Executors.newVirtualThreadPerTaskExecutor`, `Thread.ofVirtual`) for blocking IO; one per task, never pooled
- Use **sequenced collection** methods (`getFirst`/`getLast`/`reversed`) instead of `list.get(0)` and `Collections.reverse`
- Pattern variables are always `final`
- No string templates (`STR."..."`), unnamed patterns, or Java 22+ features

## Step 2: Validate with test cases

After regenerating, validate the skill using the test cases in `evals/evals.json`.

For each test case, spawn a subagent that:
1. Reads the general skill from `plugins/conventions/skills/java-coding-conventions/SKILL.md`
2. Reads the generated Java 21 skill from `plugins/conventions/skills/java21-coding-conventions/SKILL.md`
3. Reads any input files specified
4. Completes the task following both skills
5. Writes output Java files to a workspace directory

Then run the shared grading script:

```bash
cd plugins/training
python -m shared.grade <workspace-dir>
```

The script checks Java 21-specific assertions:
- `no-post-java21-features` — no string templates, unnamed patterns, flexible constructor bodies
- `uses-records`, `uses-sealed`, `uses-pattern-matching`, `uses-switch-expressions`, `uses-text-blocks`, `modern-collections`

Plus general assertions (immutable fields, small methods, streams over loops, etc.).

### Test cases

1. **Refactor OrderService** — mutable state, loops, checked exceptions, null returns, string concatenation report
2. **Refactor UserProfile** — mutable JavaBean → record
3. **Greenfield PaymentProcessing** — sealed `PaymentResult` hierarchy + dispatcher using pattern matching for `switch`

Input files for refactoring tests are in `evals/files/`.

## Conventions reference

The authoritative conventions are in `references/conventions.md`.
