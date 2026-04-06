# Java Coding Conventions — Reference

This is the authoritative source for all conventions that the java-coding-conventions skill must encode. When regenerating the skill, include all of these rules with examples.

## Core Principles

1. **All variables are final** — every local variable, parameter, catch variable, and field. No reassignment.
2. **Immutable by default** — classes have `private final` fields, no setters, defensive copies of mutable inputs, unmodifiable collection returns.
3. **Small methods** — each does exactly one thing, named to describe *what* not *how*.
4. **Unchecked exceptions only** — no checked exceptions.
5. **Composition over inheritance** — prefer delegation to extending base classes.
6. **Constructor injection** — dependencies injected via constructor, never fields or setters.

## Detailed Rules

### Variables and Parameters

- Every variable is `final`: parameters, local variables, catch variables.
- This makes data flow explicit and prevents accidental reassignment.

### Immutability

- All fields `private final`.
- No setters. If state changes are needed, return a new instance.
- Constructor sets everything. Defensive copy mutable inputs.
- Return collections as unmodifiable (exact API depends on Java version).

### Small Methods

- Each method does one thing. If describing it requires "and", split it.
- Method names describe *what* they do.
- Extract predicates, mappers, and formatters into named methods.
- The calling method should read like a high-level description of the algorithm.

### Exceptions

- Only unchecked (`RuntimeException` subclasses).
- Create domain-specific exception classes when callers need to distinguish error types.
- Checked exceptions break lambdas and pollute signatures.

### Design

- Composition over inheritance.
- Interfaces only when there are multiple implementations or for testing seams.
- Constructor injection. No field or setter injection.
- Most restrictive visibility — start private.
- `static` for methods that don't use instance state.

### Imports

- Static imports when the name is self-explanatory: `PI`, `UTF_8`, `emptyList`, `assertEquals`.
- Qualified access when the class adds clarity: `Collections.unmodifiableList`, `Duration.ofSeconds`.

### Naming

- `PascalCase` classes/interfaces, `camelCase` methods/variables, `UPPER_SNAKE_CASE` constants.
- Method names describe *what* they return or do, not *how*.
