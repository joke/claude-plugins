---
name: java17-coding-conventions
description: >
  Use when writing, reviewing, or modifying Java 17 code. Layers Java 17-specific conventions
  on top of the general java-coding-conventions skill. Covers records, sealed types, pattern
  matching for instanceof, text blocks, switch expressions, Stream.toList(), and the
  Java 17 version boundary. Does not cover formatting, indentation, or framework-specific patterns.
user-invocable: false
model: haiku-4.5
---

# Java 17 Code Conventions

First, use the Skill tool to load `conventions:java-coding-conventions`. Everything below builds on those foundations with Java 17-specific guidance.

Java 17 is the second LTS after Java 11. Compared to Java 11, it unlocks a batch of headline features that reshape how idiomatic Java is written: **records**, **sealed types**, **pattern matching for `instanceof`**, **text blocks**, **switch expressions with `->`**, and `Stream.toList()`. It does **not** yet have pattern matching for `switch` (stable in Java 21), record patterns (21), virtual threads (21), or sequenced collections (21).

## Java 17 Version Boundary

This skill covers Java 17 exclusively. The following features are **not available** and must **not** appear:

- Pattern matching for `switch` (stable in Java 21)
- Record patterns (Java 21)
- Unnamed patterns / variables (Java 21 preview)
- Virtual threads / `Thread.ofVirtual()` (Java 21)
- `SequencedCollection` / `SequencedMap` (Java 21)
- Scoped values (Java 21+ preview)
- String templates (Java 21 preview, since withdrawn)

Everything from Java 12 through 17 **is** available and should be preferred over older equivalents.

## Local Variable Type Inference (var)

`var` is available. Use it for local variables when the type is obvious from the right-hand side:

```java
final var customers = customerRepository.findAll();       // clearly List<Customer>
final var activeCount = customers.stream().filter(Customer::isActive).count(); // clearly long
```

**Always use `final var`** — never bare `var`. This keeps the immutability convention intact.

Don't use `var` when the type isn't obvious. If a reader needs to look up the return type to understand the code, spell it out.

## Records

Prefer **records** for data carriers. A record is a final, immutable class with a canonical constructor, accessors, `equals`, `hashCode`, and `toString` generated automatically:

```java
public record Customer(String id, String name, List<Order> orders) {
    public Customer {
        // compact constructor — validate and defensively copy
        orders = List.copyOf(orders);
    }
}
```

- Use records for **pure data** — DTOs, value objects, tuple-like return types, message payloads.
- Use the **compact constructor** to validate and to defensively copy mutable inputs (`List.copyOf`, `Map.copyOf`, `Set.copyOf`).
- Records are implicitly `final` and extend `java.lang.Record`. Don't try to extend them.
- Records **can** implement interfaces and have static factory methods — use `static` factories for alternative construction (e.g. `Customer.fromRow(...)`).
- Don't add mutable fields; records should stay immutable.

For classes with behavior beyond data carrying, stick with regular classes.

## Sealed Types

Use **sealed** interfaces/classes to model closed hierarchies where the set of subtypes is fixed and known:

```java
public sealed interface PaymentResult
        permits PaymentResult.Success, PaymentResult.Declined, PaymentResult.Error {

    record Success(String transactionId) implements PaymentResult {}
    record Declined(String reason) implements PaymentResult {}
    record Error(String message, Throwable cause) implements PaymentResult {}
}
```

- Sealed + records + pattern matching is the idiomatic way to model discriminated unions in Java 17.
- Permitted subtypes must be `final`, `sealed`, or `non-sealed`. Prefer `final` (or records, which are implicitly final) unless you deliberately want further extension.
- Use `non-sealed` only when a branch of the hierarchy genuinely needs to stay open — it's a documented decision, not an escape hatch.

## Pattern Matching for `instanceof`

Use `instanceof` pattern matching to replace the cast-after-check dance:

```java
// don't
if (shape instanceof Circle) {
    final Circle circle = (Circle) shape;
    return Math.PI * circle.radius() * circle.radius();
}

// do
if (shape instanceof final Circle circle) {
    return Math.PI * circle.radius() * circle.radius();
}
```

Always mark the pattern variable `final` — it matches the general convention of final locals. The pattern variable is only in scope where the match is true, so the compiler will catch misuses.

