# Null Safety Conventions — Reference

This is the authoritative source for all null safety conventions using NullAway + JSpecify.

## Core Rules

1. **Never suppress NullAway** — no `@SuppressWarnings("NullAway")` ever. Fix the code instead.
2. **Every package gets `package-info.java` with `@NullMarked`** — this enables non-null-by-default for the entire package.
3. **`@Nullable` on everything that can be null** — fields, parameters, return types. Import from `org.jspecify.annotations.Nullable` only.
4. **Null-safe handling is mandatory** — every nullable reference must be guarded before access: null check, Optional, or ternary.

## Package-Level Setup

Every package must have:
```java
@NullMarked
package com.example.mypackage;

import org.jspecify.annotations.NullMarked;
```

## Annotation Import

Only use JSpecify:
- `org.jspecify.annotations.NullMarked`
- `org.jspecify.annotations.Nullable`

Do NOT use: `javax.annotation.Nullable`, `org.jetbrains.annotations.Nullable`, `edu.umd.cs.findbugs.annotations.Nullable`, `android.support.annotation.Nullable`.

Do NOT use `@NonNull` — it's redundant under `@NullMarked`.

## Handling Patterns

- Explicit null checks: `if (x != null) { ... }`
- Optional bridge: `Optional.ofNullable(nullable).map(...).orElse(...)`
- Constructor validation: `Objects.requireNonNull(x, "x must not be null")` for non-null params
- Nullable fields in class: annotate with `@Nullable`, handle at every access point
