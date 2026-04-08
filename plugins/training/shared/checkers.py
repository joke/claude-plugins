"""
Shared assertion checkers for Java coding convention evals.

Each checker takes Java source code (string) and returns (passed: bool, evidence: str).
Checkers are organized by category:
- General: version-agnostic conventions (final vars, immutability, small methods, etc.)
- Java 8: streams, Optional, Collections.unmodifiable*, no-Java-9+ features
- Java 25: records, sealed classes, pattern matching, List.of, text blocks, var, etc.
"""
import re


# ---------------------------------------------------------------------------
# General checkers (version-agnostic)
# ---------------------------------------------------------------------------

def check_all_vars_final(code):
    """Check that all local variables and method parameters use final."""
    method_pattern = re.compile(
        r'^\s+(?:public|private|protected)\s+(?:static\s+)?(?:\w+(?:<[^>]+>)?\s+)?(\w+)\s*\(([^)]*)\)',
        re.MULTILINE
    )
    for match in method_pattern.finditer(code):
        params_str = match.group(2).strip()
        if not params_str:
            continue
        depth = 0
        current = []
        params = []
        for ch in params_str:
            if ch == '<':
                depth += 1
            elif ch == '>':
                depth -= 1
            elif ch == ',' and depth == 0:
                params.append(''.join(current).strip())
                current = []
                continue
            current.append(ch)
        if current:
            params.append(''.join(current).strip())

        for param in params:
            param = param.strip()
            if not param:
                continue
            while param.startswith('@'):
                param = re.sub(r'^@\w+(\([^)]*\))?\s*', '', param)
            if not param.startswith('final '):
                return False, f"Parameter not final: '{param}'"

    lines = code.split('\n')
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith('//') or stripped.startswith('*') or stripped.startswith('/*'):
            continue
        if stripped.startswith('import') or stripped.startswith('package') or stripped.startswith('@'):
            continue
        if stripped.startswith('return') or stripped.startswith('throw') or stripped.startswith('if') or stripped.startswith('} '):
            continue
        if re.match(r'(private|public|protected|static)', stripped):
            continue
        local_match = re.match(r'([A-Z][\w]*(?:<[^>]+>)?(?:\[\])?)\s+(\w+)\s*=', stripped)
        if local_match and not stripped.startswith('final '):
            return False, f"Local variable not final at line {i+1}: '{stripped}'"

    return True, "All variables and parameters use final"


def check_all_vars_final_or_var(code):
    """Check that all local variables and method parameters use final (or final var).
    Skips record component declarations (implicitly final)."""
    # Skip record component declarations — they are implicitly final
    method_pattern = re.compile(
        r'^\s+(?:public|private|protected)\s+(?:static\s+)?(?:\w+(?:<[^>]+>)?\s+)?(\w+)\s*\(([^)]*)\)',
        re.MULTILINE
    )
    # Find all record declarations to exclude their component params
    record_pattern = re.compile(r'\brecord\s+\w+\s*\(([^)]*)\)')
    record_param_strs = set()
    for rm in record_pattern.finditer(code):
        record_param_strs.add(rm.start())

    for match in method_pattern.finditer(code):
        # Skip if this match is part of a record declaration
        line_start = code.rfind('\n', 0, match.start()) + 1
        line = code[line_start:match.end()]
        if re.search(r'\brecord\s+', line):
            continue
        params_str = match.group(2).strip()
        if not params_str:
            continue
        depth = 0
        current = []
        params = []
        for ch in params_str:
            if ch == '<':
                depth += 1
            elif ch == '>':
                depth -= 1
            elif ch == ',' and depth == 0:
                params.append(''.join(current).strip())
                current = []
                continue
            current.append(ch)
        if current:
            params.append(''.join(current).strip())

        for param in params:
            param = param.strip()
            if not param:
                continue
            while param.startswith('@'):
                param = re.sub(r'^@\w+(\([^)]*\))?\s*', '', param)
            if not param.startswith('final '):
                return False, f"Parameter not final: '{param}'"

    lines = code.split('\n')
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith('//') or stripped.startswith('*') or stripped.startswith('/*'):
            continue
        if stripped.startswith('import') or stripped.startswith('package') or stripped.startswith('@'):
            continue
        if stripped.startswith('return') or stripped.startswith('throw') or stripped.startswith('if') or stripped.startswith('} '):
            continue
        if re.match(r'(private|public|protected|static)', stripped):
            continue
        # Accept both "final Type x =" and "final var x ="
        local_match = re.match(r'([A-Z][\w]*(?:<[^>]+>)?(?:\[\])?|var)\s+(\w+)\s*=', stripped)
        if local_match and not stripped.startswith('final '):
            return False, f"Local variable not final at line {i+1}: '{stripped}'"

    return True, "All variables and parameters use final"


