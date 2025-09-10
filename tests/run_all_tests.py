#!/usr/bin/env python3
"""Main test runner for the AI Agent System."""

import sys
import os
import subprocess
from pathlib import Path


def run_test_file(test_file: str) -> bool:
    """Run a single test file and return success status."""
    print(f"\n🧪 Running: {test_file}")
    print("-" * 50)

    try:
        # Change to project root directory
        project_root = Path(__file__).parent.parent
        os.chdir(project_root)

        # Set PYTHONPATH to include src directory
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{project_root}/src:{env.get('PYTHONPATH', '')}"

        # Run the test file
        result = subprocess.run(
            [sys.executable, str(test_file)],
            capture_output=True,
            text=True,
            timeout=60,
            env=env,
        )

        if result.returncode == 0:
            print(f"✅ {test_file} - PASSED")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"❌ {test_file} - FAILED")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print(f"⏰ {test_file} - TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 {test_file} - ERROR: {e}")
        return False


def main():
    """Run all tests in the system."""
    print("🚀 AI Agent System - Complete Test Suite")
    print("=" * 60)

    # Define test categories
    test_categories = {
        "End-to-End Tests": ["tests/end_to_end/test_system_ready.py"],
        "Integration Tests": [
            "tests/integration/test_phase2_autogen_qdrant_llm.py",
            "tests/integration/test_phase5_1_agile_agent.py",
            "tests/integration/test_phase5_2_project_generation.py",
            "tests/integration/test_qdrant_integration.py",
        ],
        "Unit Tests": [
            "tests/test_phase3_coordinator.py",
            "tests/test_enhanced_server.py",
        ],
    }

    total_tests = 0
    passed_tests = 0

    # Run tests by category
    for category, test_files in test_categories.items():
        print(f"\n📋 {category}")
        print("-" * 40)

        for test_file in test_files:
            if os.path.exists(test_file):
                total_tests += 1
                if run_test_file(test_file):
                    passed_tests += 1
            else:
                print(f"⚠️  {test_file} - NOT FOUND")

    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(
        f"Success Rate: {(passed_tests/total_tests)*100:.1f}%"
        if total_tests > 0
        else "No tests found"
    )

    if passed_tests == total_tests:
        print("\n🎉 All tests passed! System is ready.")
        return 0
    else:
        print(
            f"\n⚠️  {total_tests - passed_tests} tests failed. Check the output above."
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
