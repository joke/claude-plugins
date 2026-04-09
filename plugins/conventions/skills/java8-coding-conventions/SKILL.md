---
name: java8-coding-conventions
description: >
  Use when writing, reviewing, or modifying Java 8 code. Layers Java 8-specific functional
  programming conventions on top of the general java-coding-conventions skill. Covers streams,
  Optional, functional interfaces, and the Java 8 version boundary. Does not cover formatting,
  indentation, or framework-specific patterns.
user-invocable: false
model: haiku-4.5
---

# Java 8 Code Conventions

First, use the Skill tool to load `conventions:java-coding-conventions`. Everything below builds on those foundations with Java 8-specific guidance.

## Java 8 Version Boundary

This skill covers Java 8 exclusively. The following features are **not available** and must **not** appear:

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

Java 8 doesn't have `List.of` or `Map.of`. To create unmodifiable collections:

**Defensive copy + freeze in constructors:**
```java
public Customer(final String id, final List<Order> orders) {
    this.id = id;
    this.orders = Collections.unmodifiableList(new ArrayList<>(orders));
}
```

Always `new ArrayList<>(input)` first (defensive copy), then `Collections.unmodifiableList(...)` (freeze). This two-step pattern ensures the caller can't mutate your internal state after construction.

**For collection getters**, return the already-frozen field — no need to wrap again:
```java
public List<Order> getOrders() {
    return orders; // already unmodifiable from constructor
}
```

**For inline unmodifiable collections:**
- `Collections.unmodifiableList(Arrays.asList(...))` instead of `List.of(...)`
- `Collections.unmodifiableMap(...)` instead of `Map.of(...)`
- `Collections.unmodifiableSet(new HashSet<>(Arrays.asList(...)))` instead of `Set.of(...)`
- `Collections.emptyList()`, `Collections.emptyMap()`, `Collections.emptySet()` for empty collections
- `Collections.singletonList(x)` for single-element lists

## Streams over Loops

Prefer streams for all collection processing. Streams express *what* you want, not *how* to iterate — they compose naturally and avoid mutable accumulators.

```java
// imperative — avoid
final List<String> result = new ArrayList<>();
for (final Customer c : customers) {
    if (c.isActive()) {
        result.add(c.getName().toUpperCase());
    }
}

// functional — prefer
final List<String> result = customers.stream()
        .filter(Customer::isActive)
        .map(Customer::getName)
        .map(String::toUpperCase)
        .collect(Collectors.toList());
```

**Method references over lambdas** when the lambda just delegates to an existing method. `Customer::isActive` is clearer than `c -> c.isActive()` because it names the operation directly.

**No side effects in streams.** Never use `forEach` to accumulate into an external collection or mutate state. Use `collect`, `reduce`, or `toMap` instead.

**Key collectors** — know these well:
- `Collectors.toList()`, `Collectors.toSet()` — basic collection
- `Collectors.toMap(keyFn, valueFn)` — build maps
- `Collectors.groupingBy(classifier)` — group elements
- `Collectors.joining(delimiter)` — concatenate strings
- `Collectors.partitioningBy(predicate)` — split into true/false groups

## Optional

Return `Optional<T>` instead of null when a value may be absent. This makes the possibility of absence explicit in the type signature.

```java
public Optional<Customer> findById(final String id) {
    return customers.stream()
            .filter(c -> c.getId().equals(id))
            .findFirst();
}
```

**Chain Optional operations** — use `map`, `flatMap`, `filter`, and `orElse`/`orElseGet` instead of `isPresent` + `get`:

```java
// imperative — avoid
final Optional<Customer> customer = findById(id);
if (customer.isPresent()) {
    return customer.get().getName();
}
return "unknown";

// functional — prefer
return findById(id)
        .map(Customer::getName)
        .orElse("unknown");
```

Never call `.get()` without `.isPresent()` — but even better, avoid both by using the functional API.

**`orElse` vs `orElseGet`** — use `orElse` for cheap constants, `orElseGet` when the fallback is expensive (it takes a `Supplier` and only evaluates on absence).

**Don't use Optional for fields or parameters** — it's designed for return types.

## Functional Interfaces

Use `@FunctionalInterface` on custom single-method interfaces. This documents intent and lets the compiler catch accidental additions of abstract methods.

Prefer the standard `java.util.function` types when they fit:
- `Function<T, R>` — transform T to R
- `Predicate<T>` — test T, return boolean
- `Consumer<T>` — accept T, return nothing
- `Supplier<T>` — produce T from nothing
- `UnaryOperator<T>` — transform T to T
- `BiFunction<T, U, R>`, `BiPredicate<T, U>` — two-argument variants

Compose them with `and()`, `or()`, `negate()` (Predicate) and `andThen()`, `compose()` (Function).

## java.time API

Use `java.time` (LocalDate, LocalDateTime, Instant, Duration, Period) instead of `Date`/`Calendar`. The old date APIs are mutable and error-prone.

```java
final LocalDate today = LocalDate.now();
final LocalDate deadline = today.plusDays(30);
final Duration elapsed = Duration.between(start, end);
```