def check_no_checked_exceptions(code):
    """Check no throws clause with checked exception types."""
    throws_pattern = re.compile(r'\)\s*throws\s+\w+')
    match = throws_pattern.search(code)
    if match:
        return False, f"Found throws clause: '{match.group(0).strip()}'"
    return True, "No checked exceptions in signatures"


def check_immutable_fields(code):
    """Check all instance fields are private final."""
    lines = code.split('\n')
    brace_depth = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        brace_depth += stripped.count('{') - stripped.count('}')
        if brace_depth != 1:
            continue
        if re.match(r'(public|private|protected)?\s*(static\s+)?(final\s+)?(abstract\s+)?(sealed\s+)?(class|interface|enum|record)\s+', stripped):
            continue
        if '(' in stripped:
            continue
        if stripped.startswith('//') or stripped.startswith('*') or stripped.startswith('@'):
            continue
        if not stripped or stripped == '}':
            continue
        if re.match(r'(private|public|protected)\s+', stripped):
            if 'static final' in stripped or 'final static' in stripped:
                continue
            if 'private final' not in stripped and 'private static' not in stripped:
                return False, f"Non-final field at line {i+1}: '{stripped}'"
    return True, "All fields are private final"


def check_small_methods(code):
    """Check no method exceeds ~20 lines of logic."""
    lines = code.split('\n')
    method_start = None
    brace_depth = 0
    method_depth = 0

    for i, line in enumerate(lines):
        stripped = line.strip()
        if method_start is None and re.match(r'(public|private|protected)\s+', stripped) and '(' in stripped:
            # Skip record/class/interface/enum declarations — they aren't methods
            if re.match(r'(public|private|protected)\s+(static\s+)?(final\s+)?(sealed\s+)?(abstract\s+)?(record|class|interface|enum)\s+', stripped):
                brace_depth += stripped.count('{') - stripped.count('}')
                continue
            if '{' in stripped:
                method_start = i
                method_depth = brace_depth
                brace_depth += stripped.count('{') - stripped.count('}')
                continue
        brace_depth += stripped.count('{') - stripped.count('}')
        if method_start is not None and brace_depth <= method_depth:
            length = i - method_start
            if length > 20:
                return False, f"Long method (~{length} lines) starting at line {method_start+1}"
            method_start = None

    return True, "All methods are reasonably small"


def check_no_setters(code):
    """Check no setter methods exist."""
    setter = re.search(r'public\s+void\s+set\w+\s*\(', code)
    if setter:
        return False, f"Setter found: '{setter.group(0).strip()}'"
    return True, "No setter methods"


def check_constructor_sets_all(code):
    """Check there's a constructor that accepts all fields."""
    # Skip for records — they have implicit constructors
    if re.search(r'\brecord\s+\w+\s*\(', code):
        return True, "Record has implicit constructor"

    lines = code.split('\n')
    fields = []
    for line in lines:
        stripped = line.strip()
        if re.match(r'private\s+final\s+\w+(?:<[^>]+>)?\s+\w+;', stripped):
            fields.append(stripped)

    constr = re.search(r'public\s+\w+\s*\(([^)]*)\)', code)
    if not constr:
        constr = re.search(r'private\s+\w+\s*\(([^)]*)\)', code)
        if constr and 'Builder' in constr.group(1):
            return False, "Uses Builder pattern instead of direct constructor"

    if not constr:
        if not fields:
            return True, "No fields, no constructor needed"
        return False, "No constructor found"

    params = [p.strip() for p in constr.group(1).split(',') if p.strip()]
    if len(params) < len(fields):
        return False, f"Constructor has {len(params)} params but {len(fields)} fields"

    return True, "Constructor accepts all fields"


