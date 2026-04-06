#!/usr/bin/env python3
"""Grader for java8-coding-conventions evals."""
import json
import re
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))


def read_java_files(directory):
    """Read all .java files in directory, return concatenated content."""
    content = ""
    if not os.path.isdir(directory):
        return content
    for f in sorted(os.listdir(directory)):
        if f.endswith(".java"):
            with open(os.path.join(directory, f)) as fh:
                content += fh.read() + "\n"
    return content


def check_all_vars_final(code):
    """Check that all local variables and method parameters use final."""
    # Check method/constructor parameters
    # Only match lines starting with access modifiers (real declarations, not lambda bodies)
    method_pattern = re.compile(
        r'^\s+(?:public|private|protected)\s+(?:static\s+)?(?:\w+(?:<[^>]+>)?\s+)?(\w+)\s*\(([^)]*)\)',
        re.MULTILINE
    )
    for match in method_pattern.finditer(code):
        params_str = match.group(2).strip()
        if not params_str:
            continue
        # Split by comma, handling generics
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
            # Skip annotations
            while param.startswith('@'):
                param = re.sub(r'^@\w+(\([^)]*\))?\s*', '', param)
            if not param.startswith('final '):
                return False, f"Parameter not final: '{param}'"

    # Check local variable declarations
    lines = code.split('\n')
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Skip non-code lines
        if not stripped or stripped.startswith('//') or stripped.startswith('*') or stripped.startswith('/*'):
            continue
        if stripped.startswith('import') or stripped.startswith('package') or stripped.startswith('@'):
            continue
        if stripped.startswith('return') or stripped.startswith('throw') or stripped.startswith('if') or stripped.startswith('} '):
            continue
        # Skip field declarations (private/public/protected/static)
        if re.match(r'(private|public|protected|static)', stripped):
            continue
        # Look for: Type varname = ... (not final)
        local_match = re.match(r'([A-Z][\w]*(?:<[^>]+>)?(?:\[\])?)\s+(\w+)\s*=', stripped)
        if local_match and not stripped.startswith('final '):
            return False, f"Local variable not final at line {i+1}: '{stripped}'"

    return True, "All variables and parameters use final"


def check_no_checked_exceptions(code):
    """Check no throws clause with checked exception types."""
    # Look for 'throws' in method signatures
    throws_pattern = re.compile(r'\)\s*throws\s+\w+')
    match = throws_pattern.search(code)
    if match:
        return False, f"Found throws clause: '{match.group(0).strip()}'"
    return True, "No checked exceptions in signatures"


def check_streams_over_loops(code):
    """Check no for/while loops remain."""
    # Look for for( or while( but not in comments
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
    # Look for methods that likely return nullable but don't use Optional
    method_pattern = re.compile(r'public\s+(\w+(?:<[^>]+>)?)\s+(find\w+|get\w+ById|lookup\w+)\s*\(')
    for match in method_pattern.finditer(code):
        return_type = match.group(1)
        method_name = match.group(2)
        if 'find' in method_name.lower() and not return_type.startswith('Optional') and not return_type.startswith('List'):
            return False, f"Method '{method_name}' returns '{return_type}' instead of Optional"
    return True, "Find/lookup methods return Optional"


def check_immutable_fields(code):
    """Check all instance fields are private final."""
    lines = code.split('\n')
    brace_depth = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        brace_depth += stripped.count('{') - stripped.count('}')

        # Only check at class body level (depth == 1)
        if brace_depth != 1:
            continue

        # Skip class/interface declarations, methods, constructors, annotations, comments
        if re.match(r'(public|private|protected)?\s*(static\s+)?(final\s+)?(abstract\s+)?(class|interface|enum)\s+', stripped):
            continue
        if '(' in stripped:  # method or constructor
            continue
        if stripped.startswith('//') or stripped.startswith('*') or stripped.startswith('@'):
            continue
        if not stripped or stripped == '}':
            continue

        # This should be a field declaration
        if re.match(r'(private|public|protected)\s+', stripped):
            if 'static final' in stripped or 'final static' in stripped:
                continue  # constants are fine
            if 'private final' not in stripped and 'private static' not in stripped:
                return False, f"Non-final field at line {i+1}: '{stripped}'"
    return True, "All fields are private final"


def check_small_methods(code):
    """Check no method exceeds ~15 lines of logic."""
    lines = code.split('\n')
    method_start = None
    method_name = None
    brace_depth = 0
    method_depth = 0

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Detect method start
        if method_start is None and re.match(r'(public|private|protected)\s+', stripped) and '(' in stripped:
            if '{' in stripped:
                method_start = i
                method_name = stripped
                method_depth = brace_depth
                brace_depth += stripped.count('{') - stripped.count('}')
                continue

        brace_depth += stripped.count('{') - stripped.count('}')

        if method_start is not None and brace_depth <= method_depth:
            length = i - method_start
            if length > 20:
                return False, f"Long method (~{length} lines) starting at line {method_start+1}"
            method_start = None
            method_name = None

    return True, "All methods are reasonably small"


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
        # Stream.toList() without Collectors
        if re.search(r'\.stream\(\)[^;]*\.toList\(\)', code):
            issues.append("Stream.toList() (Java 16)")
    if issues:
        return False, "Java 9+ features found: " + ", ".join(issues)
    return True, "No Java 9+ features"


