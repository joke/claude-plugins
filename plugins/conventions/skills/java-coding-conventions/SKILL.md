---
name: java-coding-conventions
description: >
  Use when writing, reviewing, or modifying Java code regardless of Java version. Applies
  immutability, small methods, composition, and strict coding discipline. Trigger this skill
  for any Java work — it covers the universal conventions that every Java version should follow.
  Does not cover formatting, indentation, or framework-specific patterns.
user-invocable: false
---

# Java Code Conventions

These conventions produce code that is small, immutable, and easy to reason about. They apply to all Java versions — version-specific skills layer additional conventions on top.

## Variables and Parameters

Every variable and parameter is `final`. No exceptions — this eliminates reassignment bugs and makes data flow obvious at a glance.

```java
// parameters
public String format(final String name, final int count) { ... }

// local variables
final List<String> names = getNames();
final String result = process(names);

// catch blocks
try {
    ...
} catch (final IllegalArgumentException e) {
    ...
}
```

This is the single most important convention. When every binding is immutable, you can read any method top-to-bottom and know that a variable's value never changes after assignment.

## Immutability

Classes are immutable by default. All fields are `private final`, set through the constructor, with no setters. When a class needs to change, return a new instance instead of mutating.

```java
public class Customer {
    private final String id;
    private final String name;
    private final List<Order> orders;

    public Customer(final String id, final String name, final List<Order> orders) {
        this.id = id;
        this.name = name;
        this.orders = copyUnmodifiable(orders);
    }

    public List<Order> getOrders() {
        return orders; // already unmodifiable from constructor
    }
}
```

The constructor makes a defensive copy of mutable inputs and wraps them to prevent mutation. How you do this depends on your Java version (the version-specific skill will specify the exact API), but the principle is always: **copy in, freeze, expose read-only**.

## Small Methods

Each method does exactly one thing. If you need the word "and" to describe what a method does, split it. Method names describe *what* the method does, not *how*.

```java
// too much — filtering AND counting AND formatting
public String getActiveCustomerReport(final List<Customer> customers) {
    // ... 20 lines doing three things
}

// split into focused methods
public String getActiveCustomerReport(final List<Customer> customers) {
    final List<Customer> active = filterActive(customers);
    final Map<String, Long> countsByRegion = countByRegion(active);
    return formatReport(countsByRegion);
}
```

The calling method reads like a high-level description of the algorithm. Each helper method is small, testable, and reusable.

**Extract complex predicates and mapping logic** into named private methods rather than writing multi-line inline expressions. When the logic is non-trivial, giving it a name makes the calling code read like prose.

## Exceptions

Only unchecked exceptions (`RuntimeException` subclasses). Checked exceptions pollute every signature in the call chain and break functional interfaces — lambdas can't throw checked exceptions without ugly wrappers.

Create domain-specific unchecked exceptions when the caller might need to distinguish error types:

```java
public class CustomerNotFoundException extends RuntimeException {
    public CustomerNotFoundException(final String id) {
        super("Customer not found: " + id);
    }
}
```

## Design

- **Composition over inheritance.** Use inheritance only for true is-a relationships. Prefer delegating to collaborators over extending base classes.
- **Interfaces only when needed** — when there are multiple implementations or you need a testing seam. Don't create an interface for every class.
- **Constructor injection for dependencies.** No field injection, no setter injection. The constructor declares exactly what a class needs to work.
- **Most restrictive visibility.** Start `private`, widen only when needed. Package-private before `protected`, `protected` before `public`.
- **Prefer `static`** for methods that don't use instance state — it signals that the method is a pure function of its arguments.

## Imports

- **Static imports** when the import name is self-explanatory: `PI`, `UTF_8`, `format`, `assertEquals`, `emptyList`, `singletonList`
- **Qualified access** when the class name adds clarity: `Collections.unmodifiableList`, `Collectors.toList`, `Duration.ofSeconds`, `Optional.empty`

The rule of thumb: if removing the class qualifier makes the code harder to understand, keep it qualified.

## Naming

Standard Java conventions:
- `PascalCase` for classes and interfaces
- `camelCase` for methods and variables
- `UPPER_SNAKE_CASE` for constants (`static final`)

Method names describe *what* they return or do, not *how*: `calculateTotal` not `loopAndSum`, `findActiveCustomers` not `filterListForActive`.
