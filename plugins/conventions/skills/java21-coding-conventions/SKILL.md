---
name: java21-coding-conventions
description: >
  Use when writing, reviewing, or modifying Java 21 code. Layers Java 21-specific conventions
  on top of the general java-coding-conventions skill. Covers pattern matching for switch,
  record patterns, virtual threads, sequenced collections, and the Java 21 version boundary.
  Does not cover formatting, indentation, or framework-specific patterns.
user-invocable: false
model: haiku-4.5
---

# Java 21 Code Conventions

First, use the Skill tool to load `conventions:java-coding-conventions`. Everything below builds on those foundations with Java 21-specific guidance.

Java 21 is the third LTS after Java 8 and 11 and 17. It finalises the pattern-matching story (**pattern matching for `switch`**, **record patterns**), introduces **virtual threads**, and adds **sequenced collections**. Together, these reshape how idiomatic Java is written once more: discriminated unions become ergonomic, structured concurrency becomes cheap, and encounter order gets a proper API.

## Java 21 Version Boundary

This skill covers Java 21 exclusively. The following features are **not available** and must **not** appear:

- Unnamed patterns / unnamed variables (Java 22 stable, previewed in 21)
- String templates (`STR."..."` — previewed in 21, subsequently withdrawn)
- Flexible constructor bodies / statements before `super(...)` (Java 22+)
- Primitive type patterns (Java 23+)
- Scoped values as a stable API (preview in 21)
- Structured concurrency as a stable API (preview in 21)
- Module imports / `import module` (Java 23+)

Everything from Java 12 through 21 **is** available and should be preferred over older equivalents.

## Local Variable Type Inference (var)

`var` is available. Use `final var` for local variables when the type is obvious from the right-hand side. Never use bare `var` — it would leave the local non-final and break the immutability convention.

## Records and Sealed Types

Prefer **records** for pure data carriers, and **sealed** interfaces/classes for closed hierarchies. Compact constructors remain the place to validate and defensively copy mutable inputs (`List.copyOf`, `Map.copyOf`, `Set.copyOf`). Records implicitly extend `java.lang.Record` and are `final`.

```java
public sealed interface PaymentResult permits Success, Declined, Error {}
public record Success(String transactionId) implements PaymentResult {}
public record Declined(String reason) implements PaymentResult {}
public record Error(String message, Throwable cause) implements PaymentResult {}
```

Permitted subtypes must be `final`, `sealed`, or `non-sealed`. Prefer `final` (or records, which are implicitly final) unless a branch genuinely needs to stay open.

## Pattern Matching for `switch`

This is the headline Java 21 feature. Use **pattern matching for `switch`** to replace `instanceof` chains when dispatching on a type — especially on a sealed hierarchy, where the compiler now enforces exhaustiveness:

```java
final String description = switch (result) {
    case Success(final String txId)            -> "ok: " + txId;
    case Declined(final String reason)         -> "declined: " + reason;
    case Error(final String msg, final var e)  -> "error: " + msg;
};
```

- Switches over a sealed type are **exhaustive** — omit the `default` branch. Adding a case to the sealed type then becomes a compile error, which is exactly the feedback you want.
- Use `when` guards for refinements: `case Success s when s.transactionId().isBlank() -> ...`.
- Use `null` as a case label (`case null ->`) when you want to handle null explicitly instead of letting the switch throw NPE.
- Mark pattern variables `final` — same rule as `instanceof` patterns.

