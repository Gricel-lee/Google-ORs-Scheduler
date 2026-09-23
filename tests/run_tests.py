#!/usr/bin/env python3
"""
run_tests.py  —  Run planning_generator.py on each test JSON, execute the
generated solver, and check the result against the expected makespan.

Usage (from repo root):
    python tests/run_tests.py

Each test JSON may optionally contain a top-level "_expected" key:
    {
        "_expected": {
            "feasible": true,
            "makespan": 18
        }
    }
If "makespan" is present the runner asserts the solver's objective matches it.
If "feasible" is false it asserts no solution is found.
"""

import json
import os
import re
import subprocess
import sys
import tempfile

TESTS_DIR   = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT   = os.path.dirname(TESTS_DIR)
GENERATOR   = os.path.join(REPO_ROOT, 'main_generator.py')
PYTHON      = sys.executable

TEST_FILES = [
    'test_single_agent_linear.json',
    'test_two_agents_parallel.json',
    'test_virtual_node_choice.json',
    'test_derived_optional.json',
    'test_interchangeable_direction.json',
    'example.json',   # the canonical example — expected makespan 62
    'ex4.json',       # OR-dep, single agent, expected makespan 10
    'ex5.json',       # OR-dep, two agents, expected makespan 10
    'test_agri_2rows.json',  # row-scaling: solves in <1s
    'test_agri_5rows.json',  # row-scaling: solves in ~1s
    'test_agri_6rows.json',  # row-scaling: solves in ~1 min — combinatorial wall
                              # starts here; 7+ rows can take 5+ min or never finish,
                              # so they're deliberately excluded from routine runs
]


def run_test(json_path: str) -> tuple[bool, str]:
    """Generate solver, run it, check against _expected. Returns (passed, message)."""
    name = os.path.basename(json_path)

    with open(json_path) as f:
        data = json.load(f)
    expected = data.get('_expected', {})

    with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as tmp:
        solver_path = tmp.name

    try:
        # 1. Generate solver
        gen = subprocess.run(
            [PYTHON, GENERATOR, json_path, solver_path],
            capture_output=True, text=True
        )
        if gen.returncode != 0:
            return False, f'Generator failed:\n{gen.stderr.strip()}'

        # 2. Execute solver
        # 90s to accommodate test_agri_6rows.json (~1 min) — everything else
        # finishes well under that, so this only affects the slow cases.
        run = subprocess.run(
            [PYTHON, solver_path],
            capture_output=True, text=True, timeout=90
        )
        output = run.stdout + run.stderr

        if run.returncode != 0:
            return False, f'Solver crashed:\n{output.strip()}'

        no_solution = 'No solution' in output
        expected_feasible = expected.get('feasible', True)

        if expected_feasible and no_solution:
            return False, 'Expected feasible solution but solver found none.'
        if not expected_feasible and not no_solution:
            return False, 'Expected infeasible but solver found a solution.'

        if no_solution:
            return True, 'Correctly reported no solution.'

        # Parse makespan from "Solution — makespan: N min"
        m = re.search(r'makespan:\s*(\d+)', output)
        if m is None:
            return False, f'Could not parse makespan from output:\n{output.strip()}'

        actual = int(m.group(1))
        exp_makespan = expected.get('makespan')

        if exp_makespan is not None and actual != exp_makespan:
            return False, (
                f'Makespan mismatch: expected {exp_makespan}, got {actual}.\n'
                f'Solver output:\n{output.strip()}'
            )

        note = f'  (expected {exp_makespan})' if exp_makespan else ''
        return True, f'makespan = {actual}{note}'

    except subprocess.TimeoutExpired:
        return False, 'Solver timed out (>90 s).'
    finally:
        os.unlink(solver_path)


def main():
    passed = 0
    failed = 0

    for fname in TEST_FILES:
        json_path = os.path.join(TESTS_DIR, fname)
        if not os.path.exists(json_path):
            # example.json lives in the repo root, not in tests/
            json_path = os.path.join(REPO_ROOT, fname)
        if not os.path.exists(json_path):
            print(f'[ SKIP ] {fname}  (file not found)')
            continue

        ok, msg = run_test(json_path)
        status = '[ PASS ]' if ok else '[ FAIL ]'
        print(f'{status} {fname}')
        print(f'         {msg}')
        if ok:
            passed += 1
        else:
            failed += 1

    print(f'\n{passed} passed, {failed} failed.')
    sys.exit(0 if failed == 0 else 1)


if __name__ == '__main__':
    main()
