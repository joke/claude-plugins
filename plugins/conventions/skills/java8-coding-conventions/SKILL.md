---
name: java8-coding-conventions
description: >
  Use when writing, reviewing, or modifying Java 8 code. Applies functional programming
  principles, immutability, and design conventions for Java 8 codebases. Does not cover
  formatting, indentation, or framework-specific patterns.
user-invocable: false
model: haiku-4.5
---

# Java 8 Code Conventions

These conventions produce code that is small, immutable, functional, and easy to reason about. Java 8 introduced lambdas, streams, and Optional — lean into them fully. When code reads like a description of *what* it does rather than *how* it does it, you're on the right track.

## Variables and Parameters

Every variable and parameter is `final`. No exceptions — this eliminates reassignment bugs and makes data flow obvious at a glance.

```java
// parameters
public String format(final String name, final int count) { ... }

// local variables
final List<String> names = getNames();
final String result = process(names);
```

## Immutability

Classes are immutable by default. All fields are `private final`, set through the constructor, with no setters. When a class needs to expose a collection, return an unmodifiable view.

```java
public class Customer {
    private final String id;
    private final String name;
    private final List<Order> orders;

    public Customer(final String id, final String name, final List<Order> orders) {
        this.id = id;
        this.name = name;
        this.orders = Collections.unmodifiableList(new ArrayList<>(orders));
    }

    public List<Order> getOrders() {
        return orders; // already unmodifiable
    }
}
```

The constructor makes a defensive copy of mutable inputs (`new ArrayList<>(orders)`) and wraps it in `Collections.unmodifiableList`. This ensures the caller can't mutate internal state after construction.

For collections that you build internally, wrap them before storing or returning:
- `Collections.unmodifiableList(...)` / `Collections.unmodifiableMap(...)` / `Collections.unmodifiableSet(...)`

## Functional Style and Streams

Prefer streams over loops for collection processing. Streams express *what* you want, not *how* to iterate — they compose naturally and avoid mutable accumulators.

```java
// imperative — avoid
final List<String> result = new ArrayList<>();
for (final Customer c : customers) {
    if (c.isActive()) {
        result.add(c.getName().toUpperCase());
    }
}

// functional — prefer
final List<String> result = customers.stream()
        .filter(Customer::isActive)
        .map(Customer::getName)
        .map(String::toUpperCase)
        .collect(Collectors.toList());
```

**Method references over lambdas** when the lambda just delegates to an existing method. `Customer::isActive` is clearer than `c -> c.isActive()` because it names the operation directly.

**Extract complex predicates and mappers** into named methods rather than writing multi-line lambdas inline:

```java
// hard to read inline
final List<Order> result = orders.stream()
        .filter(o -> o.getTotal() > 100 && o.getStatus() == CONFIRMED && !o.isExpired())
        .collect(Collectors.toList());

// extract the predicate — now the stream reads like prose
final List<Order> result = orders.stream()
        .filter(this::isHighValueConfirmed)
        .collect(Collectors.toList());

private boolean isHighValueConfirmed(final Order order) {
    return order.getTotal() > 100
            && order.getStatus() == CONFIRMED
            && !order.isExpired();
}
```

**No side effects in streams.** Never use `forEach` to accumulate into an external collection or mutate state. Use `collect`, `reduce`, or `toMap` instead.

**Useful collectors** — know these well:
- `Collectors.toList()`, `Collectors.toSet()` — basic collection
- `Collectors.toMap(keyFn, valueFn)` — build maps
- `Collectors.groupingBy(classifier)` — group elements
- `Collectors.joining(delimiter)` — concatenate strings
- `Collectors.partitioningBy(predicate)` — split into true/false groups

## Optional

Return `Optional<T>` instead of null when a value may be absent. This makes the possibility of absence explicit in the type signature — callers can't accidentally forget to handle it.

```java
public Optional<Customer> findById(final String id) {
    return customers.stream()
            .filter(c -> c.getId().equals(id))
            .findFirst();
}
```

**Chain Optional operations** — use `map`, `flatMap`, `filter`, and `orElse`/`orElseGet` instead of `isPresent` + `get`:

```java
// imperative — avoid
final Optional<Customer> customer = findById(id);
if (customer.isPresent()) {
    return customer.get().getName();
}
return "unknown";

// functional — prefer
return findById(id)
        .map(Customer::getName)
        .orElse("unknown");
```

