# Java Coding Conventions — Reference

This is the authoritative source for all conventions that the java-coding-conventions skill must encode. When regenerating the skill, include all of these rules with examples.

## Core Principles

1. **All variables are final** — every local variable, parameter, catch variable, and field. No reassignment.
2. **Immutable by default** — classes have `private final` fields, no setters, defensive copies of mutable inputs, unmodifiable collection returns.
3. **Tiny single-purpose methods** — each does exactly one thing in a few lines, named to describe *what* not *how*.
4. **Unchecked exceptions only** — no checked exceptions.
5. **Composition over inheritance** — prefer delegation to extending base classes.
6. **Constructor injection** — dependencies injected via constructor, never fields or setters.
7. **Visibility chosen for testability** — helper methods are `protected` + `@VisibleForTesting` (not `private`) and are instance methods (not `static`), so they can be called and spied in isolation. Fields stay `private final`.

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

- Each method does one thing and is only a few lines long. If describing it requires "and" ("validates the input *and* charges the card"), that is two methods — split it.
- Method names describe *what* they do.
- Extract predicates, mappers, and formatters into named methods.
- The calling method should read like a high-level description of the algorithm.

### Visibility and Testability

Method visibility is chosen for **testability**, not just encapsulation. (Fields are still always `private final` — this rule is about methods.)

- **Prefer `protected` over `private` for methods.** A `private` helper can only be exercised through the public method that calls it; a `protected` method can be called directly from a test and stubbed/spied so the caller is tested in isolation from its helpers.
- Annotate every method you would otherwise have made private with `@VisibleForTesting` from `org.jetbrains.annotations`, so the wider visibility is understood as a test seam, not a public contract.
- Do **not** mark these helpers `final` — a `final` method cannot be overridden, which is how a spy stubs it.
- **Constructors are the exception** — keep them as restrictive as the class needs; you don't spy a constructor.
- **Prefer instance methods over `static` for helpers.** A `static` method cannot be spied; even a helper that uses no instance state should be an instance method so tests can stub it. The exception is a **pure utility class** — nothing but stateless static methods — where there is no instance to spy and `static` is correct.
- The class's *public* API still stays minimal: `public` only what callers need; everything internal is `protected` (a test seam), not `public`.

### Exceptions

- Only unchecked (`RuntimeException` subclasses).
- Create domain-specific exception classes when callers need to distinguish error types.
- Checked exceptions break lambdas and pollute signatures.

### Design

- Composition over inheritance.
- Interfaces only when there are multiple implementations or for testing seams.
- Constructor injection. No field or setter injection.
- Method visibility and instance-vs-static are governed by the Visibility and Testability rules above.

### Imports

- Static imports when the name is self-explanatory: `PI`, `UTF_8`, `emptyList`, `assertEquals`.
- Qualified access when the class adds clarity: `Collections.unmodifiableList`, `Duration.ofSeconds`.

### Naming

- `PascalCase` classes/interfaces, `camelCase` methods/variables, `UPPER_SNAKE_CASE` constants.
- Method names describe *what* they return or do, not *how*.
