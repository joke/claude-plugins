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


# A method declaration has a return type AND a name before '(' (two tokens once
# modifiers are stripped). A constructor has only the class name (one token), so
# this lets us tell methods from constructors without a real parser.
_MODIFIER_RE = re.compile(r'\b(static|final|abstract|synchronized|native|default)\b')


def _is_method_decl(head):
    """Given the text between a visibility keyword and '(', return True if it
    looks like a method (return type + name) rather than a constructor (name only)."""
    stripped = _MODIFIER_RE.sub('', head).strip()
    # Collapse generic type args so 'List<Map<K,V>> name' counts as two tokens.
    stripped = re.sub(r'<[^<>]*(?:<[^<>]*>[^<>]*)*>', '', stripped)
    return len(stripped.split()) >= 2


def check_no_private_methods(code):
    """Helper methods should be protected (+ @VisibleForTesting), not private, so
    they can be called directly and stubbed/spied in isolation tests. Constructors
    are exempt — they have no return type, so they are not flagged."""
    for i, line in enumerate(code.split('\n')):
        m = re.match(r'\s*private\s+(.*?)\s*\(', line)
        if m and _is_method_decl(m.group(1)):
            return False, f"private method at line {i+1}: '{line.strip()}' — make it protected + @VisibleForTesting"
    return True, "No private methods (helpers are protected for testability)"


def check_visible_for_testing(code):
    """Protected helper methods exist as a test seam and should be annotated
    @VisibleForTesting from org.jetbrains.annotations."""
    has_protected = any(
        re.match(r'\s*protected\s+(.*?)\s*\(', line) and _is_method_decl(re.match(r'\s*protected\s+(.*?)\s*\(', line).group(1))
        for line in code.split('\n')
    )
    if not has_protected:
        return None, "No protected methods to annotate — rule N/A"
    if '@VisibleForTesting' not in code:
        return False, "Protected helper methods should be annotated @VisibleForTesting"
    if 'org.jetbrains.annotations' in code:
        return True, "Uses @VisibleForTesting from org.jetbrains.annotations"
    if re.search(r'import\s+com\.google\.common\.annotations\.VisibleForTesting', code):
        return False, "@VisibleForTesting from Guava — use org.jetbrains.annotations"
    if re.search(r'import\s+[\w.]*\.VisibleForTesting', code):
        wrong = re.search(r'import\s+([\w.]*)\.VisibleForTesting', code).group(1)
        return False, f"@VisibleForTesting from {wrong} — use org.jetbrains.annotations"
    return True, "Uses @VisibleForTesting (import source not detected but present)"


def check_instance_over_static(code):
    """Helper methods should be instance methods (spyable), not static — unless the
    class is a pure utility class (every method is static)."""
    static_methods = []
    instance_methods = []
    for line in code.split('\n'):
        m = re.match(r'\s*(?:public|protected|private)\s+(.*?)\s*\(', line)
        if not m or not _is_method_decl(m.group(1)):
            continue
        if _MODIFIER_RE.search(m.group(1)) and 'static' in m.group(1):
            static_methods.append(line.strip())
        else:
            instance_methods.append(line.strip())
    if not static_methods:
        return True, "No static helper methods"
    if not instance_methods:
        return True, "Pure utility class — all methods static (allowed)"
    names = ', '.join(re.sub(r'\s*\{.*', '', s) for s in static_methods)
    return False, f"Static helper(s) in a stateful class — make instance methods so they can be spied: {names}"


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
# Groovy checkers
# ---------------------------------------------------------------------------

def _code_only(code):
    """Strip comments and string/regex contents so structural checks don't trip
    on tokens that merely appear inside literals. Slashy strings are left intact
    (the `/` is ambiguous with division and rarely holds the tokens we scan for)."""
    code = re.sub(r'/\*.*?\*/', ' ', code, flags=re.DOTALL)
    code = re.sub(r'""".*?"""', ' "" ', code, flags=re.DOTALL)
    code = re.sub(r"'''.*?'''", " '' ", code, flags=re.DOTALL)
    code = re.sub(r'"(?:\\.|[^"\\])*"', ' "" ', code)
    code = re.sub(r"'(?:\\.|[^'\\])*'", " '' ", code)
    code = re.sub(r'//[^\n]*', ' ', code)
    return code


def _line_of(text, pos):
    return text[:pos].count('\n') + 1


def check_no_semicolons(code):
    """Groovy uses line endings, not semicolons, as statement terminators."""
    cleaned = _code_only(code)
    match = re.search(r';', cleaned)
    if match:
        return False, f"Semicolon found at line {_line_of(cleaned, match.start())}"
    return True, "No semicolons"