For non-exhaustive switches (open types, `Object`, or when you can't enumerate cases), add a `default` branch that either produces a fallback or throws `IllegalStateException`.

**Do not** fall back to the old `if (x instanceof Foo f) { ... } else if ...` chain when the subject is a sealed type — use switch pattern matching instead.

## Record Patterns

Use **record patterns** to destructure records inline, including nested records. Combine with pattern matching for `switch` or `instanceof`:

```java
if (event instanceof final OrderPlaced(final String orderId, final Customer(final String id, final var name), final var total)) {
    log.info("order {} for {} ({}): {}", orderId, name, id, total);
}
```

Always mark the bound variables `final`. Record patterns compose naturally with sealed switches:

```java
final BigDecimal amount = switch (line) {
    case CashPayment(final var value)                      -> value;
    case CardPayment(final var value, final var _fees)     -> value;  // unused — spell it out
    case Refund(final var original, final var _reason)     -> original.negate();
};
```

Use record patterns whenever you'd otherwise call a chain of accessors (`result.order().customer().name()`) — destructuring is clearer at the call site and the compiler validates the shape.

## Virtual Threads

Use **virtual threads** for blocking workloads (IO, waiting on downstreams). They're cheap, so you can create one per task:

```java
try (final var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    final List<Future<String>> futures = requests.stream()
            .map(request -> executor.submit(() -> fetch(request)))
            .toList();
    // gather results
}
```

- Prefer `Executors.newVirtualThreadPerTaskExecutor()` for IO-bound task dispatch instead of sizing a platform-thread pool.
- Use `Thread.ofVirtual().start(runnable)` for one-off background tasks.
- Do **not** pool virtual threads — creating a new one per task is the point.
- Virtual threads are **not** a substitute for CPU-bound parallelism — keep using `ForkJoinPool` / parallel streams for that.
- Avoid long `synchronized` blocks around blocking calls — they pin the carrier thread. Prefer `ReentrantLock` in hot paths.

## Sequenced Collections

Java 21 introduces `SequencedCollection`, `SequencedSet`, and `SequencedMap` — interfaces that expose first/last access and reversed views on collections with a defined encounter order:

```java
final SequencedSet<String> tags = new LinkedHashSet<>(inputTags);
final String newest = tags.getLast();
final SequencedSet<String> oldestFirst = tags.reversed();
```

Use `getFirst()` / `getLast()` / `addFirst()` / `addLast()` / `removeFirst()` / `removeLast()` / `reversed()` instead of the older idioms (`list.get(0)`, `list.get(list.size() - 1)`, `Collections.reverse`). They communicate intent and work uniformly across `List`, `LinkedHashSet`, `LinkedHashMap`, `Deque`, and `SortedSet`.

## Streams, Optional, Collections

All the stream/Optional conventions from earlier Java versions still apply:

- `Stream.toList()` as the default terminal collection
- `Stream.mapMulti` when flat-map would force materialising intermediate streams
- `Collectors.teeing` to combine two downstream collectors
- `Optional.isEmpty`, `Optional.or`, `Optional.ifPresentOrElse`, `Optional.stream`, `Stream.ofNullable`
- `Predicate.not(...)` to negate method references
- `List.of`, `Map.of`, `Set.of`, `List.copyOf` for immutable collections

## Text Blocks

Use text blocks (`"""`) for any multi-line string — SQL, JSON templates, HTML fragments, multi-line error messages. Use `.formatted(args...)` for interpolation. String templates (`STR."..."`) are preview-only and were later withdrawn — do not use them.

## Helpful NullPointerExceptions

Helpful NPE messages are on by default. Don't wrap every dereference in a defensive null check to produce a better error — rely on the JVM's message and reserve `Objects.requireNonNull` for public API boundaries and constructor parameters.

## java.time API

Use `java.time` (LocalDate, LocalDateTime, Instant, Duration, Period) instead of `Date`/`Calendar`.

## Quick Decision Guide

When writing or reviewing Java 21 code, ask:

1. Is this a pure data carrier? → **record**
2. Is there a fixed, closed set of subtypes? → **sealed** interface/class + records + exhaustive switch
3. Dispatching on a type? → **pattern matching for `switch`** (not `instanceof` chains)
4. Accessing fields of a record? → **record pattern** destructuring
5. Blocking IO workload? → **virtual thread** (one per task)
6. Need first/last/reversed on an ordered collection? → **sequenced collection** methods
7. Multi-line string? → **text block**
8. Collecting a stream into a list? → **`.toList()`**
9. Local variable with an obvious RHS type? → **`final var`**