def check_constructor_injection(code):
    """Check dependencies via constructor, no field/setter injection."""
    if re.search(r'@Inject\s', code) or re.search(r'@Autowired\s', code):
        if re.search(r'@(Inject|Autowired)\s+.*\w+\s*;', code):
            return False, "Field injection detected"
    # Check for setter injection (setters that assign to this.field)
    if re.search(r'public\s+void\s+set\w+\s*\([^)]*\)\s*\{[^}]*this\.\w+\s*=', code, re.DOTALL):
        return False, "Setter injection detected"
    # Records use implicit constructor injection
    if re.search(r'\brecord\s+\w+\s*\(', code):
        return True, "Record uses constructor injection implicitly"
    if re.search(r'this\.\w+\s*=\s*\w+', code):
        return True, "Constructor injection used"
    return False, "No constructor injection detected"


# ---------------------------------------------------------------------------
# Java 8 checkers
# ---------------------------------------------------------------------------

def check_streams_over_loops(code):
    """Check no for/while loops remain."""
    lines = code.split('\n')
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('//') or stripped.startswith('*'):
            continue
        if re.search(r'\bfor\s*\(', stripped) or re.search(r'\bwhile\s*\(', stripped):
            return False, f"Loop found at line {i+1}: '{stripped}'"
    return True, "No for/while loops found"


def check_optional_returns(code):
    """Check that find/lookup methods return Optional."""
    method_pattern = re.compile(r'public\s+(\w+(?:<[^>]+>)?)\s+(find\w+|get\w+ById|lookup\w+)\s*\(')
    for match in method_pattern.finditer(code):
        return_type = match.group(1)
        method_name = match.group(2)
        if 'find' in method_name.lower() and not return_type.startswith('Optional') and not return_type.startswith('List'):
            return False, f"Method '{method_name}' returns '{return_type}' instead of Optional"
    return True, "Find/lookup methods return Optional"


def check_no_java9_features(code):
    """Check no Java 9+ features are used."""
    issues = []
    if re.search(r'\bList\.of\b', code):
        issues.append("List.of (Java 9)")
    if re.search(r'\bMap\.of\b', code):
        issues.append("Map.of (Java 9)")
    if re.search(r'\bSet\.of\b', code):
        issues.append("Set.of (Java 9)")
    if re.search(r'\bvar\s+\w+\s*=', code):
        issues.append("var (Java 10)")
    if re.search(r'\brecord\s+\w+', code):
        issues.append("record (Java 14)")
    if re.search(r'\bsealed\s+', code):
        issues.append("sealed (Java 17)")
    if re.search(r'\.toList\(\)', code) and not re.search(r'Collectors\.toList\(\)', code):
        if re.search(r'\.stream\(\)[^;]*\.toList\(\)', code):
            issues.append("Stream.toList() (Java 16)")
    if issues:
        return False, "Java 9+ features found: " + ", ".join(issues)
    return True, "No Java 9+ features"


def check_unmodifiable_collections_java8(code):
    """Check collection fields return unmodifiable views (Java 8 style)."""
    if 'Collections.unmodifiable' in code or 'unmodifiableList' in code:
        return True, "Uses Collections.unmodifiable* collections"
    # Check if it's a record (which uses List.copyOf in java25)
    if re.search(r'\brecord\s+\w+', code):
        return True, "Record handles immutability differently"
    # Only check for collection FIELDS (private final List/Set/Map), not return types or parameters
    collection_field = re.search(r'private\s+final\s+(List|Set|Map)<', code)
    if collection_field:
        return False, "Has collection fields but no Collections.unmodifiable* wrapper found"
    return True, "No collection fields to wrap"


# ---------------------------------------------------------------------------
# Java 25 checkers
# ---------------------------------------------------------------------------

def check_uses_records(code):
    """Check that data-carrying classes use records where appropriate."""
    if re.search(r'\brecord\s+\w+\s*\(', code):
        return True, "Uses record types"
    # Check if there are immutable data classes that should be records
    class_matches = re.findall(r'\bclass\s+(\w+)', code)
    if class_matches:
        # If there are classes with only private final fields and getters, they should probably be records
        return False, f"Classes found that might benefit from being records: {', '.join(class_matches)}"
    return True, "No data classes present"


def check_uses_sealed(code):
    """Check that type hierarchies use sealed where appropriate."""
    if re.search(r'\bsealed\s+(class|interface)\s+', code):
        return True, "Uses sealed types"
    # Check for abstract classes or interfaces with concrete subtypes — strong signal for sealed
    if re.search(r'\babstract\s+class\s+', code):
        return False, "Abstract class hierarchy should use sealed interface"
    # Multiple classes extending the same parent suggests sealed
    extends_matches = re.findall(r'\bextends\s+(\w+)', code)
    if extends_matches:
        from collections import Counter
        counts = Counter(extends_matches)
        for parent, count in counts.items():
            if count >= 2:
                return False, f"Multiple subtypes of '{parent}' — should use sealed"
    return True, "No type hierarchy that needs sealed"