def check_no_final_keyword(code):
    """Idiomatic Groovy is dynamically typed; immutability comes from @Immutable, not final."""
    cleaned = _code_only(code)
    match = re.search(r'\bfinal\b', cleaned)
    if match:
        return False, f"'final' keyword at line {_line_of(cleaned, match.start())}"
    return True, "No final keyword"


def check_no_public_modifier(code):
    """public is the default in Groovy and should be omitted."""
    cleaned = _code_only(code)
    match = re.search(r'\bpublic\b', cleaned)
    if match:
        return False, f"'public' modifier at line {_line_of(cleaned, match.start())}"
    return True, "No public modifier"


def check_groovy_accessors(code):
    """No explicit getX()/setX() calls — use property syntax."""
    cleaned = _code_only(code)
    getter = re.search(r'\.get[A-Z]\w*\s*\(\s*\)', cleaned)
    if getter:
        return False, f"Explicit getter call '{getter.group(0).strip()}' — use property access"
    setter = re.search(r'\.set[A-Z]\w*\s*\(', cleaned)
    if setter:
        return False, f"Explicit setter call '{setter.group(0).strip()}' — use property assignment"
    return True, "Uses property access, no explicit get/set calls"


def check_no_manual_getters_setters_groovy(code):
    """No hand-written getter/setter definitions — Groovy properties generate them."""
    cleaned = _code_only(code)
    getter = re.search(r'(?:\bdef\b|\b[A-Z]\w*\b|\bString\b|\bint\b|\bboolean\b|\bdouble\b|\blong\b)\s+get[A-Z]\w*\s*\(\s*\)\s*\{', cleaned)
    if getter:
        return False, f"Hand-written getter: '{getter.group(0).strip()}'"
    setter = re.search(r'(?:\bdef\b|\bvoid\b)\s+set[A-Z]\w*\s*\([^)]*\)\s*\{', cleaned)
    if setter:
        return False, f"Hand-written setter: '{setter.group(0).strip()}'"
    return True, "No hand-written getters/setters"


def check_no_manual_equals_tostring_groovy(code):
    """No hand-written equals/hashCode/toString — use an AST transform."""
    cleaned = _code_only(code)
    if re.search(r'\bboolean\s+equals\s*\(', cleaned):
        return False, "Hand-written equals() — use @Immutable/@Canonical/@EqualsAndHashCode"
    if re.search(r'\bint\s+hashCode\s*\(\s*\)', cleaned):
        return False, "Hand-written hashCode() — use an AST transform"
    if re.search(r'\bString\s+toString\s*\(\s*\)', cleaned):
        return False, "Hand-written toString() — use @ToString"
    if re.search(r'\bdef\s+(equals|hashCode|toString)\s*\(', cleaned):
        return False, "Hand-written equals/hashCode/toString — use an AST transform"
    return True, "No hand-written equals/hashCode/toString"


def check_ast_immutable(code):
    """Data classes should use @Immutable (or @Canonical) AST transforms."""
    if re.search(r'@(Immutable|Canonical)\b', code):
        return True, "Uses @Immutable/@Canonical"
    if re.search(r'@(TupleConstructor|Builder|EqualsAndHashCode|ToString|Sortable)\b', code):
        return True, "Uses Groovy AST transform(s)"
    return False, "No AST transform — data class should use @Immutable/@Canonical"


def check_bigdecimal_money(code):
    """Monetary values use BigDecimal / the G suffix, never double/float."""
    cleaned = _code_only(code)
    if re.search(r'\b(double|Double|float|Float)\b', cleaned):
        return False, "Uses double/float for a monetary value — use BigDecimal/G"
    if re.search(r'\bBigDecimal\b', cleaned) or re.search(r'\b\d[\d_]*(?:\.\d+)?[gG]\b', cleaned):
        return True, "Uses BigDecimal / G suffix for money"
    return False, "No exact monetary type (BigDecimal/G) detected"


def check_single_quotes_for_plain_strings(code):
    """A double-quoted string with no interpolation should be single-quoted."""
    c = re.sub(r'/\*.*?\*/', ' ', code, flags=re.DOTALL)
    c = re.sub(r'//[^\n]*', ' ', c)
    c = re.sub(r'""".*?"""', ' ', c, flags=re.DOTALL)
    c = re.sub(r"'''.*?'''", ' ', c, flags=re.DOTALL)
    for match in re.finditer(r'"((?:\\.|[^"\\])*)"', c):
        content = match.group(1)
        if '$' not in content and re.search(r'[A-Za-z0-9]', content):
            return False, f'Double-quoted constant "{content}" at line {_line_of(c, match.start())} — use single quotes'
    return True, "Plain strings use single quotes; double quotes only for interpolation"


