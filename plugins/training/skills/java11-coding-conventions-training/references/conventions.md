# Java 11 Coding Conventions — Reference

This is the authoritative source for all Java 11-specific conventions. The general Java conventions (immutability, small methods, etc.) are handled by `java-coding-conventions` — this file covers only what Java 11 adds on top of that.

Java 11 is the first LTS after Java 8. Features from Java 9, 10, and 11 are available and preferred over their Java 8 equivalents.

## Java 11 Version Boundary

The following features are NOT available and must NOT appear:

- Records (Java 14)
- Sealed classes (Java 17)
- Pattern matching for `instanceof` (Java 16) or `switch` (Java 21)
- Text blocks (Java 13/15)
- Switch expressions with `->` (Java 14)
- `Stream.toList()` (Java 16) — use `Collectors.toUnmodifiableList()` or `Collectors.toList()`
- `Stream.mapMulti` (Java 16)

## Local Variable Type Inference (var)

- Use `final var` for locals when the type is obvious from the right-hand side.
- Never use bare `var` — always `final var` to preserve immutability.
- Spell out the type when it isn't obvious from the RHS.

## Immutable Collection Factories

- `List.of`, `Map.of`, `Set.of` for small immutable collections (Java 9).
- `List.copyOf`, `Map.copyOf`, `Set.copyOf` for defensive copies (Java 10).
- `Collectors.toUnmodifiableList/Set/Map` for stream results (Java 10).
- Do NOT use `Stream.toList()` — it's Java 16.

## Streams and Optional — Java 9/11 Additions

- `Optional.isEmpty()` (Java 11) instead of `!opt.isPresent()`.
- `Optional.or(Supplier)`, `Optional.ifPresentOrElse`, `Optional.stream()` (Java 9).
- `Stream.ofNullable` (Java 9).
- `Stream.takeWhile` / `dropWhile` (Java 9).
- `Collectors.filtering`, `Collectors.flatMapping` (Java 9).

## Predicate.not

- `Predicate.not(String::isBlank)` over `s -> !s.isBlank()`.

## New String Methods (Java 11)

- `isBlank()` instead of `trim().isEmpty()`.
- `strip()`, `stripLeading()`, `stripTrailing()` instead of `trim()`.
- `lines()` instead of splitting on `\n`.
- `repeat(int)` instead of loops.

## Files — Read/Write Strings

- `Files.readString(Path)` and `Files.writeString(Path, CharSequence)` — default UTF-8.
- Replaces `Files.readAllBytes` + `new String(..., UTF_8)`.

## HttpClient

- Use `java.net.http.HttpClient` (with `HttpRequest`/`HttpResponse`) instead of `HttpURLConnection` or third-party clients.

## java.time API

- Use `java.time` (LocalDate, LocalDateTime, Instant, Duration, Period) instead of `Date`/`Calendar`.