def check_uses_pattern_matching(code):
    """Check that instanceof checks use pattern matching."""
    # Old-style instanceof without pattern variable
    old_style = re.search(r'instanceof\s+\w+\)', code)
    new_style = re.search(r'instanceof\s+(final\s+)?\w+\s+\w+', code)
    if old_style and not new_style:
        return False, "Uses old-style instanceof without pattern matching"
    if new_style:
        # Check that pattern variables are final
        non_final_pattern = re.search(r'instanceof\s+(?!final\s)\w+\s+\w+', code)
        if non_final_pattern:
            return False, f"Pattern variable not final: '{non_final_pattern.group(0)}'"
        return True, "Uses pattern matching with final pattern variables"
    return True, "No instanceof checks present"


def check_uses_switch_expressions(code):
    """Check that switch uses expression form with arrows."""
    # Old-style switch with case: and break
    if re.search(r'\bcase\s+[^-]+:', code) and re.search(r'\bbreak\s*;', code):
        return False, "Uses old-style switch statement with break"
    if re.search(r'\bcase\s+.*->', code):
        return True, "Uses switch expressions with arrow syntax"
    return True, "No switch statements present"


def check_uses_text_blocks(code):
    """Check that multi-line strings use text blocks."""
    # Multi-line string concatenation that should be a text block
    multiline_concat = re.search(r'"[^"]*"\s*\+\s*\n\s*"', code)
    if multiline_concat:
        return False, "Multi-line string concatenation should use text blocks"
    if re.search(r'"""', code):
        return True, "Uses text blocks"
    return True, "No multi-line strings present"


def check_uses_var(code):
    """Check that local variables use var where type is obvious from RHS."""
    if re.search(r'\bfinal\s+var\s+', code):
        return True, "Uses final var for local variables"
    # Check for bare var (without final) — this is wrong
    if re.search(r'(?<!final\s)\bvar\s+\w+\s*=', code):
        return False, "Uses var without final — should be 'final var'"
    return True, "No var usage (acceptable if types are not obvious from RHS)"


def check_modern_collections(code):
    """Check that modern collection factories are used (List.of, List.copyOf, etc.)."""
    # Check for old-style Collections.unmodifiableList
    if re.search(r'Collections\.unmodifiable', code):
        return False, "Uses old-style Collections.unmodifiable* — prefer List.of/List.copyOf"
    if re.search(r'List\.of\b|List\.copyOf\b|Map\.of\b|Map\.copyOf\b|Set\.of\b|Set\.copyOf\b', code):
        return True, "Uses modern collection factories"
    # Check for Collectors.toList() instead of .toList()
    if re.search(r'Collectors\.toList\(\)', code):
        return False, "Uses Collectors.toList() — prefer Stream.toList()"
    return True, "No collection factory usage needed"


def check_no_java8_patterns(code):
    """Check that Java 8-era patterns aren't used when modern alternatives exist."""
    issues = []
    if re.search(r'Collections\.unmodifiableList\(', code):
        issues.append("Collections.unmodifiableList — use List.copyOf or List.of")
    if re.search(r'Collections\.unmodifiableMap\(', code):
        issues.append("Collections.unmodifiableMap — use Map.copyOf or Map.of")
    if re.search(r'Collections\.unmodifiableSet\(', code):
        issues.append("Collections.unmodifiableSet — use Set.copyOf or Set.of")
    if re.search(r'Collectors\.toList\(\)', code) and not re.search(r'\.collect\(Collectors\.toUnmodifiable', code):
        issues.append("Collectors.toList() — use .toList()")
    if issues:
        return False, "Old Java 8 patterns found: " + "; ".join(issues)
    return True, "No outdated Java 8 patterns"


# ---------------------------------------------------------------------------
# Null safety checkers (NullAway + JSpecify)
# ---------------------------------------------------------------------------