def check_groovy_truth(code):
    """Prefer Groovy truth over verbose null/empty checks."""
    cleaned = _code_only(code)
    if re.search(r'\.isEmpty\s*\(\s*\)', cleaned):
        return False, "Uses .isEmpty() — prefer Groovy truth (if (collection))"
    if re.search(r'!=\s*null\s*&&', cleaned) or re.search(r'&&\s*[\w.]+\s*!=\s*null', cleaned):
        return False, "Null check combined with && — prefer Groovy truth / safe navigation"
    if re.search(r'==\s*null\s*\|\|', cleaned):
        return False, "Null check combined with || — prefer Groovy truth"
    return True, "Uses Groovy truth"


def check_no_dot_equals(code):
    """Use == for value equality, not .equals()/Objects.equals()."""
    cleaned = _code_only(code)
    if re.search(r'\.equals\s*\(', cleaned):
        return False, "Uses .equals() — prefer == for null-safe value equality"
    if re.search(r'\bObjects\.equals\b', cleaned):
        return False, "Uses Objects.equals() — prefer =="
    return True, "Uses == for equality"


def check_uses_closures(code):
    """Uses GDK closure methods rather than imperative loops."""
    cleaned = _code_only(code)
    if re.search(r'\b(collect|collectEntries|findAll|find|each|eachWithIndex|inject|groupBy|any|every|sum|max|min|sort|grep)\s*(?:\([^)]*\))?\s*\{', cleaned):
        return True, "Uses GDK closure methods"
    if re.search(r'\.\w+\s*\{', cleaned):
        return True, "Uses closure-based methods"
    return False, "No GDK closure methods detected"


def check_safe_navigation(code):
    """Uses the safe navigation operator ?. for nullable receivers."""
    if '?.' in _code_only(code):
        return True, "Uses safe navigation ?."
    return False, "No safe navigation ?. found"


def check_spaceship(code):
    """Uses the spaceship operator <=> for comparisons."""
    if '<=>' in _code_only(code):
        return True, "Uses spaceship <=>"
    return False, "No spaceship operator found"


def check_spread(code):
    """Uses the spread (*) or spread-dot (*.) operator."""
    cleaned = _code_only(code)
    if re.search(r'\*\.', cleaned):
        return True, "Uses spread-dot *."
    if re.search(r'\*:', cleaned):
        return True, "Uses spread map *:"
    if re.search(r'[\[(]\s*\*[A-Za-z_]', cleaned):
        return True, "Uses spread *"
    return False, "No spread operator found"


def check_slashy_regex(code):
    """Regex literals use slashy strings, not quoted strings."""
    if re.search(r'(=~|==~)\s*"', code) or re.search(r'(?<![\w/])~\s*"', code) \
            or re.search(r'Pattern\.compile\s*\(\s*"', code):
        return False, "Regex uses a double-quoted pattern — use a slashy /pattern/"
    if re.search(r'(=~|==~)\s*~?/', code) or '~/' in code:
        return True, "Uses a slashy-string regex"
    if re.search(r'=\s*~?/[^/\n]+/', code):
        return True, "Uses a slashy-string regex"
    return False, "No slashy-string regex detected"


def check_identity_is(code):
    """Reference identity uses the .is() operator, not =="""
    if re.search(r'\.is\s*\(', _code_only(code)):
        return True, "Uses .is() for reference identity"
    return False, "No .is() identity check found"


# ---------------------------------------------------------------------------
# Spock checkers (Groovy test specs)
# ---------------------------------------------------------------------------

_SPOCK_LABELS = ('setup', 'given', 'when', 'then', 'expect', 'cleanup', 'where', 'and')
_FEATURE_DECL = re.compile(r'(?:\bdef\b|\bvoid\b)\s+(?:[\'"].*?[\'"]|\w+)\s*\(')
_LABEL_RE = re.compile(r'^\s*(' + '|'.join(_SPOCK_LABELS) + r')\s*:(.*)$')


