---
name: groovy-coding-conventions
description: >
  Use when writing, creating, reviewing, or modifying Groovy code — .groovy classes and
  scripts, Gradle build files, Jenkinsfiles, Grails/Micronaut/Ratpack sources. Load this
  skill before authoring or editing any Groovy so the code reads as idiomatic Groovy:
  Groovy accessors, the right string flavor, safe navigation, spread, spaceship and identity
  operators, Groovy truth, AST transforms for data classes, and closures over loops — instead
  of Java transliterated into a .groovy file. Trigger this for any Groovy work even when the
  user never says "conventions" or "style". Does not cover Spock test conventions (use the
  Spock skill for tests), formatting, or indentation.
user-invocable: false
---

# Groovy Code Conventions

First, use the Skill tool to load `conventions:java-coding-conventions`. Keep its **design** values — immutable data, small single-purpose methods, composition over inheritance, constructor injection, unchecked exceptions only, most-restrictive visibility. Those are language-agnostic and still hold.

But do **not** carry the Java skill's *syntactic* rules into Groovy. This is the most important thing to internalize:

> The Java skill says "every variable and parameter is `final`" and "always write explicit types." In Groovy, **ignore both**. Groovy is dynamically typed by design, and littering `final` and explicit types everywhere produces code that looks like Java that happens to compile under `groovyc` — which is exactly what we are trying to avoid.

The goal is code a Groovy developer would write, not Java with the semicolons removed. Every section below explains the *why*, because once you understand why Groovy offers a construct, you'll reach for it naturally instead of defaulting to the Java shape.

## Prefer Groovy syntax over Java syntax

Groovy removes ceremony that Java requires. Drop it.

- **No semicolons.** One statement per line; the line ending terminates it.
- **No `return` on the last expression.** Every block and method returns its last evaluated expression. Use an explicit `return` only for early exits.
- **Optional parentheses** on top-level method calls with at least one argument: `println 'hi'`, `assertThat result equalTo 3`. Keep parens when they aid clarity or the call is an argument to another call.
- **`public` is the default** for classes and methods — omit it. Write `def` or a return type, not `public`.
- **Native literals** instead of factory calls: `[1, 2, 3]` is an `ArrayList`, `[a: 1, b: 2]` is a `LinkedHashMap`, `[] as Set`, `1..10` is a `Range`. Don't write `Arrays.asList(...)` or `new HashMap<>()`.

```groovy
// Java transliterated into Groovy — wrong
public List<String> activeNames(final List<Customer> customers) {
    final List<String> names = new ArrayList<String>();
    return names;
}

// idiomatic Groovy
def activeNames(customers) {
    customers.findAll { it.active }*.name
}
```

## Dynamic typing and `def`

Default to `def` for local variables and let Groovy infer. Use `def` (or omit the type) for method return types and parameters too — duck typing is a feature, not a hazard, and it keeps methods reusable across types that share a shape.

Reach for an explicit type **only** when it genuinely earns its place:
- A public API parameter where the type documents intent better than a name can.
- You rely on multiple-dispatch (Groovy dispatches on runtime argument types).
- You're integrating with Java code that needs the concrete type.

Don't write `final`. Immutability of *data* is achieved with `@Immutable` (see below), not by sprinkling `final` on locals. A wall of `final` is noise that signals "Java author" to every reviewer.

## Groovy accessors and properties

A field declared with **no access modifier** is a Groovy *property*: Groovy auto-generates a getter and setter. Declare data this way and never hand-write `getX()`/`setX()`.

Access everything through property syntax — even Java beans, even `getClass()`:

```groovy
customer.name              // calls getName()
customer.name = 'Ada'      // calls setName('Ada')
order.class                // calls getClass()
config.timeoutSeconds      // calls getTimeoutSeconds(), no parens
```

Writing `customer.getName()` in Groovy is a tell that the author doesn't trust the language. The only time you call the accessor explicitly is when you need a method reference (`Customer.&getName`) or the property name collides with a keyword.

