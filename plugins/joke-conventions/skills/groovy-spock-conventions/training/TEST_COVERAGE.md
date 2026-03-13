# Spock Test Coverage - Training Classes

This document describes the comprehensive set of Java classes created to validate the groovy-spock-conventions skill. Each class exposes different testing patterns and scenarios that should be covered by Spock tests.

## Order Management System

### Core Domain Classes

#### `Order.java`
- **Purpose**: Represents an order with multiple items
- **Test Scenarios**:
  - Add/remove items from an order
  - State management (status transitions)
  - Validation of order state
  - Nested object collections (OrderItem list)
  - Complex business rules (total recalculation)

#### `OrderItem.java`
- **Purpose**: Represents a line item in an order
- **Test Scenarios**:
  - Constructor validation (quantity > 0)
  - Total calculation (quantity × price)
  - Stock validation
  - Negative test cases (invalid inputs)

#### `Customer.java`
- **Purpose**: Customer with email validation and type classification
- **Test Scenarios**:
  - Email validation (regex pattern matching)
  - Static utility methods (`isValidEmail`)
  - Type-based behavior (isPremium)
  - Nested object (Address)
  - Property setters with validation
  - Enum usage (CustomerType)

#### `Product.java`
- **Purpose**: Product with inventory management
- **Test Scenarios**:
  - Price validation (must be positive)
  - Stock management (reduce, increase)
  - Exception throwing (OutOfStockException)
  - State queries (isInStock)
  - Immutable ID with mutable properties

#### `Address.java`
- **Purpose**: Address nested within Customer
- **Test Scenarios**:
  - Complex object composition
  - Multi-field validation (isComplete)
  - String concatenation and formatting
  - Read-only properties

#### `OrderStatus.java`
- **Purpose**: Enum with state transition logic
- **Test Scenarios**:
  - Enum values and properties
  - State machine behavior (canTransitionTo)
  - Final state detection
  - Business rules encoded in enums

#### `CustomerType.java`
- **Purpose**: Enum with discount mapping
- **Test Scenarios**:
  - Enum with associated data (discount percentage)
  - Behavior classification

### Service Classes

#### `OrderService.java`
- **Purpose**: Core business logic orchestrating orders
- **Test Scenarios**:
  - Dependency injection (OrderRepository, InventoryService, NotificationService)
  - Complex workflows (createOrder → addItem → submitOrder)
  - State transitions with validation
  - Cache management
  - Private method calls (validateAddItem, validateInventory, etc.)
  - Exception handling and custom exceptions
  - Method chaining and return values
  - Mock interactions for dependencies
  - Spy usage for testing private methods
  - Transactional behavior (reserve/release inventory)

**Key Testing Patterns**:
- Multiple mock interactions in single test
- Return type verification
- State assertion followed by behavior verification
- Dependency side-effects verification

### Repositories & Interfaces

#### `OrderRepository.java`
- **Purpose**: Data access interface
- **Test Scenarios**:
  - Mock interface methods
  - Optional return types
  - Save/retrieve/delete patterns

#### `InventoryService.java`
- **Purpose**: Inventory management interface
- **Test Scenarios**:
  - Dependency mocking
  - Method call verification
  - State side-effects

#### `NotificationService.java`
- **Purpose**: Notification interface
- **Test Scenarios**:
  - Verify notifications sent at correct times
  - Argument capturing and verification
  - Async behavior patterns

### Exception Classes

#### `OutOfStockException.java`
- **Purpose**: Custom exception for inventory
- **Test Scenarios**:
  - Exception throwing and catching
  - Custom exception messages
  - Exception chaining

---

## Discount System

### Domain Classes

#### `DiscountCode.java`
- **Purpose**: Represents a discount code with expiry
- **Test Scenarios**:
  - Date-based validation (isValid, isExpired)
  - Counter tracking (usageCount)
  - State mutation (expire)
  - Time-sensitive behavior

### Service Classes

#### `DiscountService.java`
- **Purpose**: Discount code management with caching
- **Test Scenarios**:
  - Cache hit/miss verification
  - Complex business logic
  - Multiple return types (boolean, BigDecimal)
  - Cache clearing
  - Dependency on validation service
  - Exception throwing for invalid codes
  - Spy testing for private methods (validateInput)
  - State mutation (increment usage, expire codes)

**Key Testing Patterns**:
- Cache verification with mock inspection
- Calculation logic with BigDecimal
- State-based testing
- Dependency mock verification

### Repository & Service Interfaces

#### `DiscountRepository.java`
- **Purpose**: Discount data access
- **Test Scenarios**:
  - Mock repository behavior
  - Save and retrieve patterns

#### `ValidationService.java`
- **Purpose**: Validation logic interface
- **Test Scenarios**:
  - Stub for simple return values
  - Boolean return type patterns

### Exception Classes

#### `InvalidDiscountException.java`
- **Purpose**: Custom exception for discount validation
- **Test Scenarios**:
  - Exception handling and verification

---

## Skill Coverage Matrix

| Feature | Class(es) | Test Pattern |
|---------|-----------|--------------|
| **Basic CRUD** | Order, Product, Customer | Simple when/then verification |
| **Nested Objects** | Customer+Address, Order+OrderItem | Object graph traversal in assertions |
| **Enums** | OrderStatus, CustomerType | Enum behavior and state machines |
| **Validation** | Multiple classes | Exception throwing and catching |
| **Interfaces & Mocking** | OrderService, DiscountService | Mock dependency verification |
| **State Management** | Order, DiscountCode | State transitions and assertions |
| **Caching** | OrderService, DiscountService | Cache hit/miss verification with spies |
| **Collections** | Order, OrderService | List manipulation and verification |
| **Calculations** | OrderItem, DiscountService | Numeric computation and assertion |
| **Dependency Injection** | OrderService, DiscountService | Constructor injection patterns |
| **Private Methods** | OrderService, DiscountService | Spy usage for private method testing |
| **Exceptions** | Multiple classes | Exception handling patterns |
| **Data-Driven Tests** | OrderItem, DiscountCode | Multiple input/output combinations |
| **Async/Side Effects** | OrderService notifications | Verify notification calls |
| **Closures/Predicates** | Mock verification | Argument matching with closures |
| **Complex Returns** | OrderService.submitOrder | Nested object return verification |

---

## Test Class Template

Each class should have a corresponding test named `*Test` (e.g., `OrderServiceTest`) that:

1. **Uses @Subject annotation** for the class under test
2. **Mocks all dependencies** as field-level declarations
3. **Separate feature methods** for state assertions (expect) and interaction verification (then)
4. **Tests all public methods** with positive and negative cases
5. **Uses Spy** for testing private methods when necessary
6. **Verifies nested objects** with `with()` grouping
7. **Ends all then: blocks** with `0 * _`
8. **Captures and verifies return values** in expect blocks
9. **Tests exception paths** with thrown()
10. **Uses data-driven tests** with where: blocks for multiple scenarios

---

## Coverage Goals

- ✅ Basic method testing (getters, setters, simple logic)
- ✅ Complex object graphs (nested objects and collections)
- ✅ Dependency mocking and verification
- ✅ Spy usage for private methods
- ✅ Exception handling and custom exceptions
- ✅ Enum and state machine behavior
- ✅ Cache management verification
- ✅ Data-driven testing with multiple scenarios
- ✅ Closures and predicates for argument matching
- ✅ Time-based and date-based logic
- ✅ Numeric calculations and comparisons
- ✅ Complex return type verification
- ✅ Side-effect verification (notifications)