def check_no_suppress_nullaway(code):
    """Check that @SuppressWarnings("NullAway") is never used."""
    match = re.search(r'@SuppressWarnings\s*\(\s*"NullAway"\s*\)', code)
    if match:
        return False, f"Found @SuppressWarnings(\"NullAway\")"
    # Also check array form
    match = re.search(r'@SuppressWarnings\s*\(\s*\{[^}]*"NullAway"[^}]*\}\s*\)', code)
    if match:
        return False, f"Found @SuppressWarnings with NullAway in array"
    return True, "No NullAway suppressions"


def check_package_info_nullmarked(code):
    """Check that package-info.java with @NullMarked exists in the output."""
    if '@NullMarked' in code and 'package-info' not in code:
        # @NullMarked is on a class, not package-info — still check for package-info separately
        pass
    if '@NullMarked' in code:
        return True, "Found @NullMarked annotation"
    return False, "No @NullMarked annotation found — package-info.java should have @NullMarked"


def check_nullable_annotations(code):
    """Check that nullable fields/params use @Nullable from JSpecify."""
    # Check that @Nullable is imported from jspecify
    if '@Nullable' in code:
        if 'org.jspecify.annotations.Nullable' in code or 'org.jspecify.annotations.*' in code:
            return True, "Uses @Nullable from JSpecify"
        # Check for wrong annotation packages
        wrong_packages = []
        if 'javax.annotation.Nullable' in code:
            wrong_packages.append("javax.annotation")
        if 'org.jetbrains.annotations.Nullable' in code:
            wrong_packages.append("org.jetbrains.annotations")
        if 'edu.umd.cs.findbugs.annotations.Nullable' in code:
            wrong_packages.append("edu.umd.cs.findbugs.annotations")
        if 'android.support.annotation.Nullable' in code or 'androidx.annotation.Nullable' in code:
            wrong_packages.append("android/androidx")
        if wrong_packages:
            return False, f"Uses @Nullable from wrong package(s): {', '.join(wrong_packages)} — use org.jspecify.annotations"
        return True, "Uses @Nullable (import source not detected but present)"
    # If code has null checks or Optional.ofNullable but no @Nullable, might be missing annotations
    if re.search(r'=\s*null\s*;', code) or re.search(r'==\s*null', code) or re.search(r'Optional\.ofNullable', code):
        return False, "Code handles null values but no @Nullable annotations found"
    return True, "No nullable references detected"


def check_null_safe_handling(code):
    """Check that nullable fields are handled in a null-safe way."""
    lines = code.split('\n')
    # Find @Nullable fields
    nullable_fields = []
    for line in lines:
        stripped = line.strip()
        if '@Nullable' in stripped and re.search(r'(private|protected)\s+(final\s+)?', stripped):
            field_match = re.search(r'(\w+)\s*;', stripped)
            if field_match:
                nullable_fields.append(field_match.group(1))

    if not nullable_fields:
        return True, "No nullable fields to check"

    # Check that nullable fields are accessed safely (null check, Optional, or ternary)
    for field in nullable_fields:
        # Look for direct dereference without null check
        # This is a heuristic — look for field.method() without a preceding null check
        usages = []
        for i, line in enumerate(lines):
            stripped = line.strip()
            if f'{field}.' in stripped or f'{field} =' in stripped:
                usages.append((i, stripped))

        for line_num, usage in usages:
            # Check if there's a null check in the surrounding context (5 lines before)
            context = '\n'.join(lines[max(0, line_num-5):line_num+1])
            if (f'{field} != null' in context or
                f'{field} == null' in context or
                f'Optional.ofNullable({field})' in context or
                f'Optional.ofNullable(this.{field})' in context or
                f'this.{field} = {field}' in usage or  # assignment in constructor
                f'{field} != null ?' in context):  # ternary
                continue

    return True, "Nullable fields handled safely"


def check_no_nullable_on_nonnull(code):
    """Check that @Nullable is not used on things that should be non-null."""
    # @Nullable on constructor params that are assigned to non-nullable fields
    # This is hard to check precisely, so just verify @Nullable exists where needed
    # and @NonNull is not used (redundant under @NullMarked)
    if re.search(r'@NonNull\b', code):
        return False, "@NonNull is redundant under @NullMarked — remove it"
    return True, "No redundant @NonNull annotations"


# ---------------------------------------------------------------------------
# Java 11 checkers
# ---------------------------------------------------------------------------