For read-only data, prefer an immutable class (see AST transforms) over a property with a public setter.

## Pick the right string

Groovy has four string flavors. Using the wrong one is the most common Groovy smell. Choose by *what's inside the string*, not by habit:

- **Single quotes** `'...'` → a plain `java.lang.String`. **Default to this** whenever there's no interpolation. Cheaper than a GString and signals "no surprises inside."
- **Double quotes** `"...${expr}..."` → a `GString` with interpolation. Use **only when you actually interpolate** a variable or expression. Don't use double quotes for a constant string.
- **Triple quotes** `'''...'''` (plain) or `"""...${x}..."""` (interpolating) → multi-line strings: SQL, JSON, templates, help text. Pick the single- or double-quoted triple based on whether you interpolate.
- **Slashy strings** `/pattern/` → regular expressions. Backslashes don't need escaping, so `/\d+/` instead of `"\\d+"`. For patterns containing a literal `/`, use dollar-slashy `$/.../$`.

```groovy
def name = 'Ada'                              // no interpolation → single quotes
def greeting = "Hello, ${name}!"              // interpolation → double quotes
def query = """
    SELECT id, name FROM customers
    WHERE status = 'ACTIVE'
"""                                            // multi-line → triple quotes
def digits = ~/\d+/                            // regex → slashy (~/.../ precompiles a Pattern)
```

## Groovy truth over verbose checks

Groovy defines "truth" for every type, so lean on it instead of explicit comparisons. A `null` reference, an empty `String`, an empty collection or map, the number `0`, and `false` are all *falsy*; everything else is *truthy*.

```groovy
// Java-style — verbose
if (name != null && !name.isEmpty()) { ... }
if (list != null && !list.isEmpty()) { ... }

// Groovy truth — say what you mean
if (name) { ... }      // non-null and non-empty
if (list) { ... }      // non-null and non-empty
```

Pair this with the **Elvis operator** `?:` to supply defaults: `def display = name ?: 'Anonymous'` returns `name` when truthy, otherwise `'Anonymous'`.

### `==` is equality; use `is()` for identity

In Groovy, `==` calls `.equals()` (null-safe), so it's what you almost always want — never reach for `.equals()` directly. When you genuinely need *reference* identity (the same object instance, not just equal), use `a.is(b)`. This is the Groovy identity operator and the only correct way to assert "the very same object."

```groovy
order == otherOrder        // value equality (calls equals)
cached.is(original)        // true only if the same instance
result.is(null)            // identity check against null
```

## Operators that replace boilerplate

- **Safe navigation `?.`** short-circuits to `null` instead of throwing on a null receiver: `order?.customer?.address?.city`. Use it wherever a link in a chain can legitimately be `null` — combine with Elvis for a default: `order?.total ?: 0`.
- **Spaceship `<=>`** is `compareTo`: returns -1/0/1. It's the natural body of a comparator closure: `people.sort { a, b -> a.age <=> b.age }`. Chain with Elvis for tie-breaks: `{ a, b -> a.last <=> b.last ?: a.first <=> b.first }`.
- **Spread-dot `*.`** applies a property or method across a collection: `customers*.name` collects every name; `files*.delete()` calls `delete()` on each. It's null-safe on the collection itself.
- **Spread `*`** unpacks a list into elements, and `*:` unpacks a map. Use it to flatten into literals or pass through arguments: `[*head, *tail]`, `[*: defaults, timeout: 30]`, `max(*numbers)`.

```groovy
def names = customers*.name                    // spread-dot
def all = [*defaults, *overrides]              // spread into a list
def merged = [*: base, region: 'eu']           // spread into a map
def newest = people.max { it.joined }          // closure, implicit it
people.sort { a, b -> a.age <=> b.age }        // spaceship comparator
```

## Number literals and type suffixes

Use a type suffix on a literal instead of constructing or coercing the number afterward. The suffix makes the type unambiguous at the point of declaration:

