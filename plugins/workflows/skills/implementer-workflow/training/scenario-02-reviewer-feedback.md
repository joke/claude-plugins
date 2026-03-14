# Scenario 02: Address Reviewer Feedback

## Input

You submitted your DiscountCalculator implementation for review. The reviewer returned:

```
## What Was Done Well
- Clean structure, good naming

## Findings

### src/main/java/com/example/discount/DiscountCalculator.java:15
🔴 **Missing null check on customer parameter**
- Problem: calculateTotal accepts null customer without validation
- Expected: Validate inputs at method entry per project conventions
- Fix: Add null check with IllegalArgumentException

### src/main/java/com/example/discount/DiscountCalculator.java:22
🟡 **Magic number for discount percentages**
- Problem: 0.10 and 0.20 are hardcoded in the method body
- Expected: Use constants or derive from CustomerType enum
- Fix: Define as constants or use CustomerType.getDiscountRate()

## Summary
- MUST FIX: 1
- SHOULD FIX: 1
- Verdict: CHANGES REQUIRED
```

## Expected Behaviors

- [ ] Addresses the 🔴 MUST FIX item (null check) — this is non-negotiable
- [ ] Addresses the 🟡 SHOULD FIX item (magic numbers)
- [ ] References each point being addressed in the response
- [ ] Re-runs tests after changes to confirm still green
- [ ] Re-submits for review after addressing all feedback

## Anti-patterns

- [ ] Must NOT skip or partially implement any reviewer feedback
- [ ] Must NOT silently ignore the SHOULD FIX item
- [ ] Must NOT modify test files to accommodate the changes
- [ ] Must NOT argue against the MUST FIX without a concrete technical reason
