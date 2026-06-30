---
name: opsx-artifact-commit
description: Use when creating, implementing, or syncing OpenSpec artifacts with opsx skills.
user-invocable: false
allowed-tools: Bash(git add:*), Bash(git diff:*), Bash(git commit:*)
---

**CRITICAL**: Load the `conventional-commits` skill before writing any commit message.

Commit automatically at these three moments — no need to wait for an explicit commit request:

**After writing `tasks.md`** (final planning artifact):
```bash
git commit --only -m "<message>" -- openspec/changes/<change-name>/
```

**After a successful `opsx:verify`** (implementation complete):
```bash
git add -u
git diff --cached
git commit -m "<message>"
```
Reference the change name in the commit footer: `Implements: <change-name>`

**Before syncing specs**:
```bash
git commit --only -m "<message>" -- openspec/specs/
```
