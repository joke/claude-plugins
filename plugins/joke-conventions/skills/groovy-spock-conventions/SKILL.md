---
name: groovy-spock-conventions
description: >
  Use when writing, reviewing, or modifying Spock specifications. Applies
  conventions for structuring feature methods, mocking, and data-driven tests.
user-invocable: false
model: haiku-4.5
---

# Spock Test Conventions

## Pre-flight: Answer These Before Writing Any Code

Before writing the first line of a test class, read the full production source and answer:

**Q1: Does any method call a static utility?**
Check two things:
- Explicit class prefix: `Validate.notBlank(x)`, `ListUtils.unmodifiableList(x)`
- **`import static` declarations at the top of the file**: `import static ListUtils.unmodifiableList` means `unmodifiableList(x)` calls in the code are static calls to `ListUtils` — even though the class name is invisible at the call site.

→ For each static utility found: mark its class name. You will need `SpyStatic(ClassName)` in the relevant feature method.

**Q2: Does any method call another method defined in the same class?**
This includes calls inside lambdas, streams, or predicates: `.filter(c -> isCustomerWithMatchingName(...))` counts.
→ Yes: the subject **must** be declared as `Spy(new Subject(...))` — not plain `new`.

Write the subject declaration **now**, before any feature methods:
```groovy
// Q2 = yes → Spy spec field
@Subject(OrderService)
final orderService = Spy(new OrderService(customerRepository))

// Q2 = no → plain new inline per feature
// @Subject(Address) on the class
```

---

## Feature Method 1: Constructor/Initialization Test

**Always write this first.** It tests that the constructor set all fields correctly — including fields that should be `null`. This is not a "pass-through" test: it verifies the complete post-construction state, especially that optional fields are not accidentally pre-populated.

Construct inline in the feature body with `final`. Use `verifyAll` for 3+ fields:

```groovy
def 'creates customer with required id'() {
    final customer = new Customer('CUST-001')

    expect:
    verifyAll(customer) {
        id == 'CUST-001'
        name == null
        email == null
        address == null
        type == null
    }
}
```

---

## Feature Methods for Methods That Delegate to Static Utilities

When `setName` calls `Validate.notBlank(name)`:
- Use `SpyStatic(Validate)` to intercept and verify the delegation
- Test the **happy path** with `when:/then:` + trailing `expect:` for state

**CRITICAL: Do NOT test exception paths for delegating validators.** When `setName` calls `Validate.notBlank(name)` which throws, the exception comes from the static utility — not from your class. Writing `thrown(IllegalArgumentException)` verifies the static library, not your code. Write ONE happy-path test with `SpyStatic` that verifies the delegation was made.

```groovy
def 'sets name after validating it is not blank'() {
    SpyStatic(Validate)
    final customer = new Customer('CUST-001')

    when:
    customer.name = 'some-name'

    then:
    1 * Validate.notBlank('some-name')
    1 * Validate.notBlank(*_)   // cover overloads called internally
    0 * _

    expect:
    customer.name == 'some-name'
}
```

When `getCustomers` calls `ListUtils.unmodifiableList(...)`:
```groovy
def 'get customers'() {
    SpyStatic(ListUtils)
    List<Customer> customers = Mock()
    List<Customer> unmodifiableCustomers = Mock()

    when:
    final res = orderService.customers

    then:
    1 * customerRepository.customers >> customers
    1 * ListUtils.unmodifiableList(customers) >> unmodifiableCustomers
    1 * orderService._
    0 * _

    expect:
    res == unmodifiableCustomers
}
```

---

## When Q2 = Yes — Spy Changes Everything

When the subject has self-delegation (Q2 = yes), every feature method changes. **Do not use `new Subject(...)` — declare the Spy as a spec field.**

### The `1 * spy._` Rule

**Every `then:` block for the Spy subject MUST include `1 * spy._`** — this intercepts the top-level call on the Spy. Without it, interactions on the Spy go unverified.

This applies to ALL feature methods including simple delegations:

```groovy
// WRONG — uses new, no spy._
OrderService orderService = new OrderService(customerRepository)

def 'add customer'() {
    when: orderService.addCustomer(customer)
    then:
    1 * customerRepository.saveCustomer(customer)
    // ← missing 1 * orderService._ — can't have it without Spy
    0 * _
}

// RIGHT — Spy field, spy._ in every then:
@Subject(OrderService)
final orderService = Spy(new OrderService(customerRepository))

def 'add customer'() {
    Customer customer = Mock()
    when:
    orderService.addCustomer(customer)
    then:
    1 * customerRepository.saveCustomer(customer)
    1 * orderService._      // ← required for every Spy method
    0 * _
}
```

