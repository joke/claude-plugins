---
name: java11-coding-conventions
description: >
  Use when writing, reviewing, or modifying Java 11 code. Layers Java 11-specific conventions
  on top of the general java-coding-conventions skill. Covers var, immutable collection factories,
  new String/Optional/Predicate methods, the java.net.http client, and the Java 11 version
  boundary. Does not cover formatting, indentation, or framework-specific patterns.
user-invocable: false
---

# Java 11 Code Conventions

First, use the Skill tool to load `conventions:java-coding-conventions`. Everything below builds on those foundations with Java 11-specific guidance.

Java 11 is the first LTS after Java 8. It brings `var`, the `List.of`/`Map.of`/`Set.of` factories, a modern `HttpClient`, and a handful of small but high-value additions to `String`, `Optional`, `Predicate`, and `Files`. It does **not** yet have records, sealed types, pattern matching, text blocks, or switch expressions — those come later.

## Java 11 Version Boundary

This skill covers Java 11 exclusively. The following features are **not available** and must **not** appear:

- Records (Java 14)
- Sealed classes (Java 17)
- Pattern matching for `instanceof` (Java 16) and `switch` (Java 21)
- Text blocks (Java 13/15)
- Switch expressions with `->` (Java 14)
- `Stream.toList()` (Java 16) — use `Collectors.toUnmodifiableList()` or `Collectors.toList()`
- `Stream.mapMulti` (Java 16)
- Helpful NullPointerExceptions as a stable feature (Java 14)

Features from Java 9 and 10 **are** available and preferred over their Java 8 equivalents (see below).

## Local Variable Type Inference (var)

`var` (Java 10) is available. Use it for local variables when the type is obvious from the right-hand side:

```java
final var customers = customerRepository.findAll();       // clearly List<Customer>
final var activeCount = customers.stream().filter(Customer::isActive).count(); // clearly long
```

**Always use `final var`** — never bare `var`. This keeps the immutability convention intact.

**Don't use `var` when the type isn't obvious.** If a reader needs to look up the return type to understand the code, spell it out:

```java
// unclear — what does process() return?
final var result = process(data);

// explicit type is better
final ProcessingResult result = process(data);
```

## Immutable Collection Factories

Use `List.of`, `Map.of`, `Set.of` (Java 9) for small immutable collections — they return truly immutable collections and reject nulls:

```java
final var statuses = List.of("ACTIVE", "PENDING", "SUSPENDED");
final var defaults = Map.of("timeout", 30, "retries", 3);
final var tags = Set.of("premium", "verified");
```

Use `List.copyOf`, `Map.copyOf`, `Set.copyOf` (Java 10) for defensive copies that are also immutable:

```java
public Customer(final String id, final List<Order> orders) {
    this.id = id;
    this.orders = List.copyOf(orders); // defensive copy + immutable, one step
}
```

This replaces the Java 8 `Collections.unmodifiableList(new ArrayList<>(orders))` two-step pattern.

For stream results, use `Collectors.toUnmodifiableList/Set/Map()` (Java 10) when you want an immutable result:

```java
final var activeNames = customers.stream()
        .filter(Customer::isActive)
        .map(Customer::getName)
        .collect(Collectors.toUnmodifiableList());
```

Note: `stream().toList()` is Java 16 — not available here. Stick with collectors.

## Streams and Optional — Java 9/11 Additions

Beyond the Java 8 basics, these additions are worth using:

- `Optional.isEmpty()` (Java 11) — clearer than `!opt.isPresent()`
- `Optional.or(() -> alternative)` (Java 9) — chain Optional suppliers
- `Optional.ifPresentOrElse(action, emptyAction)` (Java 9) — handle both cases without `isPresent`
- `Optional.stream()` (Java 9) — convert an Optional to a zero-or-one element stream, useful inside `flatMap`
- `Stream.ofNullable(value)` (Java 9) — zero-or-one element stream, handy in flatMap chains
- `Stream.takeWhile` / `dropWhile` (Java 9) — prefix-based stream slicing on ordered streams
- `Collectors.filtering`, `Collectors.flatMapping` (Java 9) — downstream collectors for `groupingBy`

All the Java 8 functional conventions still apply: prefer streams over loops, method references over trivial lambdas, no side effects inside stream pipelines, and never `.get()` without first making absence impossible through the functional API.

## Predicate.not

Use `Predicate.not` (Java 11) to negate a method reference without wrapping it in a lambda:

```java
import static java.util.function.Predicate.not;

final var nonBlank = lines.stream()
        .filter(not(String::isBlank))
        .collect(Collectors.toUnmodifiableList());
```

This reads better than `.filter(s -> !s.isBlank())` and preserves the method-reference style.

## New String Methods (Java 11)

Prefer these over hand-rolled equivalents:

- `isBlank()` — true if empty or whitespace-only; use instead of `trim().isEmpty()`
- `strip()`, `stripLeading()`, `stripTrailing()` — Unicode-aware, use instead of `trim()` for user-facing text
- `lines()` — returns a `Stream<String>` of lines, better than splitting on `\n` or `\r\n`
- `repeat(int)` — replaces manual loops or `String.join` tricks

```java
if (input.isBlank()) {
    return Optional.empty();
}
final var cleaned = input.strip();
final var lineCount = cleaned.lines().count();
```

## Files — Read/Write Strings Directly

`Files.readString(Path)` and `Files.writeString(Path, CharSequence)` (Java 11) replace the Java 8 dance of `Files.readAllBytes` + `new String(..., UTF_8)`:

```java
final var config = Files.readString(Path.of("config.json"));
Files.writeString(Path.of("out.txt"), report);
```

Both default to UTF-8, which is what you want almost always.

## HttpClient (java.net.http)

Use `java.net.http.HttpClient` (Java 11) instead of `HttpURLConnection` or pulling in Apache HttpClient for simple HTTP calls. It supports HTTP/2, sync and async, and has a clean builder API:

```java
final var client = HttpClient.newBuilder()
        .connectTimeout(Duration.ofSeconds(10))
        .build();

final var request = HttpRequest.newBuilder()
        .uri(URI.create("https://api.example.com/status"))
        .header("Accept", "application/json")
        .GET()
        .build();

final HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
```

For async, use `sendAsync` which returns a `CompletableFuture<HttpResponse<T>>`.

## Local-Variable Syntax for Lambda Parameters

Java 11 allows `var` in lambda parameters, primarily so annotations can be applied:

```java
list.stream().map((@Nonnull var s) -> s.strip())
```

Only use this when you actually need an annotation on the parameter. Plain `s -> s.strip()` is still preferred — adding `var` without a reason is noise.

## java.time API

Use `java.time` (LocalDate, LocalDateTime, Instant, Duration, Period) instead of `Date`/`Calendar`. The old date APIs are mutable and error-prone.

```java
final var today = LocalDate.now();
final var deadline = today.plusDays(30);
final var elapsed = Duration.between(start, end);
```
