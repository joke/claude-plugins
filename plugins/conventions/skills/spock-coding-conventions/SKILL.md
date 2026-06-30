---
name: spock-coding-conventions
description: >
  Use when writing, creating, reviewing, or modifying Spock tests — Groovy
  `*Spec.groovy` specifications, classes that extend `spock.lang.Specification`,
  feature methods with when/then/expect, data-driven `where:` tables, and
  Mock/Stub/Spy collaborators. Load this before authoring or editing any Spock
  test so specs follow our Spock 2.4 house style: skip setup/given, keep value
  assertions in `expect` and interactions in `then`, use strict mocking ended by
  `0 * _`, declare mocks as `Type x = Mock()`, validate every mocked argument
  (never bare `_`), spy the subject for self-calls, and drop `@Unroll`. Trigger
  this for any Spock or Groovy unit-test work even when the user only says
  "write a unit test for this class" and never mentions Spock by name. Builds on
  the groovy-coding-conventions skill for idiomatic Groovy. Does not cover
  production Groovy (use the Groovy skill) or JUnit/Java tests.
user-invocable: false
---

# Spock Test Conventions (Spock 2.4)

First, use the Skill tool to load `conventions:groovy-coding-conventions`. A Spock spec **is** Groovy — every idiom from that skill applies to the test body: `def`, Groovy truth, single-quoted strings, property access, GDK closures, `@Immutable` for fixture data. This skill layers the *testing* discipline on top.

The thread running through all of it: **a test should document exactly how the unit behaves and exactly who it talks to.** Strict, explicit mocking turns the spec into a precise contract — when collaboration changes, the test fails and tells you what moved. Everything below serves that goal, so once you see the reasoning you can apply it past the literal examples.

## The shape of a feature method

A feature method reads top-to-bottom as *arrange → act → assert*, but Spock gives each phase a block. We use them deliberately:

- **No `setup:`/`given:` label.** Spock treats unlabeled statements at the top of a method as the implicit setup block, so the label is pure noise. Construct mocks and the subject as plain statements — the blank line before `when:` is the boundary.
- **`when:` / `then:` carry the action and its *interactions*.** The `when:` block calls the one method under test. The `then:` block holds **only interaction verifications** (`1 * mock.foo(arg)`) and `thrown(...)`.
- **`expect:` carries *value assertions*.** Conditions like `result == 5` or `total > 0` go in an `expect:` block after `then:`, never in `then:`. Separating them keeps "what the unit returned" visually distinct from "who the unit called" — a `then:` block full of `==` checks buries the interaction contract.
- **No `@Unroll`.** Spock 2.4 already unrolls data-driven features and embeds the data-variable values in the reported name. The annotation is redundant; leave it off.

```groovy
def 'charges the order total and returns the transaction id'() {
    PaymentGateway gateway = Mock()
    def service = new CheckoutService(gateway)
    def order = new Order(total: 49.99G)

    when:
    def receipt = service.checkout(order)

    then:
    1 * gateway.charge(49.99G) >> 'txn-123'
    0 * _

    expect:
    receipt.transactionId == 'txn-123'
}
```

When the unit has no collaborators and returns a value, drop `when:`/`then:` entirely and assert in a standalone `expect:`:

```groovy
def 'formats a positive amount with the currency symbol'() {
    def formatter = new MoneyFormatter()

    expect:
    formatter.format(19.99G) == '€19.99'
}
```

## Prefer mocks, and mock strictly

Default every collaborator to a **`Mock`**. A mock both stubs return values and records calls, so it lets you verify the collaboration — which is the point. Reach for a real object only when the collaborator is a trivial value/data class; reach for a `Spy` only to isolate the subject's own methods (see below).

**Strict mocking is non-negotiable: every interaction is explicit, and every `then:` ends with `0 * _`.** That trailing `0 * _` asserts "no other interaction happened on any mock." Without it a test silently tolerates extra calls — exactly the regressions we want to catch. With it, adding an unplanned collaborator call breaks a test until someone declares it on purpose.

```groovy
then:
1 * repository.save(customer) >> customer
1 * eventBus.publish(event)
0 * _                            // nothing else was allowed to happen
```

### Interactions live in `then:` — nowhere else

Declare interactions where the action is verified, so the cause (`when:`) and the expectation sit together.

- **Never put interactions in the setup block.** A `1 * mock.foo()` above `when:` hides the contract from the act/assert pair and reads as configuration rather than verification.
- **Never nest interactions in the `Mock()` initializer.** Inline stubbing like `Mock(Repo) { findById(_) >> row }` (or `Repo repo = Mock() { ... }`) buries behavior in construction and usually leans on `_`. Declare it in `then:` with the real argument instead.

```groovy
// wrong — interaction hidden in the initializer, argument unchecked
CustomerRepository repository = Mock() {
    findById(_) >> customer
}

// right — declared in then, with the actual argument
CustomerRepository repository = Mock()
...
then:
1 * repository.findById('cust-1') >> customer
0 * _
```

