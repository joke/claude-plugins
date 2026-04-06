# Java 8 Coding Conventions — Reference

This is the authoritative source for all conventions that the java8-coding-conventions skill must encode. When regenerating the skill, include all of these rules with examples.

## Core Principles

1. **All variables are final** — every local variable, parameter, and field. No reassignment.
2. **Immutable by default** — classes have `private final` fields, no setters, defensive copies of mutable inputs, unmodifiable collection returns.
3. **Functional style** — streams over loops, method references over lambdas when possible, no side effects in streams, compose operations declaratively.
4. **Small methods** — each does exactly one thing, named to describe *what* not *how*.
5. **Unchecked exceptions only** — no checked exceptions.

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

## Detailed Rules

### Variables and Parameters

- Every variable is `final`: parameters, local variables, catch variables, enhanced for-each variables.
- This makes data flow explicit and prevents accidental reassignment.

### Immutability

- All fields `private final`.
- No setters. Ever. If state changes are needed, return a new instance.
- Constructor sets everything. Defensive copy mutable inputs: `new ArrayList<>(input)`.
- Return collections as unmodifiable: `Collections.unmodifiableList(this.items)`.
- Use `Collections.unmodifiableList/Map/Set` for wrapping.

### Streams over Loops

- Prefer streams for filtering, mapping, reducing, collecting.
- Use `Collectors.toList()`, `Collectors.toSet()`, `Collectors.toMap()`, `Collectors.groupingBy()`, `Collectors.joining()`, `Collectors.partitioningBy()`.
- Method references (`Customer::getName`) over lambdas (`c -> c.getName()`) when the lambda just delegates.
- Extract complex predicates and mapping functions into named private methods.
- No side effects in streams — never use `forEach` to mutate external state or accumulate into a collection.

### Optional

- Return `Optional<T>` instead of null for values that may be absent.
- Chain with `map`, `flatMap`, `filter`, `orElse`, `orElseGet`.
- Never call `.get()` without `.isPresent()` — prefer the functional chain instead.
- `orElse` for cheap constants, `orElseGet(supplier)` for expensive fallbacks.
- Don't use Optional for fields or method parameters — it's for return types.

### Small Methods

- Each method does one thing. If describing it requires "and", split it.
- Method names describe *what* they do.
- Extract predicates, mappers, and formatters into named methods for readability.
- The calling method should read like a high-level description of the algorithm.

### Functional Interfaces

- `@FunctionalInterface` on custom single-method interfaces.
- Prefer standard `java.util.function` types: `Function`, `Predicate`, `Consumer`, `Supplier`, `UnaryOperator`, `BiFunction`, `BiPredicate`.
- Compose predicates with `and()`, `or()`, `negate()` and functions with `andThen()`, `compose()`.

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

### java.time API

- Use `java.time` (LocalDate, LocalDateTime, Instant, Duration, Period) instead of `Date`/`Calendar`.

### Imports

- Static imports when the name is self-explanatory: `PI`, `UTF_8`, `emptyList`, `assertEquals`.
- Qualified access when the class adds clarity: `Collections.unmodifiableList`, `Collectors.toList`, `Optional.empty`.

### Naming

- `PascalCase` classes/interfaces, `camelCase` methods/variables, `UPPER_SNAKE_CASE` constants.
