---
name: groovy-coding-conventions
description: >
  Use when writing, reviewing, or modifying Groovy code. Applies general programming
  principles and design conventions. Does not cover formatting or indentation.
user-invocable: false
---

# Groovy Code Conventions

## Typing

- Prefer `@CompileStatic` for performance and safety; use `def` only when dynamic dispatch is genuinely needed
- Type-annotate method signatures even in dynamic code

## Immutability

- Prefer `@Immutable` for data classes
- Use `final` for variables where applicable
- Prefer unmodifiable collections

## Null Handling

- Use safe navigation operator `?.` to avoid NPEs
- Use Elvis operator `?:` for defaults
- Prefer `Optional<T>` when returning absent values from APIs

## Property Access

- **Use Groovy-style property access for JavaBean getter/setter methods** (`obj.name` instead of `obj.getName()`)
- This applies ONLY to getter including boolean getters and setters: `.getName()` → `.name`, `.isFinal()` → `.final`, `.setName(v)` → `.name = v`

## Closures

- Prefer closures for single-method callbacks
- Name closure parameters explicitly (avoid `it` when nesting or when clarity matters)
- Prefer GDK collection methods (`collect`, `findAll`, `each`, `inject`) over manual loops

## Strings

- Use GStrings (`"${expr}"`) for interpolation; single-quoted strings (`'...'`) for all plain string literals with no interpolation
- Never use double quotes (`"..."`) for plain strings; double quotes are only for GString interpolation
- Use multiline strings (`"""..."""`) for templates/SQL/XML

## Collections

- Use native Groovy list (`[a, b]`) and map (`[k: v]`) literals
- Prefer spread operator (`*.method()`) for concise bulk operations

## Design

- Composition over inheritance; inheritance only for true is-a relationships
- Interfaces only when there are multiple implementations or needed for testing
- Constructor injection for DI; no field injection

## Methods

- Each method does exactly one thing; extract named methods over inline logic
- Use `return` keyword explicitly for non-trivial methods (clarity over implicit return)

## Visibility

- Most restrictive access modifier possible; start private, widen only when needed
- Prefer `static` where possible

## Naming

- Standard conventions: `PascalCase` classes, `camelCase` methods/variables, `UPPER_SNAKE_CASE` constants