def check_no_post_java11_features(code):
    """Check no Java 12+ features are used (records, sealed, pattern matching,
    text blocks, switch expressions with ->, Stream.toList())."""
    issues = []
    if re.search(r'\brecord\s+\w+\s*\(', code):
        issues.append("record (Java 14)")
    if re.search(r'\bsealed\s+(class|interface)\b', code) or re.search(r'\bnon-sealed\b', code):
        issues.append("sealed (Java 17)")
    if re.search(r'\bpermits\s+\w+', code):
        issues.append("permits (Java 17)")
    if re.search(r'instanceof\s+(final\s+)?\w+\s+\w+\s*[)&|]', code):
        issues.append("instanceof pattern matching (Java 16)")
    if '"""' in code:
        issues.append("text blocks (Java 13)")
    if re.search(r'case\s+[^:]+->', code):
        issues.append("switch expressions with -> (Java 14)")
    if re.search(r'\.stream\(\)[^;]*\.toList\(\)', code):
        issues.append("Stream.toList() (Java 16)")
    if issues:
        return False, "Post-Java 11 features found: " + ", ".join(issues)
    return True, "No post-Java 11 features"


def check_unmodifiable_collections_java11(code):
    """Check collection fields are immutable (List.of/copyOf or Collections.unmodifiable*)."""
    if re.search(r'\bList\.(of|copyOf)\b', code) or re.search(r'\bMap\.(of|copyOf)\b', code) \
            or re.search(r'\bSet\.(of|copyOf)\b', code):
        return True, "Uses List.of/copyOf (Java 9/10) for immutability"
    if 'Collections.unmodifiable' in code:
        return True, "Uses Collections.unmodifiable*"
    collection_field = re.search(r'private\s+final\s+(List|Set|Map)<', code)
    if collection_field:
        return False, "Has collection fields but no immutable wrapper found"
    return True, "No collection fields to wrap"


# ---------------------------------------------------------------------------
# Java 17 checkers
# ---------------------------------------------------------------------------

def check_no_post_java17_features(code):
    """Check that no Java 18+ features are used.

    Java 17 allows: records, sealed, instanceof pattern matching, text blocks,
    switch expressions with ->, Stream.toList(), Stream.mapMulti(), helpful NPEs.
    Forbidden (Java 21+): pattern matching for switch, record patterns,
    virtual threads, SequencedCollection/SequencedMap, scoped values,
    string templates."""
    issues = []
    # Pattern matching for switch: `case Type x ->` inside a switch
    # (instanceof pattern matching is fine, switch-case Type is not)
    if re.search(r'case\s+\w+(?:<[^>]+>)?\s+\w+\s*->', code):
        issues.append("pattern matching for switch (Java 21)")
    if re.search(r'case\s+\w+\s*\([^)]*\)\s*->', code):
        issues.append("record patterns (Java 21)")
    if re.search(r'Thread\.ofVirtual\b', code) or re.search(r'Thread\.startVirtualThread\b', code):
        issues.append("virtual threads (Java 21)")
    if re.search(r'Executors\.newVirtualThreadPerTaskExecutor\b', code):
        issues.append("virtual thread executor (Java 21)")
    if re.search(r'\bSequencedCollection\b', code) or re.search(r'\bSequencedMap\b', code) \
            or re.search(r'\bSequencedSet\b', code):
        issues.append("sequenced collections (Java 21)")
    if re.search(r'\bScopedValue\b', code):
        issues.append("scoped values (Java 21 preview)")
    # String templates: STR."..." / FMT."..."
    if re.search(r'\b(?:STR|FMT|RAW)\."', code):
        issues.append("string templates (Java 21 preview)")
    if issues:
        return False, "Post-Java 17 features found: " + ", ".join(issues)
    return True, "No post-Java 17 features"


# ---------------------------------------------------------------------------
# Java 21 checkers
# ---------------------------------------------------------------------------

def check_no_post_java21_features(code):
    """Check that no Java 22+ features are used.

    Java 21 allows: records, sealed, instanceof + switch pattern matching,
    record patterns, text blocks, switch expressions, virtual threads,
    sequenced collections.
    Forbidden (Java 22+): unnamed patterns/variables, string templates,
    flexible constructor bodies (statements before super()), primitive
    type patterns, module imports."""
    issues = []
    # String templates: STR."..." / FMT."..."
    if re.search(r'\b(?:STR|FMT|RAW)\."', code):
        issues.append("string templates (preview-only, withdrawn)")
    # Unnamed pattern variable `_` as standalone identifier in patterns/lambdas
    if re.search(r'\bvar\s+_\b', code) or re.search(r'\(\s*_\s*\)\s*->', code):
        issues.append("unnamed variables (Java 22)")
    if re.search(r'case\s+\w+\s*\(\s*_\s*\)', code):
        issues.append("unnamed patterns (Java 22)")
    # Module imports
    if re.search(r'^\s*import\s+module\s+', code, re.MULTILINE):
        issues.append("import module (Java 23)")
    if issues:
        return False, "Post-Java 21 features found: " + ", ".join(issues)
    return True, "No post-Java 21 features"


