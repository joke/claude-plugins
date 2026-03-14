# Scenario 01: New Feature — Add Email Notification Service

## Input

You are working on a Spring Boot application. The user wants to add an email notification service that sends order confirmation emails when orders are submitted.

The codebase has:
- `src/main/java/com/example/order/OrderService.java` — existing order processing
- `src/main/java/com/example/order/OrderRepository.java` — data access
- `docs/architecture/README.md` — architecture docs
- No existing notification infrastructure

User message: "I want to add email notifications when orders are confirmed."

## Expected Behaviors

- [ ] Researches the codebase before proposing anything (reads architecture docs, recent commits, relevant code)
- [ ] Proposes 5 options/directions to plan next
- [ ] Asks clarifying questions (scope, edge cases, constraints)
- [ ] Produces architectural direction with all 4 sections: Requirements, Structure, Constraints, Rationale
- [ ] Requirements describe behaviors, not implementation (e.g., "send confirmation when order is submitted" not "call emailService.send()")
- [ ] Structure defines components and boundaries (e.g., NotificationService interface, EmailNotificationService implementation)
- [ ] Constraints specify patterns (e.g., "use dependency injection", "notification must not block order processing")
- [ ] Rationale explains why decisions serve maintainability
- [ ] Does NOT proceed to detailed plan without explicit user approval
- [ ] Loads architecture/convention skills before designing

## Anti-patterns

- [ ] Must NOT write any code (no Java, no Groovy, no pseudocode with method signatures)
- [ ] Must NOT assign specific tasks ("tester, write a test for X", "implementer, create class Y")
- [ ] Must NOT reference specific lines of code
- [ ] Must NOT skip the research phase
- [ ] Must NOT skip interactive planning and jump straight to a detailed plan
- [ ] Must NOT provide implementation snippets even if asked
