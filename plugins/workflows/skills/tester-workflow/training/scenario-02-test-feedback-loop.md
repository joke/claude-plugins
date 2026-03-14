# Scenario 02: Incorporate Feedback and Re-enter Review Loop

## Input

You wrote Spock tests for a UserRegistrationService. The implementer reports back:

"The test `'registering a user with an existing email should throw DuplicateEmailException'` is too rigid — it asserts the exact exception message string, but the message includes a timestamp that changes on every run. Can you make the assertion more flexible?"

## Expected Behaviors

- [ ] Acknowledges the implementer's feedback as valid
- [ ] Modifies the test to use a less rigid assertion (e.g., check exception type and that message contains the email, not exact string match)
- [ ] Performs self-review on the modified test
- [ ] Re-enters the review loop by requesting another code review from the reviewer
- [ ] Does NOT hand off back to implementer until reviewer re-approves

## Anti-patterns

- [ ] Must NOT modify production code to fix the issue
- [ ] Must NOT dismiss the implementer's feedback
- [ ] Must NOT skip the review loop after changes
- [ ] Must NOT hand off directly to implementer without reviewer re-approval
