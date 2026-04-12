---
name: lombok-coding-conventions
description: >
  Lombok-first Java coding conventions. Load whenever writing, modifying, or reviewing
  Java code in a project that has Lombok on the classpath. Trigger on any Java file
  creation, editing, or code generation — even if the user doesn't mention Lombok.
  If `lombok.config` or a Lombok dependency exists in the project, this skill applies.
user-invocable: false
---

# Lombok-First Java Conventions

The guiding principle is simple: **write as little boilerplate as you can**. If Lombok has an annotation for it, use the annotation instead of writing the code by hand. Every explicit getter, setter, constructor, `toString`, `equals`/`hashCode`, logger field, or resource cleanup block that Lombok could generate is wasted code.

The only Lombok features that must **never** be used are `lombok.var` and `lombok.val` — use Java's native `var` instead.

## Detecting Lombok

Before writing Java code, check whether Lombok is available:
- Look for `lombok.config` in the project root
- Check build files (`build.gradle`, `pom.xml`) for a Lombok dependency
- Check if existing source files import from `lombok.*`

If Lombok is present, **all conventions below apply** — regardless of whether the existing code in the file already uses Lombok. When modifying a file that has hand-written boilerplate, refactor it to use Lombok as part of the change.

## Constructor Annotations

Replace hand-written constructors with the matching annotation:

| Scenario | Annotation |
|---|---|
| No-arg constructor | `@NoArgsConstructor` |
| Constructor for all `final` / `@NonNull` fields | `@RequiredArgsConstructor` |
| Constructor for every field | `@AllArgsConstructor` |

### `onConstructor_` for dependency injection

When a constructor needs a framework annotation like `@Inject`, `@Autowired`, or any other qualifier, move it to `onConstructor_` instead of writing the constructor explicitly.

```java
// WRONG — hand-written constructor just to place @Inject
public final class BuildGraphStage {
    @Inject
    BuildGraphStage() {}
}

// CORRECT
@NoArgsConstructor(onConstructor_ = @Inject)
public final class BuildGraphStage {
}
```

```java
// WRONG
public final class GenerateStage {
    private final Filer filer;

    @Inject
    GenerateStage(final Filer filer) {
        this.filer = filer;
    }
}

// CORRECT
@RequiredArgsConstructor(onConstructor_ = @Inject)
public final class GenerateStage {
    private final Filer filer;
}
```

### `staticName` for factory methods

When existing code has a manual static factory method (commonly named `of`, `create`, `from`, etc.) that just delegates to `new`, replace it with `staticName`:

```java
// WRONG — manual factory method
@RequiredArgsConstructor(access = AccessLevel.PRIVATE)
public class Pair<A, B> {
    private final A first;
    private final B second;

    public static <A, B> Pair<A, B> of(A first, B second) {
        return new Pair<>(first, second);
    }
}

// CORRECT
@RequiredArgsConstructor(staticName = "of")
public class Pair<A, B> {
    private final A first;
    private final B second;
}
```

Do **not** add `staticName` by default when there is no existing factory method — only use it to replace one.

### `access` for visibility

Match the constructor visibility to what the code actually needs. If the original constructor was package-private, use `access = AccessLevel.PACKAGE`. If it was `protected`, use `AccessLevel.PROTECTED`. Default (`PUBLIC`) is fine when that matches intent.

## Data Class Annotations

### `@Getter` / `@Setter`

- Place on the class to generate for all fields, or on individual fields for selective generation.
- Prefer class-level when most fields need accessors.
- Use `@Getter(AccessLevel.NONE)` or `@Setter(AccessLevel.NONE)` to exclude specific fields from class-level generation.
- Use `@Getter(lazy = true)` for expensive computations that should be cached.

### `@ToString`

- Use `@ToString` on any class that overrides `toString()` manually.
- Use `@ToString(onlyExplicitlyIncluded = true)` combined with `@ToString.Include` for selective field inclusion — this is preferred over `@ToString.Exclude` when only a few fields matter.
- Use `@ToString.Include(rank = N)` to control field ordering.
- Use `@ToString.Include(name = "alias")` to rename fields in output.
- Use `@ToString(callSuper = true)` when the parent class's toString matters.

### `@EqualsAndHashCode`

