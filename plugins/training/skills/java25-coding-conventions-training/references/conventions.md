# Java 25 Coding Conventions — Reference

This is the authoritative source for all Java 25-specific conventions. The general Java conventions (final vars, immutability, small methods, etc.) are handled by `java-coding-conventions` — this file covers only what modern Java adds on top.

## Records

- Use `record` for classes that are pure data carriers (value objects, DTOs, events, query results).
- Use the compact canonical constructor (no parameter list) for validation and defensive copies.
- Use `List.copyOf`, `Map.copyOf`, `Set.copyOf` in the constructor to freeze collection components.
- Record components replace getters — access via `customer.name()` not `customer.getName()`.
- Don't use records for JPA entities or classes that need inheritance.

## Sealed Classes and Interfaces

- Use `sealed` to define a closed set of subtypes.
- Pair sealed types with pattern matching for exhaustive handling.
- Subtypes should be records when they're data carriers.

## Pattern Matching

### instanceof

- Use pattern matching: `if (shape instanceof final Circle c)` not `if (shape instanceof Circle)` followed by cast.
- Pattern variables must be `final`.

### Switch

- Use switch expressions with pattern matching for type dispatch over sealed types.
- No `default` needed when switching over sealed types — compiler enforces exhaustiveness.
- Use guarded patterns (`case Success s when s.data().isEmpty()`) for conditional logic.

## Switch Expressions

- Use `->` arrow form for all switches, even without pattern matching.
- No fall-through, returns a value, compiler checks exhaustiveness for enums.

## Text Blocks

- Use text blocks (`"""`) for multi-line strings: SQL, JSON, HTML, log messages.
- Align closing `"""` to control trailing whitespace.

## Local Variable Type Inference (var)

- Use `final var` (never bare `var`) when the type is obvious from the right-hand side.
- Spell out the type when the RHS doesn't make it obvious.

## Modern Collection Factories

- `List.of`, `Map.of`, `Set.of` for creating small immutable collections.
- `List.copyOf`, `Map.copyOf`, `Set.copyOf` for defensive copies.
- `Stream.toList()` instead of `Collectors.toList()`.
- `Collectors.toUnmodifiableList/Set/Map()` when an explicit collector is needed.
- Never use `Collections.unmodifiableList/Map/Set` — use the modern equivalents.

## Modern Stream/Optional Operations

- `stream().toList()` — shorthand for collecting to unmodifiable list.
- `Stream.ofNullable(value)` — zero-or-one element stream.
- `Optional.stream()` — converts Optional to stream.
- `Optional.or(() -> alternative)` — chain Optional suppliers.
- `Optional.ifPresentOrElse(action, emptyAction)` — handle both cases.
