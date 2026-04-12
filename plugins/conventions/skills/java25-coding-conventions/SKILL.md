---
name: java25-coding-conventions
description: >
  Use when writing, reviewing, or modifying Java 25 code. Layers modern Java conventions on top
  of the general java-coding-conventions skill. Covers records, sealed classes, pattern matching,
  switch expressions, text blocks, var, and modern collection factories. Does not cover formatting,
  indentation, or framework-specific patterns.
user-invocable: false
---

# Java 25 Code Conventions

First, use the Skill tool to load `conventions:java-coding-conventions`. Everything below builds on those foundations with modern Java guidance.

## Records for Data Classes

Use `record` for classes that are pure data carriers. Records give you immutability, `equals`/`hashCode`/`toString`, and a compact canonical constructor for free — no boilerplate.

```java
// instead of a manual immutable class with private final fields, constructor, getters, equals, hashCode, toString
public record Customer(String id, String name, List<Order> orders) {

    // compact canonical constructor for validation and defensive copies
    public Customer {
        Objects.requireNonNull(id, "id must not be null");
        orders = List.copyOf(orders); // defensive copy + unmodifiable
    }
}
```

**When to use records:**
- Value objects, DTOs, events, query results, composite keys
- Any class whose identity is defined by its data, not by some external reference

**When NOT to use records:**
- Classes with mutable state or behavior beyond data access
- Classes that need inheritance (records are implicitly final)
- JPA entities (records don't work well with proxying and lazy loading)

**Record conventions:**
- Use the compact canonical constructor (no parameter list) for validation and defensive copies
- Use `List.copyOf`, `Map.copyOf`, `Set.copyOf` in the constructor to freeze collection components
- Record components replace getters — access via `customer.name()` not `customer.getName()`

## Sealed Classes and Interfaces

Use `sealed` to define a closed set of subtypes. This lets the compiler verify exhaustive handling and makes the domain model explicit about what forms a type can take.

```java
public sealed interface PaymentMethod permits CreditCard, BankTransfer, DigitalWallet {
    String displayName();
}

public record CreditCard(String number, String expiry) implements PaymentMethod {
    public String displayName() { return "Credit Card ending " + number.substring(number.length() - 4); }
}

public record BankTransfer(String iban) implements PaymentMethod {
    public String displayName() { return "Bank Transfer to " + iban; }
}

public record DigitalWallet(String provider, String email) implements PaymentMethod {
    public String displayName() { return provider + " (" + email + ")"; }
}
```

Sealed types pair naturally with pattern matching — when you switch over a sealed type, the compiler knows all possible cases.

## Pattern Matching

### instanceof Pattern Matching

Use pattern matching to eliminate redundant casts:

```java
// old style — avoid
if (shape instanceof Circle) {
    final Circle c = (Circle) shape;
    return Math.PI * c.radius() * c.radius();
}

// pattern matching — prefer
if (shape instanceof final Circle c) {
    return Math.PI * c.radius() * c.radius();
}
```

Note the `final` on the pattern variable — consistent with our convention that all variables are final.

### Switch Pattern Matching

Use switch expressions with pattern matching for exhaustive type dispatch:

```java
public double area(final Shape shape) {
    return switch (shape) {
        case Circle c -> Math.PI * c.radius() * c.radius();
        case Rectangle r -> r.width() * r.height();
        case Triangle t -> 0.5 * t.base() * t.height();
    };
}
```

When switching over a sealed type, the compiler enforces exhaustiveness — no `default` needed, and adding a new subtype forces you to handle it everywhere.

**Guarded patterns** for conditional logic within cases:

```java
return switch (response) {
    case Success s when s.data().isEmpty() -> handleEmpty();
    case Success s -> handleData(s.data());
    case Error e -> handleError(e.message());
};
```

## Switch Expressions

Use switch expressions (with `->`) instead of switch statements for all switches, even without pattern matching:

```java
final String label = switch (status) {
    case ACTIVE -> "Active";
    case INACTIVE -> "Inactive";
    case SUSPENDED -> "Suspended";
};
```

The arrow form has no fall-through, returns a value, and the compiler checks exhaustiveness for enums.

## Text Blocks

Use text blocks for multi-line strings — SQL, JSON, HTML, log messages:

```java
final String query = """
        SELECT c.id, c.name, COUNT(o.id) as order_count
        FROM customers c
        LEFT JOIN orders o ON c.id = o.customer_id
        WHERE c.status = 'ACTIVE'
        GROUP BY c.id, c.name
        """;
```

Text blocks strip incidental indentation automatically. Align the closing `"""` to control trailing whitespace.

## Local Variable Type Inference (var)

Use `var` for local variables when the type is obvious from the right-hand side:

```java
final var customers = customerRepository.findAll();        // clearly List<Customer>
final var activeCount = customers.stream().filter(Customer::isActive).count(); // clearly long
final var report = generateReport(customers);              // clearly whatever generateReport returns
```

**Always use `final var`** — never bare `var`. This keeps our immutability convention intact.

**Don't use `var` when the type isn't obvious:**

```java
// unclear — what does process() return?
final var result = process(data);

// explicit type is better here
final ProcessingResult result = process(data);
```

The rule of thumb: if a reader needs to look up the return type to understand the code, spell it out.

## Modern Collection Factories

Use `List.of`, `Map.of`, `Set.of` for creating small immutable collections:

```java
final var statuses = List.of("ACTIVE", "PENDING", "SUSPENDED");
final var defaults = Map.of("timeout", 30, "retries", 3);
final var tags = Set.of("premium", "verified");
```

These return truly immutable collections (no `Collections.unmodifiable*` wrapper needed) and reject null elements.

**Use `List.copyOf`, `Map.copyOf`, `Set.copyOf`** for defensive copies that are also immutable:

```java
public Customer(final String id, final List<Order> orders) {
    this.id = id;
    this.orders = List.copyOf(orders); // defensive copy + immutable
}
```

**Use `Collectors.toUnmodifiableList()`** (or `stream().toList()`) instead of `Collectors.toList()`:

```java
final var activeNames = customers.stream()
        .filter(Customer::isActive)
        .map(Customer::name)
        .toList(); // returns unmodifiable list
```

## Streams — Modern Additions

Java 25 adds useful stream operations beyond Java 8:

- `stream().toList()` — shorthand for `collect(Collectors.toList())`, returns unmodifiable list
- `Stream.ofNullable(value)` — creates a zero-or-one element stream, useful in flatMap chains
- `Collectors.toUnmodifiableList/Set/Map()` — when you need an explicit collector that produces immutable results
- `Optional.stream()` — converts Optional to a zero-or-one element stream
- `Optional.or(() -> alternative)` — chain Optional suppliers
- `Optional.ifPresentOrElse(action, emptyAction)` — handle both cases

## java.time API

Use `java.time` (LocalDate, LocalDateTime, Instant, Duration, Period) instead of `Date`/`Calendar`. The old date APIs are mutable and error-prone.

```java
final var today = LocalDate.now();
final var deadline = today.plusDays(30);
final var elapsed = Duration.between(start, end);
```