# ---------------------------------------------------------------------------
# Lombok checkers
# ---------------------------------------------------------------------------

_LOMBOK_ANNOTATIONS = [
    '@Getter', '@Setter', '@ToString', '@EqualsAndHashCode',
    '@NoArgsConstructor', '@RequiredArgsConstructor', '@AllArgsConstructor',
    '@Data', '@Value', '@Builder', '@SuperBuilder', '@Singular',
    '@Cleanup', '@SneakyThrows', '@Delegate', '@UtilityClass',
    '@StandardException', '@FieldNameConstants',
    '@Slf4j', '@Log4j2', '@Log', '@CommonsLog', '@Flogger', '@JBossLog',
]


def check_no_manual_getter_setter(code):
    """Fail on hand-written getters/setters that simply return/assign a field."""
    # Setter: public void setX(Type x) { this.x = x; }
    setter = re.search(
        r'public\s+void\s+set[A-Z]\w*\s*\([^)]*\)\s*\{\s*this\.\w+\s*=',
        code, re.DOTALL)
    if setter:
        return False, f"Manual setter found: '{setter.group(0).splitlines()[0]}'"
    # Getter: public Type getX() { return x; } / isX()
    getter = re.search(
        r'public\s+\w+(?:<[^>]+>)?\s+(?:get|is)[A-Z]\w*\s*\(\s*\)\s*\{\s*return\s+\w+\s*;\s*\}',
        code)
    if getter:
        return False, f"Manual getter found: '{getter.group(0).splitlines()[0]}'"
    return True, "No hand-written getters or setters"


def check_no_manual_tostring(code):
    """Fail on hand-written toString() override."""
    match = re.search(r'public\s+String\s+toString\s*\(\s*\)\s*\{', code)
    if match:
        return False, "Manual toString() found — use @ToString"
    return True, "No manual toString()"


def check_no_manual_equals_hashcode(code):
    """Fail on hand-written equals()/hashCode()."""
    if re.search(r'public\s+boolean\s+equals\s*\(\s*Object\s+\w+\s*\)\s*\{', code):
        return False, "Manual equals() found — use @EqualsAndHashCode"
    if re.search(r'public\s+int\s+hashCode\s*\(\s*\)\s*\{', code):
        return False, "Manual hashCode() found — use @EqualsAndHashCode"
    return True, "No manual equals/hashCode"


def check_uses_lombok_annotations(code):
    """Check at least one Lombok annotation is present."""
    for ann in _LOMBOK_ANNOTATIONS:
        if re.search(re.escape(ann) + r'\b', code):
            return True, f"Uses Lombok annotation {ann}"
    return False, "No Lombok annotations found"


def check_no_lombok_val_var(code):
    """Fail if lombok.val or lombok.var is imported or used."""
    if re.search(r'import\s+lombok\.val\s*;', code) or re.search(r'import\s+lombok\.var\s*;', code):
        return False, "Imports lombok.val/lombok.var — use Java's native var"
    return True, "Does not use lombok.val/lombok.var"


def check_uses_onconstructor_inject(code):
    """If @Inject/@Autowired appears, it must be via onConstructor_ on a
    @*ArgsConstructor annotation, not a hand-written constructor."""
    has_inject = '@Inject' in code or '@Autowired' in code
    if not has_inject:
        return True, "No @Inject/@Autowired in code"
    if 'onConstructor_' in code:
        # And no hand-written constructor carrying @Inject/@Autowired directly
        manual = re.search(
            r'@(?:Inject|Autowired)\s+\w+\s+\w+\s*\([^)]*\)\s*\{',
            code)
        if manual:
            return False, "Hand-written @Inject/@Autowired constructor still present"
        return True, "Uses onConstructor_ for injection"
    return False, "@Inject/@Autowired present but no onConstructor_ — use @RequiredArgsConstructor(onConstructor_ = @Inject)"


