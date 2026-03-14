# Scenario 01: Review Spock Test Code

## Input

The tester submits test code for review:

```groovy
class DiscountCalculatorTest extends Specification {

    def "test discount"() {
        given:
        def calc = new DiscountCalculator()
        def customer = new Customer(type: CustomerType.PREMIUM)
        def items = [new OrderItem(price: 100.0, quantity: 1)]

        when:
        def result = calc.calculateTotal(customer, items)

        then:
        result == 90.0
    }
}
```

The project uses the groovy-spock-coding-conventions skill which requires:
- Descriptive test names documenting behavior
- `@Subject` annotation on SUT
- `0 * _` at end of then blocks for strict interaction verification
- `and:` labels to separate logical groups
- BigDecimal for monetary values (not double/float)

## Expected Behaviors

- [ ] Loads coding convention skills before reviewing
- [ ] Acknowledges what was done well (basic structure is correct, given/when/then blocks)
- [ ] Flags non-descriptive test name as 🔴 MUST FIX
- [ ] Flags missing `@Subject` annotation as 🔴 MUST FIX
- [ ] Flags missing `0 * _` at end of then block as 🔴 MUST FIX
- [ ] Flags use of `100.0` (double) instead of `new BigDecimal("100.00")` as 🔴 MUST FIX
- [ ] Provides concrete fixes for each finding
- [ ] References exact file/line numbers
- [ ] Renders verdict: CHANGES REQUIRED (due to MUST FIX items)
- [ ] Uses the structured output format (What Was Done Well, Findings, Summary)

## Anti-patterns

- [ ] Must NOT modify the code directly
- [ ] Must NOT approve code with MUST FIX violations
- [ ] Must NOT skip acknowledging what was done well
- [ ] Must NOT provide feedback without severity ratings
- [ ] Must NOT make architectural decisions (that's the architect's domain)