- Use `@EqualsAndHashCode` on any class with manual `equals`/`hashCode`.
- Use `@EqualsAndHashCode(onlyExplicitlyIncluded = true)` with `@EqualsAndHashCode.Include` for identity-by-key patterns.
- Use `@EqualsAndHashCode.Exclude` to skip transient or derived fields.
- Use `@EqualsAndHashCode(callSuper = true)` for subclasses where the parent's equality matters.
- Use `@EqualsAndHashCode(cacheStrategy = LAZY)` for immutable objects used heavily in collections.

### `@Data`

Use `@Data` when a class needs `@Getter`, `@Setter`, `@ToString`, `@EqualsAndHashCode`, and `@RequiredArgsConstructor` all at once. This is the go-to for mutable DTOs.

### `@Value`

Use `@Value` for immutable data carriers. It makes the class `final`, fields `private final`, generates getters (no setters), `toString`, `equals`/`hashCode`, and an all-args constructor. Prefer `@Value` over `@Data` for immutable objects.

## Builder Pattern

### `@Builder`

Use `@Builder` instead of hand-written builder classes. Combine with `@Builder.Default` for fields with default values:

```java
@Builder
public class Config {
    @Builder.Default
    private int timeout = 30;
    private String host;
}
```

### `@SuperBuilder`

Use `@SuperBuilder` instead of `@Builder` when the class participates in an inheritance hierarchy and the builder must support setting parent fields.

### `@Singular`

Use `@Singular` on collection fields inside `@Builder`/`@SuperBuilder` classes to generate `addX(item)` methods in addition to `xList(list)`.

## Utility Annotations

### `@Cleanup`

Use `@Cleanup` instead of try-with-resources when it simplifies the code:

```java
@Cleanup InputStream in = new FileInputStream(file);
```

### `@SneakyThrows`

Use `@SneakyThrows` when a checked exception is either impossible in practice or when the caller cannot meaningfully handle it. Especially useful in lambdas and streams where checked exceptions create friction.

### `@Log` (and variants)

Use the appropriate `@Log` variant instead of manually declaring a logger field:

| Logger framework | Annotation |
|---|---|
| `java.util.logging` | `@Log` |
| SLF4J | `@Slf4j` |
| Log4j 2 | `@Log4j2` |
| Commons Logging | `@CommonsLog` |
| Flogger | `@Flogger` |
| JBoss Logging | `@JBossLog` |

### `@Delegate`

Use `@Delegate` to implement the decorator/delegation pattern without boilerplate.

### `@UtilityClass`

Use `@UtilityClass` for classes that contain only static methods. It makes the class final, adds a private constructor that throws, and makes all methods static:

```java
@UtilityClass
public class MathUtils {
    int add(int a, int b) {  // automatically static
        return a + b;
    }
}
```

### `@StandardException`

Use `@StandardException` for exception classes instead of writing the standard constructor set by hand:

```java
@StandardException
public class ProcessingException extends RuntimeException {
}
// Generates: no-arg, (String), (Throwable), (String, Throwable) constructors
```

### `@FieldNameConstants`

Use `@FieldNameConstants` when code references field names as strings (e.g., for criteria queries, reflection, or serialization config).

## What NOT to Use

- **`lombok.var`** / **`lombok.val`** — always use Java's built-in `var` instead.

## Quick Decision Guide

When writing or reviewing Java code, ask:

1. Is there a hand-written constructor? → `@NoArgsConstructor` / `@RequiredArgsConstructor` / `@AllArgsConstructor`
2. Does the constructor have `@Inject` or `@Autowired`? → add `onConstructor_`
3. Is there a manual static factory that just calls `new`? → add `staticName`
4. Are there manual getters/setters? → `@Getter` / `@Setter`
5. Is there a manual `toString`? → `@ToString`
6. Is there a manual `equals`/`hashCode`? → `@EqualsAndHashCode`
7. Is there a manual builder class? → `@Builder` or `@SuperBuilder`
8. Is there a manual logger field? → `@Slf4j` / `@Log4j2` / etc.
9. Is there a try-with-resources with no catch? → consider `@Cleanup`
10. Is there a checked exception being caught just to rethrow as unchecked? → `@SneakyThrows`
11. Is it a utility class with only static methods? → `@UtilityClass`
12. Is it an exception with standard constructors? → `@StandardException`
13. Is it a pure delegation wrapper? → `@Delegate`
14. Does code reference field names as strings? → `@FieldNameConstants`
