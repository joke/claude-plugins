---
name: feature
description: >
  Orchestrates feature development from start to finish.
user-invocable: true
disable-model-invocation: true
model: haiku
allowed-tools: TeamCreate, SendMessage
---

You MUST ALWAYS fetch the tool schemas for: TeamCreate, SendMessage

These are the phases of feature development. You MUST follow them precisely and do not deviate!

## Phase 1: Repository Validation

Before any work begins, the repository must be in a pristine state.

1. Run `git status` to check for modified, staged, or untracked files
2. If the repository is **clean** (no modifications, no staged changes, no untracked files): proceed to Phase 2
3. If the repository is **dirty**: stop and inform the user. Ask them how they want to proceed:
   - **Option A — You handle it**: Run `git stash` to safely preserve their changes, then re-check `git status` to confirm the repository is clean
   - **Option B — User handles it**: Wait for the user to clean up manually, then re-run `git status` to verify
4. Do NOT proceed to Phase 2 until `git status` confirms a pristine working tree

## Phase 2: Launch the Agent Team

Pick a random word to use as a team name.
Now you MUST start an agent team with that name. Launch the lead teammate first. Wait for the lead teammate to signal that you should launch the other teammates: 
- `architect` (lead teammate)
- `implementer`
- `tester`
- `reviewer`

Wait for the architect to send an explicit completion signal indicating the feature is done.