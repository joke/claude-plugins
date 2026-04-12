---
name: null-safety-coding-conventions
description: >
  Use when writing or modifying Java code in projects that use Uber's NullAway with JSpecify
  annotations. Covers @NullMarked package-info.java, @Nullable annotations, and null-safe
  handling patterns. Trigger this whenever you see NullAway in the build config, JSpecify
  imports, or @NullMarked/@Nullable annotations in existing code.
user-invocable: false
---

# Null Safety Conventions (NullAway + JSpecify)

These conventions apply to projects using [NullAway](https://github.com/uber/NullAway) for compile-time null checking with [JSpecify](https://jspecify.dev/) annotations. NullAway treats every reference as non-null by default — the annotations exist to mark the exceptions and the compiler enforces correctness. The result is code where null pointer exceptions become compile errors instead of runtime surprises.

## Never Suppress NullAway

Never use `@SuppressWarnings("NullAway")`. If NullAway flags something, the code has a real nullability issue that needs fixing — suppressing the warning just hides a potential NPE. Fix the root cause instead.

```java
// NEVER do this
@SuppressWarnings("NullAway")
public String getName() {
    return name; // if NullAway complains, name might actually be null — fix it
}
```

If NullAway reports a false positive (rare), restructure the code so NullAway can verify it. The tool is right far more often than not, and every suppression is a potential NPE waiting to happen.

## Package-Level @NullMarked

Every package must have a `package-info.java` that applies `@NullMarked`. This tells NullAway that all types in the package are non-null by default — you only need to annotate the exceptions with `@Nullable`.

```java
// com/example/service/package-info.java
@NullMarked
package com.example.service;

import org.jspecify.annotations.NullMarked;
```

When creating a new package or adding files to a package that lacks `package-info.java`, create it. This is not optional — without `@NullMarked`, NullAway's checking is significantly weaker for that package.

## @Nullable Annotations

Any field, parameter, or return type that can legitimately be null must be annotated with `@Nullable`. This makes the contract explicit — callers and implementors can see at a glance where null is possible.

```java
import org.jspecify.annotations.Nullable;

public class Customer {
    private final String id;                    // never null
    private final String name;                  // never null
    private final @Nullable String nickname;    // may be null
    private final @Nullable LocalDate birthday; // may be null
}
```

**Where to use `@Nullable`:**
- Fields that may hold null
- Method parameters that accept null
- Method return types that may return null
- Type arguments when the element can be null: `List<@Nullable String>`

**Where NOT to use `@Nullable`:**
- Everything else. Under `@NullMarked`, non-null is the default. Don't annotate things as `@NonNull` — it's redundant and clutters the code.

## Null-Safe Handling

Every access to a `@Nullable` reference must be guarded. NullAway enforces this at compile time — code that dereferences a nullable without a check won't compile.

### Explicit null checks

The simplest approach — check and branch:

```java
public String getDisplayName(final @Nullable String nickname, final String fullName) {
    if (nickname != null) {
        return nickname;
    }
    return fullName;
}
```

### Optional for return types

When a method may not have a result, return `Optional` instead of a nullable. This makes absence part of the type and composes well with functional chains:

```java
public Optional<String> findNickname(final String userId) {
    final @Nullable String nickname = repository.getNickname(userId);
    return Optional.ofNullable(nickname);
}
```

Use `Optional.ofNullable()` to bridge from a `@Nullable` value into the Optional world. From there, chain with `map`, `flatMap`, `filter`, `orElse`.

### Functional style

For nullable fields that need transformation, use Optional as a bridge:

```java
public String formatBirthday() {
    return Optional.ofNullable(birthday)
            .map(DateTimeFormatter.ISO_LOCAL_DATE::format)
            .orElse("not provided");
}
```

### Constructor validation

For fields that must not be null, validate in the constructor. `Objects.requireNonNull` documents the contract and fails fast:

```java
public Customer(final String id, final String name, final @Nullable String nickname) {
    this.id = Objects.requireNonNull(id, "id must not be null");
    this.name = Objects.requireNonNull(name, "name must not be null");
    this.nickname = nickname; // nullable — no check needed
}
```

## Annotations Import

Always import from JSpecify:

```java
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;
```

Do not use annotations from other packages (`javax.annotation`, `org.jetbrains.annotations`, `edu.umd.cs.findbugs.annotations`, etc.) — JSpecify is the standard that NullAway supports natively.