### Validate the argument — never `_` as "any"

A mocked/stubbed interaction must pin down the argument it expects. `_` means "any value," which lets a wrong argument slip through and defeats the contract. State the exact value, or constrain it with a code closure.

```groovy
// wrong — accepts any argument
1 * repository.save(_)

// right — the exact argument the unit must pass
1 * repository.save(expectedCustomer)

// right — a constraint when you can't name the exact instance
1 * repository.save({ it.id == 'cust-1' })
```

### `verifyAll` for multiple properties of an argument

When you need to assert several properties of a single argument, wrap them in `verifyAll(it) { ... }` inside the constraint closure. `verifyAll` evaluates *every* condition and reports all failures at once, instead of stopping at the first — far better diagnostics than chained `&&`. For a **single** property, the inline boolean closure is enough; don't reach for `verifyAll`.

```groovy
// multiple properties → verifyAll
1 * repository.save({ Customer c ->
    verifyAll(c) {
        name == 'Ada'
        region == 'eu'
        active
    }
})

// single property → plain closure
1 * auditLog.record({ it.action == 'CHECKOUT' })
```

`verifyAll` is also the right tool in an `expect:` block when you assert several properties of the returned value.

## Mocking static methods

Spock 2.4 mocks statics through the Mockito inline mock maker. Enable it by calling **`SpyStatic(TheClass)`** as a statement at the top of the feature method — it sits with the other setup statements (`SpyStatic` is a method, *not* an `@SpyStatic` annotation, and it does not go in `then:`). Then declare the static interaction in `then:` exactly like any other — validated argument, stubbed return.

```groovy
def 'applies the configured regional tax rate'() {
    SpyStatic(PricingRules)
    def service = new InvoiceService()

    when:
    def total = service.totalWithTax(100G, 'eu')

    then:
    1 * PricingRules.taxRate('eu') >> 0.20G
    0 * _

    expect:
    total == 120G
}
```

(`SpyStatic` requires the Mockito `mock-maker-inline` maker on the test runtime — standard in Spock 2.4 setups.)

## Test the subject in isolation

Each method gets tested **directly and on its own** — never as a side effect of exercising some other method.

- **One feature method per method under test.** If `placeOrder` happens to call `validate` internally, that does not test `validate`. Give `validate` its own feature method that calls it directly. Testing a method only through a caller leaves its edge cases uncovered and couples the tests to the caller's flow.
- **Protected methods are tested separately too.** Groovy lets the spec call a protected method directly (or via a spy). Cover it on its own rather than hoping a public caller exercises every branch.

### Use a `Spy` when a method calls a sibling on the same object

If the method under test calls another method **of the same class**, stub that sibling so you test the one method in isolation — otherwise you're testing two methods at once and a bug in either fails both. A `Spy` wraps a real instance but lets you stub and verify its own methods.

Because the subject is now a mock-like object, its method calls count as interactions under strict mode. The method under test is itself invoked once (by the `when:` block), so close the interaction list with **`1 * subject._`** to account for that entry call; the more specific sibling interactions match first.

```groovy
def 'placeOrder validates the order then persists it'() {
    OrderRepository repository = Mock()
    OrderService service = Spy(constructorArgs: [repository])

    when:
    service.placeOrder(order)

    then:
    1 * service.validate(order)        // sibling method — stubbed on the spy
    1 * repository.persist(order)
    1 * service._                      // accounts for the placeOrder() entry call
    0 * _
}
```

## Exceptions

Capture a thrown exception in `then:` with `thrown(...)`, then assert its details in `expect:` — keeping the type expectation (an interaction-shaped check) and the value assertion (the message) in their respective blocks.

```groovy
def 'rejects a null order'() {
    def service = new CheckoutService(Mock(PaymentGateway))

    when:
    service.checkout(null)

    then:
    def error = thrown(IllegalArgumentException)
    0 * _

    expect:
    error.message == 'order must not be null'
}
```

## Quick checklist

Before finishing a spec, verify:

- [ ] No `setup:` / `given:` label; fixtures are unlabeled statements at the top.
- [ ] No `@Unroll`.
- [ ] Collaborators are `Mock`s; declared as `Type name = Mock()`, not `def name = Mock(Type)`.
- [ ] Every interaction is in a `then:` block — none in setup, none nested in a `Mock()` initializer.
- [ ] Every mocked/stubbed argument is a real value or a constraint closure — no bare `_`.
- [ ] Multiple properties of one argument (or one result) checked with `verifyAll`.
- [ ] Each `then:` block ends with `0 * _`.
- [ ] Value assertions (`==`, `>`, etc.) live in `expect:`, not `then:`.
- [ ] Each method (including protected ones) has its own feature method and is called directly.
- [ ] If the subject calls its own methods, it's a `Spy` and the interactions end with `1 * subject._`.
- [ ] Thrown exceptions captured in `then:`; their message asserted in `expect:`.
