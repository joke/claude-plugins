# Scenario 01: Write Failing Tests for a Discount Calculator

## Input

The architect has broadcast the following requirements:

```
### Requirements
- The system must calculate discounts based on customer type (REGULAR, PREMIUM, VIP)
- REGULAR customers get no discount
- PREMIUM customers get 10% discount
- VIP customers get 20% discount
- Discount must not apply to already-discounted items

### Structure
- DiscountCalculator component responsible for discount logic
- Takes a Customer and list of OrderItems as input
- Returns the total discounted price as BigDecimal

### Constraints
- Follow existing naming patterns in the codebase
- Use BigDecimal for all monetary calculations
```

The project uses Groovy with Spock for testing.

## Expected Behaviors

- [ ] Loads coding convention skills before writing any test code
- [ ] Writes test code that FAILS (red phase) — tests behavior that doesn't exist yet
- [ ] Tests cover all customer types (REGULAR, PREMIUM, VIP)
- [ ] Tests cover the edge case of already-discounted items
- [ ] Uses descriptive test method names documenting expected behavior
- [ ] Performs self-review against loaded conventions before requesting external review
- [ ] Verifies tests actually fail by running them
- [ ] Requests code review after self-review passes
- [ ] Does NOT proceed to implementer handoff until reviewer approves

## Anti-patterns

- [ ] Must NOT write production code (no DiscountCalculator implementation)
- [ ] Must NOT modify any existing source files
- [ ] Must NOT write tests that pass without implementation (that's not red phase)
- [ ] Must NOT skip the self-review step
- [ ] Must NOT hand off to implementer before reviewer approval
