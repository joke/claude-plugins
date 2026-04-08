---
name: java11-coding-conventions-training
description: >
  Training skill that generates and validates the java11-coding-conventions skill.
  Run this skill to regenerate the conventions from reference material and verify
  them against test cases. Use when updating or re-tuning Java 11 coding conventions.
user-invocable: true
model: haiku-4.5
---

# Java 11 Coding Conventions Training

This skill regenerates the `java11-coding-conventions` skill from reference material and validates it against test cases.

## What it produces

A SKILL.md at `plugins/conventions/skills/java11-coding-conventions/SKILL.md` that teaches Claude to write and review Java 11 code. This skill layers Java 11-specific conventions on top of the general `java-coding-conventions` skill.

## Step 1: Regenerate the skill

Read `references/conventions.md` for the Java 11-specific conventions. Then write the output skill:

1. **Output path:** `plugins/conventions/skills/java11-coding-conventions/SKILL.md`
2. **Frontmatter:** name `java11-coding-conventions`, `user-invocable: false`, `model: haiku-4.5`
3. **Scope:** Java 11 (LTS). Java 9/10/11 features are allowed and preferred over Java 8 equivalents. Features from Java 12+ must not appear. The skill must reference `plugins/conventions/skills/java-coding-conventions/SKILL.md` for general conventions and only add Java 11-specific guidance.
4. **Tone:** Explain *why* each convention matters, not just what to do. Use before/after examples. Imperative form.
5. **Length:** Under 500 lines. Dense and practical — no filler.
6. **Structure:** Start with inclusion of general skill, then: version boundary, `var`, immutable collection factories (`List.of`/`copyOf`, `Collectors.toUnmodifiableList`), stream/Optional additions (Java 9/11), `Predicate.not`, new `String` methods (`isBlank`/`strip`/`lines`/`repeat`), `Files.readString`/`writeString`, `HttpClient`, `java.time`.

Key things the skill must make very clear (these are the conventions models don't follow without explicit instruction):
- Use `final var` for locals when the type is obvious from the RHS — never bare `var`
- Use `List.of`/`Map.of`/`Set.of` for small immutable collections, and `List.copyOf` etc. for defensive copies (replaces the Java 8 `unmodifiableList(new ArrayList<>(...))` pattern)
- Use `Collectors.toUnmodifiableList()` — `Stream.toList()` is Java 16 and must not appear
- Prefer `Optional.isEmpty()`, `Optional.or`, `ifPresentOrElse`, `Optional.stream()`, `Stream.ofNullable`
- Use `Predicate.not(String::isBlank)` style negation
- Use `String.isBlank/strip/lines/repeat` instead of `trim().isEmpty()` and similar workarounds
- Use `Files.readString` / `Files.writeString` with the default UTF-8
- Use `java.net.http.HttpClient` for HTTP calls
- No records, sealed, pattern matching, text blocks, switch expressions with `->`, or `Stream.toList()`

## Step 2: Validate with test cases

After regenerating, validate the skill using the test cases in `evals/evals.json`.

For each test case, spawn a subagent that:
1. Reads the general skill from `plugins/conventions/skills/java-coding-conventions/SKILL.md`
2. Reads the generated Java 11 skill from `plugins/conventions/skills/java11-coding-conventions/SKILL.md`
3. Reads any input files specified in the test case
4. Completes the task described in the prompt, following both skills' conventions
5. Writes output Java files to a workspace directory

Then run the shared grading script against the outputs:

```bash
cd plugins/training
python -m shared.grade <workspace-dir>
```

The script checks Java 11-specific assertions:
- `no-post-java11-features` — no records/sealed/pattern matching/text blocks/switch expressions/`Stream.toList()`
- `unmodifiable-collections-java11` — `List.of`/`copyOf` or `Collections.unmodifiable*`
- `streams-over-loops`, `optional-for-find`
- `all-vars-final-or-var` — allows `final var` alongside `final`

Plus general assertions (immutable fields, small methods, etc.) to verify the general skill inclusion works correctly.

### Expected results

All assertions should pass for all test cases. If any fail, the conventions in the skill need strengthening in that area.

### Test cases

The test cases in `evals/evals.json` cover:
1. **Refactor OrderService** — mutable state, loops, checked exceptions, null returns, long methods
2. **Refactor UserProfile** — mutable JavaBean with getters/setters, imperative collection code
3. **Greenfield InventoryService** — write a new service class from scratch

Input files for refactoring tests are in `evals/files/`.

## Conventions reference

The authoritative conventions are in `references/conventions.md`. Always read that file when regenerating — it is the single source of truth for what Java 11-specific rules to include.
