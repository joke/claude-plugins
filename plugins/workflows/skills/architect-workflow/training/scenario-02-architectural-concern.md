# Scenario 02: Handling an Architectural Concern from a Teammate

## Input

You have already broadcast your architectural direction for adding a caching layer to the OrderService. The tester raises a concern:

"The caching strategy you proposed uses a simple in-memory cache, but the OrderService is deployed across 3 instances behind a load balancer. Won't this cause stale reads across instances?"

## Expected Behaviors

- [ ] Takes the concern seriously and considers it
- [ ] Acknowledges the validity of the concern (distributed caching vs in-memory)
- [ ] Adjusts the architecture if warranted (e.g., switch to distributed cache like Redis, or add cache invalidation strategy)
- [ ] Re-broadcasts updated architectural direction with all 4 sections
- [ ] Explains the rationale for the adjustment
- [ ] If the concern is not valid, explains why and holds firm with reasoning

## Anti-patterns

- [ ] Must NOT dismiss the concern without explanation
- [ ] Must NOT write code to solve the caching problem
- [ ] Must NOT assign the tester a task like "update your tests for Redis"
- [ ] Must NOT make implementation-level decisions (e.g., "use Jedis client" or "set TTL to 300s")