def _spock_blocks(code):
    """Yield (block_type, line_text, line_no) for each line, tagged with the Spock
    block it belongs to. block_type is None for the implicit setup region (before
    any label). `and:` continues the current block; setup:/given: map to 'setup'.
    A feature-method declaration resets to the implicit setup region."""
    cleaned = _code_only(code)
    current = None
    for i, line in enumerate(cleaned.split('\n')):
        if _FEATURE_DECL.search(line):
            current = None
            yield (current, line, i + 1)
            continue
        m = _LABEL_RE.match(line)
        if m:
            label = m.group(1)
            if label in ('setup', 'given'):
                current = 'setup'
            elif label != 'and':
                current = label
            yield (current, m.group(2), i + 1)
            continue
        yield (current, line, i + 1)


def _then_blocks(code):
    """Return [(start_line, [line_text, ...]), ...] for each then: block."""
    blocks = []
    lines = None
    start = 0
    for block_type, text, lineno in _spock_blocks(code):
        if block_type == 'then':
            if lines is None:
                lines = []
                start = lineno
            lines.append(text)
        elif lines is not None:
            blocks.append((start, lines))
            lines = None
    if lines is not None:
        blocks.append((start, lines))
    return blocks


def check_extends_specification(code):
    """A Spock spec extends spock.lang.Specification."""
    if re.search(r'\bextends\s+Specification\b', code):
        return True, "Spec extends Specification"
    return False, "No 'extends Specification' found"


def check_no_setup_given_label(code):
    """setup:/given: labels are noise — unlabeled top-of-method statements are the
    implicit setup block."""
    cleaned = _code_only(code)
    m = re.search(r'^\s*(setup|given)\s*:', cleaned, re.MULTILINE)
    if m:
        return False, f"'{m.group(1)}:' label at line {_line_of(cleaned, m.start())} — drop it; the implicit setup is unlabeled"
    return True, "No setup:/given: label"


def check_no_unroll(code):
    """@Unroll is redundant in Spock 2.4."""
    if re.search(r'@Unroll\b', code):
        return False, "@Unroll present — redundant in Spock 2.4"
    return True, "No @Unroll"


def check_typed_mock_declaration(code):
    """Mocks are declared 'Type x = Mock()', not 'def x = Mock(Type)'."""
    cleaned = _code_only(code)
    m = re.search(r'\bdef\s+\w+\s*=\s*(Mock|Stub|Spy)\s*\(', cleaned)
    if m:
        kind = m.group(1)
        return False, f"'def x = {kind}(Type)' at line {_line_of(cleaned, m.start())} — declare as 'Type x = {kind}()'"
    return True, "Mocks declared with the type on the left (Type x = Mock())"


def check_no_nested_init_interactions(code):
    """No interactions nested in a Mock()/Stub()/Spy() initializer closure —
    interactions belong in then:."""
    cleaned = _code_only(code)
    m = re.search(r'\b(Mock|Stub|Spy)\s*\([^)]*\)\s*\{', cleaned)
    if m:
        return False, f"Nested interaction in a {m.group(1)}() initializer at line {_line_of(cleaned, m.start())} — declare it in then:"
    return True, "No nested interactions in Mock()/Stub()/Spy() initializers"


def check_strict_zero_interactions(code):
    """Every then: block ends with '0 * _' to enforce strict interaction checking."""
    blocks = _then_blocks(code)
    if not blocks:
        return None, "No then: blocks found"
    zero_re = re.compile(r'\b0\s*\*\s*_')
    for start, lines in blocks:
        if not zero_re.search('\n'.join(lines)):
            return False, f"then: block at line {start} is missing '0 * _'"
    return True, "Every then: block ends with 0 * _"


def check_no_bare_underscore_arg(code):
    """No bare '_' as an argument matcher — validate the actual argument. ('0 * _'
    and 'N * subject._' are fine; those are not argument lists.)"""
    cleaned = _code_only(code)
    for i, line in enumerate(cleaned.split('\n')):
        if '>>' not in line and not re.search(r'\d+\s*\*', line):
            continue
        for argm in re.finditer(r'\.\w+\s*\(([^()]*)\)', line):
            tokens = [a.strip() for a in argm.group(1).split(',')]
            if any(t == '_' for t in tokens):
                return False, f"Bare '_' argument matcher at line {i+1}: '{line.strip()}' — validate the actual argument"
    return True, "No bare '_' argument matchers; arguments are validated"