Pattern matching for `switch` is **not** available in Java 17 (it's a preview there, stable in 21) — use `if`/`else if` chains with `instanceof` patterns, or switch over an enum/sealed type with classic labels.

## Switch Expressions

Use `switch` **expressions** with the arrow (`->`) form. They're exhaustive, don't fall through, and return a value:

```java
final var category = switch (order.status()) {
    case PENDING, ACTIVE -> "open";
    case COMPLETED -> "closed";
    case CANCELLED, REFUNDED -> "terminated";
};
```

- Prefer switch expressions over `if`/`else if` chains when dispatching on an enum or small finite set of values.
- For multi-statement branches, use `{ ... yield value; }`.
- Never use the old colon-form (`case X:` + `break`) in new code.

When switching over a sealed type in Java 17, you can't yet rely on compiler exhaustiveness for type patterns — fall back to `instanceof` chains:

```java
final String describe;
if (result instanceof final PaymentResult.Success s) {
    describe = "ok: " + s.transactionId();
} else if (result instanceof final PaymentResult.Declined d) {
    describe = "declined: " + d.reason();
} else if (result instanceof final PaymentResult.Error e) {
    describe = "error: " + e.message();
} else {
    throw new IllegalStateException("Unknown result: " + result);
}
```

## Text Blocks

Use **text blocks** (`"""`) for any multi-line string. They eliminate escaping, preserve formatting, and strip incidental indentation:

```java
final var query = """
        SELECT id, name, email
        FROM customers
        WHERE active = true
        ORDER BY name
        """;
```

- Use for SQL, JSON templates, HTML fragments, multi-line error messages.
- Don't concatenate strings with `"\n"` or `+` across lines — use a text block instead.
- Use `.formatted(args...)` for simple interpolation (since Java 15).

## Immutable Collection Factories

Use `List.of`, `Map.of`, `Set.of` for small immutable collections — they return truly immutable collections and reject nulls. Use `List.copyOf`, `Map.copyOf`, `Set.copyOf` for defensive copies that are also immutable:

```java
public Customer(final String id, final List<Order> orders) {
    this.id = id;
    this.orders = List.copyOf(orders);
}
```

Prefer **`Stream.toList()`** (Java 16) over `Collectors.toList()` for terminal collection:

```java
final var activeNames = customers.stream()
        .filter(Customer::isActive)
        .map(Customer::name)
        .toList();  // returns an unmodifiable List
```

`Stream.toList()` returns an unmodifiable list and is shorter than `Collectors.toUnmodifiableList()`. Use it as the default; reach for collectors only when you need a mutable result, a specific implementation, or downstream grouping.

## Streams, Optional, Predicate

Beyond the Java 8/11 basics, the following additions are worth using:

- `Stream.toList()` (Java 16) — default terminal collection
- `Stream.mapMulti(...)` (Java 16) — flat-map-like with zero/many outputs, without materializing intermediate streams
- `Stream.ofNullable`, `Optional.stream()`, `Optional.isEmpty()`, `Optional.or`, `Optional.ifPresentOrElse` (all Java 9/11)
- `Predicate.not(...)` — negate method references without lambdas
- `Collectors.teeing(d1, d2, merger)` (Java 12) — combine two downstream collectors

All the Java 8 functional conventions still apply: prefer streams over loops, method references over trivial lambdas, no side effects inside stream pipelines, and never `.get()` without first making absence impossible through the functional API.

## Helpful NullPointerExceptions

Java 14+ produces helpful NPE messages by default (`-XX:+ShowCodeDetailsInExceptionMessages`). Don't wrap every dereference in a defensive null check just to produce a better error — rely on the JVM's message, and reserve `Objects.requireNonNull` for **public API boundaries** and constructor parameters.

## New String Methods

Prefer these over hand-rolled equivalents:

- `isBlank()`, `strip()`, `stripLeading()`, `stripTrailing()`, `lines()`, `repeat(int)` (Java 11)
- `formatted(Object...)` (Java 15) — instance method form of `String.format`, reads nicely with text blocks
- `String::indent` (Java 12) — adjust indentation of a multi-line string

## Files / IO

- `Files.readString(Path)` / `Files.writeString(Path, CharSequence)` (Java 11) — default UTF-8
- `Files.mismatch(Path, Path)` (Java 12) — byte-level comparison
- `java.net.http.HttpClient` for HTTP calls

## java.time API

Use `java.time` (LocalDate, LocalDateTime, Instant, Duration, Period) instead of `Date`/`Calendar`. The old date APIs are mutable and error-prone.

## Quick Decision Guide

When writing or reviewing Java 17 code, ask:

1. Is this a pure data carrier? → **record**
2. Is there a fixed, closed set of subtypes? → **sealed** interface/class + records
3. `instanceof` followed by a cast? → **pattern matching**, with `final` pattern variable
4. `if/else` chain or old-style `switch`? → **switch expression** with `->`
5. Multi-line string or string concatenation with `\n`? → **text block**
6. Collecting a stream into a list? → **`.toList()`**
7. Need an immutable collection? → **`List.of` / `List.copyOf`**
8. Local variable with an obvious RHS type? → **`final var`**
