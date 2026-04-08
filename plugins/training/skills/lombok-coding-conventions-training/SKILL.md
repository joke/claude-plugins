---
name: lombok-coding-conventions-training
description: >
  Training skill that generates and validates the lombok-coding-conventions skill.
  Run this skill to regenerate the conventions from reference material and verify
  them against test cases. Use when updating or re-tuning Lombok conventions.
user-invocable: true
model: haiku-4.5
---

# Lombok Coding Conventions Training

This skill regenerates the `lombok-coding-conventions` skill from reference material
and validates it against test cases.

## What it produces

A SKILL.md at `plugins/conventions/skills/lombok-coding-conventions/SKILL.md` that
teaches Claude to replace Java boilerplate with Lombok annotations wherever Lombok
is on the classpath.

## Step 1: Regenerate the skill

Read `references/conventions.md` for the full set of conventions. Then write the
output skill:

1. **Output path:** `plugins/conventions/skills/lombok-coding-conventions/SKILL.md`
2. **Frontmatter:** name `lombok-coding-conventions`, `user-invocable: false`, `model: haiku-4.5`
3. **Scope:** Lombok-first Java code. Version-agnostic.
4. **Tone:** Explain *why* each convention matters. Use before/after examples. Imperative form.
5. **Length:** Under 500 lines. Dense and practical.
6. **Structure:** Detection, constructor annotations, data class annotations, builders, utility annotations, what not to use, quick decision guide.

Key things the skill must make very clear:
- Never write a constructor/getter/setter/toString/equals/hashCode by hand when an annotation will generate it
- `@Inject`/`@Autowired` constructors go via `onConstructor_` on `@RequiredArgsConstructor`
- Manual `Logger` fields must be replaced with the matching `@Log` variant (`@Slf4j`, `@Log4j2`, etc.)
- Utility classes use `@UtilityClass`; exception classes use `@StandardException`
- `lombok.val` / `lombok.var` must never be used — use Java's native `var` instead

## Step 2: Validate with test cases

After regenerating, validate the skill using the test cases in `evals/evals.json`.

For each test case, spawn a subagent that:
1. Reads the generated skill from `plugins/conventions/skills/lombok-coding-conventions/SKILL.md`
2. Reads any input files specified in the test case
3. Completes the task described in the prompt, following the skill's conventions
4. Writes output Java files to a workspace directory

Then run the shared grading script against the outputs:

```bash
cd plugins/training
python -m shared.grade <workspace-dir>
```

The script checks:
- No hand-written getters/setters
- No hand-written `toString` / `equals` / `hashCode`
- Lombok annotations are actually used
- No manual `Logger` field when `@Slf4j` (or variant) applies
- `@Inject`/`@Autowired` constructors use `onConstructor_`
- Exception classes use `@StandardException`; utility classes use `@UtilityClass`
- No `lombok.val` / `lombok.var` imports

### Test cases

1. **Refactor UserDto** — manual getters, setters, constructor, toString, equals/hashCode → `@Data` (or the equivalent combination)
2. **Refactor GreetingService** — hand-written `@Inject` constructor and manual SLF4J `Logger` field → `@RequiredArgsConstructor(onConstructor_ = @Inject)` + `@Slf4j`
3. **Greenfield utilities** — create a `StringUtils` utility class and a `ValidationException` exception class using `@UtilityClass` and `@StandardException`

Input files for refactoring tests are in `evals/files/`.

## Conventions reference

The authoritative conventions are in `references/conventions.md`.