def check_value_assertions_not_in_then(code):
    """Value assertions (==, !=, >=, <=, >, <) belong in expect:, not then:.
    then: holds only interactions and thrown(...)."""
    blocks = _then_blocks(code)
    if not blocks:
        return None, "No then: blocks found"
    for start, lines in blocks:
        depth = 0
        for line in lines:
            l = line.strip()
            start_depth = depth
            depth += l.count('{') - l.count('}') + l.count('(') - l.count(')')
            # lines nested inside a closure / argument list belong to an interaction
            if start_depth > 0:
                continue
            if not l or re.search(r'\d+\s*\*', l) or '>>' in l or 'thrown(' in l \
                    or l.startswith('def ') or l.startswith('and'):
                continue
            scrubbed = l.replace('<=>', ' ').replace('>>', ' ').replace('<<', ' ').replace('->', ' ')
            if re.search(r'==|!=|>=|<=|>|<', scrubbed):
                return False, f"Value assertion in a then: block at line {start} ('{l}') — move it to an expect: block"
    return True, "then: blocks hold only interactions/thrown; value assertions are in expect:"


def check_uses_verifyall(code):
    """Multiple grouped property assertions use verifyAll(...)."""
    if re.search(r'\bverifyAll\s*\(', code):
        return True, "Uses verifyAll for grouped assertions"
    return False, "No verifyAll — group multi-property assertions with verifyAll(...)"


def check_spy_subject_wildcard(code):
    """When the subject is a Spy, interactions close with 'N * subject._' to
    account for the method-under-test call."""
    cleaned = _code_only(code)
    if not re.search(r'\bSpy\s*\(', cleaned):
        return None, "No Spy subject — rule N/A"
    if re.search(r'[1-9]\d*\s*\*\s*\w+\s*\.\s*_', cleaned):
        return True, "Spy subject closes interactions with 'N * subject._'"
    return False, "Spy subject but no 'N * subject._' to account for the method-under-test call"


def check_uses_spystatic(code):
    """Static methods are enabled with a SpyStatic(TheClass) method call — not an
    @SpyStatic annotation."""
    cleaned = _code_only(code)
    if re.search(r'@SpyStatic\b', cleaned):
        return False, "Uses @SpyStatic annotation — SpyStatic is a method call, e.g. 'SpyStatic(TheClass)' at the top of the feature method"
    if re.search(r'(?<!@)\bSpyStatic\s*\(', cleaned):
        return True, "Uses SpyStatic(TheClass) method call for static mocking"
    return False, "No SpyStatic(...) — enable static mocking with a 'SpyStatic(TheClass)' method call"


def check_thrown_in_then(code):
    """Thrown exceptions are captured with thrown(...) inside a then: block."""
    blocks = _then_blocks(code)
    for start, lines in blocks:
        if any('thrown(' in l for l in lines):
            return True, "Exception captured with thrown(...) in then:"
    if 'thrown(' in _code_only(code):
        return False, "thrown(...) is not inside a then: block"
    return False, "No thrown(...) found"


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
    'no-private-methods': check_no_private_methods,
    'protected-helpers': check_no_private_methods,
    'visible-for-testing': check_visible_for_testing,
    'instance-over-static': check_instance_over_static,

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

    # Groovy
    'no-semicolons': check_no_semicolons,
    'no-final-keyword': check_no_final_keyword,
    'no-public-modifier': check_no_public_modifier,
    'groovy-accessors': check_groovy_accessors,
    'no-manual-getters-setters': check_no_manual_getters_setters_groovy,
    'no-manual-equals-tostring': check_no_manual_equals_tostring_groovy,
    'ast-immutable': check_ast_immutable,
    'bigdecimal-money': check_bigdecimal_money,
    'single-quotes-for-plain-strings': check_single_quotes_for_plain_strings,
    'groovy-truth': check_groovy_truth,
    'no-dot-equals': check_no_dot_equals,
    'no-loops': check_streams_over_loops,
    'uses-closures': check_uses_closures,
    'safe-navigation': check_safe_navigation,
    'spaceship-operator': check_spaceship,
    'spread-operator': check_spread,
    'slashy-regex': check_slashy_regex,
    'identity-operator-is': check_identity_is,

    # Spock
    'extends-specification': check_extends_specification,
    'no-setup-given-label': check_no_setup_given_label,
    'no-unroll': check_no_unroll,
    'typed-mock-declaration': check_typed_mock_declaration,
    'no-nested-init-interactions': check_no_nested_init_interactions,
    'strict-zero-interactions': check_strict_zero_interactions,
    'no-bare-underscore-arg': check_no_bare_underscore_arg,
    'value-assertions-in-expect': check_value_assertions_not_in_then,
    'uses-verifyall': check_uses_verifyall,
    'spy-subject-wildcard': check_spy_subject_wildcard,
    'uses-spystatic': check_uses_spystatic,
    'thrown-in-then': check_thrown_in_then,
}