**Never call `.get()` without `.isPresent()`** — but even better, avoid both by using the functional API. If you find yourself writing `if (opt.isPresent()) { opt.get()... }`, rewrite it with `map`/`flatMap`/`orElse`.

**`orElse` vs `orElseGet`** — use `orElse` for cheap constants, `orElseGet` when the fallback is expensive (it takes a `Supplier` and only evaluates on absence).

**Don't use Optional for fields or parameters** — it's designed for return types. For fields, use a meaningful default or handle absence in the constructor.

## Small Methods

Each method does exactly one thing. If you need the word "and" to describe what a method does, split it. Method names describe *what* the method does, not *how*.

```java
// too much — does filtering AND mapping AND formatting
public String getActiveCustomerReport(final List<Customer> customers) {
    final List<Customer> active = customers.stream()
            .filter(Customer::isActive)
            .collect(Collectors.toList());
    final Map<String, Long> countsByRegion = active.stream()
            .collect(Collectors.groupingBy(Customer::getRegion, Collectors.counting()));
    return countsByRegion.entrySet().stream()
            .map(e -> e.getKey() + ": " + e.getValue())
            .collect(Collectors.joining("\n"));
}

// split into focused methods
public String getActiveCustomerReport(final List<Customer> customers) {
    final List<Customer> active = filterActive(customers);
    final Map<String, Long> countsByRegion = countByRegion(active);
    return formatReport(countsByRegion);
}

private List<Customer> filterActive(final List<Customer> customers) {
    return customers.stream()
            .filter(Customer::isActive)
            .collect(Collectors.toList());
}

private Map<String, Long> countByRegion(final List<Customer> customers) {
    return customers.stream()
            .collect(Collectors.groupingBy(Customer::getRegion, Collectors.counting()));
}

private String formatReport(final Map<String, Long> counts) {
    return counts.entrySet().stream()
            .map(e -> e.getKey() + ": " + e.getValue())
            .collect(Collectors.joining("\n"));
}
```

## Functional Interfaces

Use `@FunctionalInterface` on custom single-method interfaces. This documents intent and lets the compiler catch accidental additions of abstract methods.

Prefer the standard `java.util.function` types when they fit:
- `Function<T, R>` — transform T to R
- `Predicate<T>` — test T, return boolean
- `Consumer<T>` — accept T, return nothing
- `Supplier<T>` — produce T from nothing
- `UnaryOperator<T>` — transform T to T
- `BiFunction<T, U, R>`, `BiPredicate<T, U>` — two-argument variants

Compose them with `and()`, `or()`, `negate()` (Predicate) and `andThen()`, `compose()` (Function):

```java
final Predicate<Customer> isActiveHighValue = Customer::isActive
        .and(c -> c.getTotal() > 1000);
```

## Exceptions

Only unchecked exceptions (`RuntimeException` subclasses). Checked exceptions pollute every signature in the call chain and break functional interfaces (lambdas can't throw checked exceptions without ugly wrappers).

Create domain-specific unchecked exceptions when the caller might need to distinguish error types:

```java
public class CustomerNotFoundException extends RuntimeException {
    public CustomerNotFoundException(final String id) {
        super("Customer not found: " + id);
    }
}
```

## Design

- **Composition over inheritance.** Inheritance only for true is-a relationships.
- **Interfaces only when needed** — when there are multiple implementations or for testing seams.
- **Constructor injection for dependencies.** No field injection, no setter injection.
- **Most restrictive visibility.** Start `private`, widen only when needed.
- **Prefer `static`** for methods that don't use instance state — it signals that the method is a pure function of its arguments.

## java.time API

Use `java.time` (LocalDate, LocalDateTime, Instant, Duration, Period) instead of `Date`/`Calendar`. The old date APIs are mutable and error-prone.

```java
final LocalDate today = LocalDate.now();
final LocalDate deadline = today.plusDays(30);
final Duration elapsed = Duration.between(start, end);
```

## Imports

- **Static imports** when the import name is self-explanatory: `PI`, `UTF_8`, `format`, `assertEquals`, `emptyList`, `singletonList`
- **Qualified access** when the class name adds clarity: `Collections.unmodifiableList`, `Collectors.toList`, `Duration.ofSeconds`, `Optional.empty`

## Naming

Standard Java conventions:
- `PascalCase` for classes and interfaces
- `camelCase` for methods and variables
- `UPPER_SNAKE_CASE` for constants (`static final`)
