# Java 8 Coding Conventions — Reference

This is the authoritative source for all Java 8-specific conventions. The general Java conventions (final vars, immutability, small methods, etc.) are handled by `java-coding-conventions` — this file covers only what Java 8 adds on top.

## Java 8 Version Boundary

This skill covers Java 8 exclusively. The following features are NOT available and must NOT appear:

- `var` (Java 10)
- `List.of`, `Map.of`, `Set.of` (Java 9) — use `Collections.unmodifiableList(Arrays.asList(...))` etc.
- Records (Java 14)
- Sealed classes (Java 17)
- Pattern matching (Java 16+)
- Text blocks (Java 13)
- Switch expressions (Java 14)
- `Stream.toList()` (Java 16) — use `Collectors.toList()`
- Modules / module-info.java (Java 9)

## Immutable Collections in Java 8

- Defensive copy + freeze: `Collections.unmodifiableList(new ArrayList<>(input))`
- `Collections.emptyList()`, `Collections.singletonList()` for small collections
- `Collections.unmodifiableMap/Set` for other collection types

## Streams over Loops

- Prefer streams for filtering, mapping, reducing, collecting.
- Use `Collectors.toList()`, `Collectors.toSet()`, `Collectors.toMap()`, `Collectors.groupingBy()`, `Collectors.joining()`, `Collectors.partitioningBy()`.
- Method references (`Customer::getName`) over lambdas (`c -> c.getName()`) when the lambda just delegates.
- Extract complex predicates and mapping functions into named private methods.
- No side effects in streams — never use `forEach` to mutate external state.

## Optional

- Return `Optional<T>` instead of null for values that may be absent.
- Chain with `map`, `flatMap`, `filter`, `orElse`, `orElseGet`.
- Never call `.get()` without `.isPresent()` — prefer the functional chain.
- `orElse` for cheap constants, `orElseGet(supplier)` for expensive fallbacks.
- Don't use Optional for fields or method parameters.

## Functional Interfaces

- `@FunctionalInterface` on custom single-method interfaces.
- Prefer standard `java.util.function` types: `Function`, `Predicate`, `Consumer`, `Supplier`, `UnaryOperator`.
- Compose predicates with `and()`, `or()`, `negate()` and functions with `andThen()`, `compose()`.

## java.time API

- Use `java.time` (LocalDate, LocalDateTime, Instant, Duration, Period) instead of `Date`/`Calendar`.
