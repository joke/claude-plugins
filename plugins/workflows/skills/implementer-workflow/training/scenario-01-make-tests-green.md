# Scenario 01: Implement Code to Make Failing Tests Pass

## Input

The tester has handed off failing Spock tests for a `DiscountCalculator`:

```
Test files:
- src/test/groovy/com/example/discount/DiscountCalculatorTest.groovy

Tests expect:
- DiscountCalculator.calculateTotal(Customer, List<OrderItem>) returns BigDecimal
- REGULAR customers: no discount applied
- PREMIUM customers: 10% discount on eligible items
- VIP customers: 20% discount on eligible items
- Already-discounted items are not further discounted

Architect's direction:
- DiscountCalculator is a standalone component
- Uses BigDecimal for monetary calculations
- Follows existing naming patterns
```

## Expected Behaviors

- [ ] Loads coding convention skills before writing any code
- [ ] Reviews existing code in the area for consistency
- [ ] Reads and understands the failing tests before implementing
- [ ] Writes production code that makes all tests pass
- [ ] Performs internal code review (self-check against loaded conventions)
- [ ] Runs tests to confirm green
- [ ] Requests code review from the reviewer after tests pass
- [ ] Follows the architect's structural direction (standalone component, BigDecimal)

## Anti-patterns

- [ ] Must NOT modify test files
- [ ] Must NOT skip the internal code review step
- [ ] Must NOT silently ignore reviewer feedback
- [ ] Must NOT deviate from the architect's structural direction without raising a concern
- [ ] Must NOT work around bad tests — instead communicate back to the tester
