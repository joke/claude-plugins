#!/usr/bin/env python3
"""
Shared grader for Java coding convention evals.

Usage:
    python -m shared.grade <workspace-dir>

Expects structure:
    <workspace-dir>/
        eval-*/
            eval_metadata.json
            with_skill/outputs/*.java
            without_skill/outputs/*.java  (optional)
            old_skill/outputs/*.java      (optional)

Writes grading.json into each variant directory.
"""
import json
import os
import sys

from .checkers import CHECKERS


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
        checker = CHECKERS.get(aid)
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
    if len(sys.argv) > 1:
        base = sys.argv[1]
    else:
        base = os.getcwd()

    eval_dirs = sorted([
        d for d in os.listdir(base)
        if os.path.isdir(os.path.join(base, d)) and d.startswith('eval-')
    ])

    if not eval_dirs:
        print(f"No eval-* directories found in {base}")
        sys.exit(1)

    total_passed = 0
    total_assertions = 0

    for eval_dir_name in eval_dirs:
        eval_dir = os.path.join(base, eval_dir_name)
        for variant in ['with_skill', 'without_skill', 'old_skill']:
            variant_dir = os.path.join(eval_dir, variant)
            if not os.path.isdir(variant_dir):
                continue
            result = grade_eval(eval_dir, variant)
            out_path = os.path.join(variant_dir, 'grading.json')
            with open(out_path, 'w') as f:
                json.dump(result, f, indent=2)

            passed = sum(1 for e in result.get("expectations", []) if e.get("passed"))
            total = len(result.get("expectations", []))
            total_passed += passed
            total_assertions += total
            print(f"{eval_dir_name}/{variant}: {passed}/{total} passed")
            for e in result.get("expectations", []):
                status = "PASS" if e["passed"] else ("FAIL" if e["passed"] is False else "SKIP")
                print(f"  [{status}] {e['text']}: {e['evidence']}")

    print(f"\nTotal: {total_passed}/{total_assertions} passed")


if __name__ == '__main__':
    main()
