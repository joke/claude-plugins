# Claude Plugins

A collection of Claude Code plugins for coding conventions and team-based development workflows.

## Plugins

### conventions

Coding convention skills for JVM languages. These are non-user-invocable skills loaded automatically by agents when writing or reviewing code.

| Skill | Description |
|---|---|
| `groovy-coding-conventions` | General Groovy programming principles and design conventions |
| `groovy-spock-coding-conventions` | Spock test structuring, mocking, data-driven tests, and interaction verification |
| `java-coding-conventions` | General Java programming principles and design conventions |

### workflows

Team-based development workflows using coordinated agents.

#### Skills

| Skill | Description |
|---|---|
| `feature` | Orchestrates feature development end-to-end. Validates the repo is clean, then launches the agent team. User-invocable. |

#### Agents

The `feature` skill spawns a four-agent team that follows a TDD workflow:

| Agent | Role |
|---|---|
| `architect` | Lead teammate. Researches the codebase, plans interactively with the user, broadcasts requirements to the team. Loads architecture convention skills. Never writes code. |
| `tester` | Owns the red phase. Translates the architect's requirements into failing Spock tests, gets them reviewed, then hands off to the implementer. |
| `implementer` | Owns the green phase. Makes failing tests pass, then submits code for review. Loads coding convention skills. |
| `reviewer` | Quality gate. Reviews test and implementation code against loaded conventions. Must approve before work proceeds. |

```
User Request
  └─► architect (plans with user)
        └─► tester (writes failing tests)
              └─► reviewer (approves tests)
                    └─► implementer (makes tests green)
                          └─► reviewer (approves implementation)
```

## Standalone Agents

Located in `.claude/agents/`, these are available outside the team workflow:

| Agent | Description |
|---|---|
| `spock-test-writer` | Writes Spock unit tests with strict convention compliance. Loads `groovy-coding-conventions` and `groovy-spock-coding-conventions` skills. Iterates through implement → review → fix cycles until zero violations, then runs tests. |