### Internal Self-Delegation — Use Spy to Verify the Call

When `findCustomerByPrefix` calls `isCustomerWithMatchingName` on itself (even inside a lambda):

```groovy
def 'find customer by name'() {
    Customer customer1 = Mock()
    Customer customer2 = Mock()

    when:
    final res = orderService.findCustomerByPrefix('some')

    then:
    1 * customerRepository.customers >> [customer1, customer2]
    1 * orderService.isCustomerWithMatchingName('some', customer1) >> true   // internal — specific
    1 * orderService._      // top-level method — wildcard
    0 * _

    expect:
    !res.empty
    res.get() == customer1
}
```

Rules for Spy interaction lines in `then:`:
- Top-level method (what `when:` calls) → `1 * spy._` (wildcard, **never the method name**)
- Internal methods called by the top-level → specific name and arguments

### Do NOT Test Internal Helper Methods as Standalone Features

If `findCustomerByPrefix` calls `isCustomerWithMatchingName` on itself, verify `isCustomerWithMatchingName` **only** through the delegation line inside `findCustomerByPrefix`'s test. **Never write a separate feature method for an internal helper.**

```groovy
// WRONG — standalone test for internal helper
def 'isCustomerWithMatchingName returns true when ...'() { ... }

// RIGHT — verified only through delegation in the calling method's test
then:
1 * orderService.isCustomerWithMatchingName('some', customer1) >> true
```

---

## Block Structure Rules

**No mocks / no SpyStatic → `expect:` only. Never add `when:/then:/0 * _` to a feature with no interactions.**

**Mocks present → `when:/then:` for interactions, trailing `expect:` for state.**

`and:` after `then:` is still `then:` semantics — **never put state assertions in `and:` after `then:`**. Always use a separate trailing `expect:` block:

```groovy
// WRONG
then:
1 * mock.method()
0 * _
and:
result == expected      // ← still then: semantics, state assertion here is wrong

// RIGHT
then:
1 * mock.method()
0 * _
expect:
result == expected      // ← trailing expect: is correct
```

---

## Exception Verification

Inside `then:`: interactions first → `0 * _` → `thrown`. Exception properties in trailing `expect:`:

```groovy
when:
orderService.badCustomer

then:
1 * orderService._
0 * _
final ex = thrown BadCustomerException

expect:
ex.message == 'Bad customer'
```

---

## Data-Driven Tests — Never Split Scenarios Into Separate Methods

All scenarios for the same behavior go in **one** feature method with a `where:` table:

```groovy
// WRONG — three separate methods
def 'isPremium returns true for VIP'() { ... }
def 'isPremium returns true for PREMIUM'() { ... }
def 'isPremium returns false for STANDARD'() { ... }

// RIGHT — one data-driven feature
def 'is premium'() {
    final customer = new Customer('CUST-001').with(true) {
        type = premiumType
    }
    final res = customer.premium

    expect:
    res == isPremium

    where:
    premiumType || isPremium
    VIP         || true
    PREMIUM     || true
    STANDARD    || false
}
```

Use `.with(true) { ... }` to configure object properties inline for data-driven tests.

---

## Assertions

**Do NOT use `verifyAll` for fewer than 3 assertions.** Use direct assertions for 1–2 properties.

---

## Strict Interaction Verification

Every `then:` block ends with `0 * _`. Never put `0 * _` in `expect:`.

---

## Strings and Variables

- Single-quoted strings for all plain literals
- `final` for all local variables — never `def`
- Use Groovy property access: `customer.name` not `customer.getName()`
- Static imports for enum constants: `import static com.example.CustomerType.*`

---

## Mock vs Spy vs SpyStatic Summary

| Situation | Tool |
|---|---|
| External dependency (repository, service) | `Mock()` as spec field |
| Subject has self-delegation (Q2=yes) | `Spy(new Subject(...))` as spec field; `1 * spy._` in every `then:` |
| Subject calls static utility (explicit or `import static`) | `SpyStatic(ClassName)` before `when:` |
| Simple return value only (no interaction needed) | `Stub()` inline |
