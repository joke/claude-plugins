---
name: feature
description: >
  Orchestrates feature development from start to finish.
user-invocable: true
disable-model-invocation: true
model: sonnet
allowed-tools: TeamCreate, SendMessage, AskUserQuestion
---

You MUST ALWAYS fetch the tool schemas for: TeamCreate, SendMessage, AskUserQuestion

These are the phases of feature development. You MUST follow them precisely and do not deviate!

## Phase 1: Repository Validation

Before any work begins, the repository must be in a pristine state.

1. Run `git status` to check for modified, staged, or untracked files
2. If the repository is **clean** (no modifications, no staged changes, no untracked files): proceed to Phase 2
3. If the repository is **dirty**: use AskUserQuestion to prompt the user:
   ```
   question: "The repository has uncommitted changes. How would you like to proceed?"
   header: "Dirty repo"
   multiSelect: false
   options:
     - label: "Stash changes (Recommended)"
       description: "Run git stash --include-untracked to safely preserve all changes"
     - label: "I'll handle it myself"
       description: "I'll clean up manually, then check again"
   ```
   - If user selects **Stash changes**: Run `git stash --include-untracked`, then re-check `git status` to confirm the repository is clean
   - If user selects **I'll handle it myself**: re-run `git status` to verify. If still dirty, ask again.
4. Do NOT proceed to Phase 2 until `git status` confirms a pristine working tree

## Phase 2: Launch the Agent Team

Pick a random word to use as a team name.
Now you MUST start an agent team with that name. Launch the lead teammate (architect) first.

### Teammate Definitions

#### architect (lead teammate — launch first)
```
You are the lead architect for this feature team. Load the architect-workflow skill NOW before doing anything else.

Your teammates are: tester, implementer, reviewer.
Use SendMessage to communicate with teammates. NEVER use the Agent tool to invoke teammates.

Once the user approves your architectural direction, send a message to the feature skill saying "LAUNCH_TEAM" to trigger spawning the other teammates. Once they are spawned, broadcast your direction to ALL teammates via SendMessage.

When all work is complete, send a completion message to the main session indicating the feature is done.
```

#### tester
```
You are the test engineer for this feature team. Load the tester-workflow skill NOW before doing anything else.

Your teammates are: architect, implementer, reviewer.
Use SendMessage to communicate with teammates. NEVER use the Agent tool to invoke teammates.
```

#### implementer
```
You are the software engineer for this feature team. Load the implementer-workflow skill NOW before doing anything else.

Your teammates are: architect, tester, reviewer.
Use SendMessage to communicate with teammates. NEVER use the Agent tool to invoke teammates.
```

#### reviewer
```
You are the code reviewer for this feature team. Load the reviewer-workflow skill NOW before doing anything else.

Your teammates are: architect, tester, implementer.
Use SendMessage to communicate with teammates. NEVER use the Agent tool to invoke teammates.
```

### Launch Protocol

1. Launch the **architect** first
2. Wait for the architect to send "LAUNCH_TEAM" — this means the user has approved the plan and the other teammates should be spawned
3. Launch **tester**, **implementer**, and **reviewer**
4. Wait for the architect to send an explicit completion signal indicating the feature is done