- `G` → `BigInteger` for an integer literal (`42G`), `BigDecimal` for a decimal literal (`19.99G`). Use `G` for money and any exact arithmetic — never `double`/`float` for currency.
- `L` → `long` (`5_000_000L`), `I` → `Integer`, `D` → `double`, `F` → `float`.
- Underscores group digits for readability: `1_000_000`.

```groovy
def price = 19.99G          // BigDecimal — exact, safe for money
def count = 5_000_000L      // long
def big = 2G ** 64          // BigInteger arithmetic
```

## Collections and closures

Reach for the Groovy GDK collection methods and closures instead of `for`/`while` loops — they read as the intent, not the mechanics. A single-argument closure can use the implicit parameter `it`.

| Intent | Use |
|---|---|
| transform each element | `collect { }` |
| keep matching elements | `findAll { }` |
| first match | `find { }` |
| any / all match | `any { }` / `every { }` |
| side effect per element | `each { }` / `eachWithIndex { x, i -> }` |
| fold to a single value | `inject(seed) { acc, x -> }` |
| group by a key | `groupBy { }` |
| sum / max / min | `sum()` / `max { }` / `min { }` |

```groovy
// loop-and-mutate — avoid
def totals = [:]
for (order in orders) {
    totals[order.region] = (totals[order.region] ?: 0) + order.amount
}

// idiomatic
def totals = orders.groupBy { it.region }
                   .collectEntries { region, list -> [region, list*.amount.sum()] }
```

Use `with` to run several statements against one target, and `tap` when you want the target back (great for configuring and returning an object):

```groovy
def report = new Report().tap {
    title = 'Q4'
    generatedAt = Instant.now()
}
```

## Data classes via AST transforms

This is how Groovy eliminates the boilerplate the Java skill builds by hand. Annotate the class; the compiler generates the members at build time. Prefer these over hand-written constructors, getters, `equals`/`hashCode`, and `toString`.

- **`@Immutable`** — the default for value objects, DTOs, events. Generates `private final` fields, a tuple constructor, a map constructor, `equals`/`hashCode`/`toString`, and defensively copies collections/dates. This *is* immutability in Groovy — you don't write `final` yourself.
- **`@Canonical`** — like `@Immutable` but mutable: combines `@TupleConstructor` + `@EqualsAndHashCode` + `@ToString`. Use when the object must change after construction.
- **`@TupleConstructor`** — generates a positional constructor (alongside Groovy's default map constructor).
- **`@Builder`** — a fluent builder when there are many optional fields.
- **`@Sortable`** — generates `compareTo`/comparators from chosen properties, so instances drop straight into `sort()` and `<=>`.
- **`@Memoized`** on a method caches results by arguments. **`@Lazy`** on a field defers initialization until first access.

```groovy
@Immutable
class Money {
    BigDecimal amount
    String currency
}

def price = new Money(19.99G, 'EUR')           // tuple constructor
def free = new Money(amount: 0G, currency: 'EUR')  // map constructor
price == new Money(19.99G, 'EUR')              // generated equals → true
```

Construct objects with **named (map) arguments** when it makes the call site self-documenting — Groovy gives every class a map constructor that sets properties by name:

```groovy
def customer = new Customer(name: 'Ada', region: 'eu', vip: true)
```

## Exceptions, logging, and the rest

These inherit from the Java skill, with a Groovy nuance:

- **Unchecked exceptions only.** Groovy doesn't enforce checked exceptions at all — you never need `throws` clauses or try/catch wrappers just to satisfy the compiler. Throw `RuntimeException` subtypes; create domain-specific ones when callers must distinguish.
- **`@Slf4j`** (from `groovy.util.logging`) injects a `log` field — use it instead of hand-rolling a logger.
- **Power asserts:** plain `assert expr` gives a detailed breakdown on failure. Use it freely in scripts and validation.

When in doubt, ask: "Would a seasoned Groovy developer write it this way, or does it look like Java wearing a Groovy costume?" Favor the former.