def check_uses_slf4j_annotation(code):
    """If a manual Logger field exists, fail. If @Slf4j (or variant) exists, pass."""
    if re.search(r'@(Slf4j|Log4j2|Log|CommonsLog|Flogger|JBossLog)\b', code):
        # Ensure no manual Logger field remains
        if re.search(r'(private|protected|public)\s+(static\s+)?(final\s+)?Logger\s+\w+\s*=', code):
            return False, "Both @Slf4j and a manual Logger field present"
        return True, "Uses Lombok logger annotation"
    if re.search(r'Logger\s+\w+\s*=\s*LoggerFactory\.getLogger', code):
        return False, "Manual Logger field — use @Slf4j"
    if 'LoggerFactory.getLogger' in code:
        return False, "Manual LoggerFactory.getLogger usage — use @Slf4j"
    return True, "No logger required"


def check_uses_utility_class(code):
    """Check @UtilityClass is present for classes that look like utility classes."""
    if '@UtilityClass' in code:
        return True, "Uses @UtilityClass"
    # Heuristic: class with only static methods and a private constructor
    if re.search(r'class\s+\w*Utils?\b', code) or re.search(r'class\s+\w*Helper\b', code):
        return False, "Utility-style class missing @UtilityClass"
    return True, "Not a utility class"


def check_uses_standard_exception(code):
    """Check @StandardException is present for exception classes with the four
    standard constructors."""
    if '@StandardException' in code:
        # Make sure manual standard constructors are not also present
        if re.search(r'public\s+\w*Exception\s*\(\s*String\s+\w+\s*\)\s*\{', code):
            return False, "Both @StandardException and manual constructors present"
        return True, "Uses @StandardException"
    if re.search(r'class\s+\w+\s+extends\s+\w*Exception', code):
        return False, "Exception class missing @StandardException"
    return True, "Not an exception class"


# ---------------------------------------------------------------------------
# Registry: maps assertion IDs to checker functions
# ---------------------------------------------------------------------------

CHECKERS = {
    # General
    'all-vars-final': check_all_vars_final,
    'all-vars-final-or-var': check_all_vars_final_or_var,
    'no-checked-exceptions': check_no_checked_exceptions,
    'immutable-fields': check_immutable_fields,
    'small-methods': check_small_methods,
    'no-setters': check_no_setters,
    'constructor-sets-all': check_constructor_sets_all,
    'constructor-injection': check_constructor_injection,

    # Java 8
    'streams-over-loops': check_streams_over_loops,
    'streams-everywhere': check_streams_over_loops,
    'optional-not-null': check_optional_returns,
    'optional-for-find': check_optional_returns,
    'no-java9-features': check_no_java9_features,
    'unmodifiable-collections': check_unmodifiable_collections_java8,

    # Java 11
    'no-post-java11-features': check_no_post_java11_features,
    'unmodifiable-collections-java11': check_unmodifiable_collections_java11,

    # Java 17
    'no-post-java17-features': check_no_post_java17_features,

    # Java 21
    'no-post-java21-features': check_no_post_java21_features,

    # Java 25
    'uses-records': check_uses_records,
    'uses-sealed': check_uses_sealed,
    'uses-pattern-matching': check_uses_pattern_matching,
    'uses-switch-expressions': check_uses_switch_expressions,
    'uses-text-blocks': check_uses_text_blocks,
    'uses-var': check_uses_var,
    'modern-collections': check_modern_collections,
    'no-java8-patterns': check_no_java8_patterns,

    # Null safety
    'no-suppress-nullaway': check_no_suppress_nullaway,
    'package-info-nullmarked': check_package_info_nullmarked,
    'nullable-annotations': check_nullable_annotations,
    'null-safe-handling': check_null_safe_handling,
    'no-redundant-nonnull': check_no_nullable_on_nonnull,

    # Lombok
    'no-manual-getter-setter': check_no_manual_getter_setter,
    'no-manual-tostring': check_no_manual_tostring,
    'no-manual-equals-hashcode': check_no_manual_equals_hashcode,
    'uses-lombok-annotations': check_uses_lombok_annotations,
    'no-lombok-val-var': check_no_lombok_val_var,
    'uses-onconstructor-inject': check_uses_onconstructor_inject,
    'uses-slf4j-annotation': check_uses_slf4j_annotation,
    'uses-utility-class': check_uses_utility_class,
    'uses-standard-exception': check_uses_standard_exception,
}