def check_no_setters(code):
    """Check no setter methods exist."""
    setter = re.search(r'public\s+void\s+set\w+\s*\(', code)
    if setter:
        return False, f"Setter found: '{setter.group(0).strip()}'"
    return True, "No setter methods"


def check_constructor_sets_all(code):
    """Check there's a constructor that accepts all fields."""
    # Count fields
    lines = code.split('\n')
    fields = []
    for line in lines:
        stripped = line.strip()
        if re.match(r'private\s+final\s+\w+(?:<[^>]+>)?\s+\w+;', stripped):
            fields.append(stripped)

    # Find constructor params
    constr = re.search(r'public\s+\w+\s*\(([^)]*)\)', code)
    if not constr:
        # Check for private constructor with builder
        constr = re.search(r'private\s+\w+\s*\(([^)]*)\)', code)
        if constr and 'Builder' in constr.group(1):
            return False, "Uses Builder pattern instead of direct constructor"

    if not constr:
        return False, "No constructor found"

    params = [p.strip() for p in constr.group(1).split(',') if p.strip()]
    if len(params) < len(fields):
        return False, f"Constructor has {len(params)} params but {len(fields)} fields"

    return True, "Constructor accepts all fields"


def check_unmodifiable_collections(code):
    """Check collection getters return unmodifiable views."""
    if 'Collections.unmodifiable' in code or 'unmodifiableList' in code:
        return True, "Uses unmodifiable collections"
    if re.search(r'List<', code) or re.search(r'Set<', code) or re.search(r'Map<', code):
        return False, "Has collection fields but no unmodifiable wrapper found"
    return True, "No collections to wrap"


def check_constructor_injection(code):
    """Check dependencies via constructor, no field/setter injection."""
    if re.search(r'@Inject\s', code) or re.search(r'@Autowired\s', code):
        # Check if it's on constructor
        if re.search(r'@(Inject|Autowired)\s+.*\w+\s*;', code):
            return False, "Field injection detected"
    # Check constructor exists and sets repository
    if re.search(r'this\.\w+\s*=\s*\w+', code):
        return True, "Constructor injection used"
    return False, "No constructor injection detected"


ASSERTION_CHECKERS = {
    'all-vars-final': check_all_vars_final,
    'no-checked-exceptions': check_no_checked_exceptions,
    'streams-over-loops': check_streams_over_loops,
    'streams-everywhere': check_streams_over_loops,
    'optional-not-null': check_optional_returns,
    'optional-for-find': check_optional_returns,
    'immutable-fields': check_immutable_fields,
    'small-methods': check_small_methods,
    'no-java9-features': check_no_java9_features,
    'no-setters': check_no_setters,
    'constructor-sets-all': check_constructor_sets_all,
    'unmodifiable-collections': check_unmodifiable_collections,
    'constructor-injection': check_constructor_injection,
}


def grade_eval(eval_dir, variant):
    """Grade a single eval variant."""
    outputs_dir = os.path.join(eval_dir, variant, 'outputs')
    meta_path = os.path.join(eval_dir, 'eval_metadata.json')

    with open(meta_path) as f:
        meta = json.load(f)

    code = read_java_files(outputs_dir)
    if not code:
        return {"error": f"No Java files in {outputs_dir}"}

    results = {
        "eval_id": meta["eval_id"],
        "eval_name": meta["eval_name"],
        "variant": variant,
        "expectations": []
    }

    for assertion in meta.get("assertions", []):
        aid = assertion["id"]
        checker = ASSERTION_CHECKERS.get(aid)
        if checker:
            passed, evidence = checker(code)
        else:
            passed, evidence = None, f"No checker for '{aid}'"

        results["expectations"].append({
            "text": assertion["text"],
            "passed": passed,
            "evidence": evidence
        })

    return results


def main():
    eval_dirs = sorted([
        d for d in os.listdir(BASE)
        if os.path.isdir(os.path.join(BASE, d)) and d.startswith('eval-')
    ])

    for eval_dir_name in eval_dirs:
        eval_dir = os.path.join(BASE, eval_dir_name)
        for variant in ['with_skill', 'without_skill']:
            variant_dir = os.path.join(eval_dir, variant)
            if not os.path.isdir(variant_dir):
                continue
            result = grade_eval(eval_dir, variant)
            out_path = os.path.join(variant_dir, 'grading.json')
            with open(out_path, 'w') as f:
                json.dump(result, f, indent=2)

            passed = sum(1 for e in result.get("expectations", []) if e.get("passed"))
            total = len(result.get("expectations", []))
            print(f"{eval_dir_name}/{variant}: {passed}/{total} passed")
            for e in result.get("expectations", []):
                status = "PASS" if e["passed"] else "FAIL"
                print(f"  [{status}] {e['text']}: {e['evidence']}")


if __name__ == '__main__':
    main()
