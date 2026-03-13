---
name: java-code-conventions
description: >
  Use when writing, reviewing, or modifying Java code. Applies general programming
  principles and design conventions. Does not cover formatting or indentation.
user-invocable: false
---

# Java Code Conventions

## Immutability

- Classes are immutable by default. Use setters only if absolutely necessary.
- Variables and parameters must be `final`.
- Prefer unmodifiable collections (`List.of`, `Map.of`). Store and return collections as unmodifiable when they don't need mutation.

## Null Handling

- Prefer `Optional<T>` for values that may be absent.
- If null is used, annotate with jspecify `@Nullable`.
- Mark packages as jspecify `@NullMarked`.

## Exceptions

- Only unchecked exceptions (`RuntimeException` subclasses). No checked exceptions.

## Design

- Composition over inheritance. Inheritance only for true is-a relationships.
- Interfaces only when there are multiple implementations or needed for testing.
- Constructor injection for DI. No field injection.

## Modern Java

- Prefer records for data carriers.
- Use `var` for local variables.
- Use sealed classes and pattern matching where appropriate.

## Methods

- Each method does exactly one thing. If you can't describe it simply, extract.
- Method names describe what the method does.
- Small and focused. Extract named methods over inline logic.
- Prefer streams over loops for collection processing.

## Visibility & Static

- Most restrictive access modifier possible. Start private, widen only when needed.
- Prefer `static` where possible.

## Imports

- Prefer static imports when the import name is self-explanatory (e.g., `PI`, `UTF_8`, `singletonMap`, `format`, `assertEquals`).
- Use qualified static access when the class name provides a much clearer context (e.g., `List.of`, `Map.of`, `Duration.ofSeconds`)

## Naming

- Standard Java conventions: `PascalCase` classes, `camelCase` methods/variables, `UPPER_SNAKE_CASE` constants.
