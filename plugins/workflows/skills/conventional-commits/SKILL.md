---
name: conventional-commits
description: Use when writing a git commit message.
user-invocable: false
allowed-tools: Bash(git diff:*), Bash(git status:*), Bash(git log:*)
---

## Format

```
<type>(<scope>): <subject>

[body]

[footer]
```

## Types

| Type | When to use |
|------|-------------|
| `feat` | New feature or behaviour |
| `fix` | Bug fix |
| `refactor` | Code change that is neither a fix nor a feature |
| `test` | Adding or updating tests |
| `docs` | Documentation only |
| `chore` | Build, tooling, dependencies, config |
| `perf` | Performance improvement |
| `ci` | CI/CD changes |

## Scope

Optional. Names the component, module, or area affected. Use the dominant area when multiple are touched.

## Subject

- Imperative mood: "add", not "added" or "adds"
- Lowercase
- No trailing period
- Max 72 characters

## Body

Optional. Explains *why*, not *what*. Separate from subject with a blank line.

## Footer

Optional. Use for references and breaking changes:

```
BREAKING CHANGE: <description>
Closes: #<issue>
Implements: <openspec-change-name>
```

## Read before writing

Always inspect the actual changes before composing the message:

```bash
git diff --cached
git status
```
