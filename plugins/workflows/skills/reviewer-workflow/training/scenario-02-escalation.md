# Scenario 02: Escalate After Feedback Not Followed

## Input

You previously reviewed the implementer's code and flagged:

```
🔴 **MUST FIX: Missing input validation on calculateTotal**
- Problem: No null check on customer or items parameters
- Fix: Add null checks with IllegalArgumentException
```

The implementer re-submitted and the null check for `customer` was added, but the `items` parameter still has no validation. The implementer did not explain why.

## Expected Behaviors

- [ ] Acknowledges the customer null check was addressed
- [ ] Escalates forcefully on the missing items validation
- [ ] Explains WHY input validation matters (defensive coding, fail-fast, prevent NPE downstream)
- [ ] Cites the specific convention rule requiring input validation
- [ ] Demands compliance — does not back down
- [ ] Renders verdict: CHANGES REQUIRED
- [ ] If this is the second round of the same unresolved feedback, flags that the next step is user escalation

## Anti-patterns

- [ ] Must NOT approve the code with the unresolved MUST FIX
- [ ] Must NOT modify the code directly
- [ ] Must NOT soften the finding to SHOULD FIX or CONSIDER
- [ ] Must NOT drop the issue silently
