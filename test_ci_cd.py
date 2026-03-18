#!/usr/bin/env python3
"""Test script for hermes-loop plugin CI/CD verification."""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a shell command and return output."""
    print(f"\n>>> Running: {cmd}")
    result = subprocess.run(
        cmd, 
        shell=True, 
        capture_output=True, 
        text=True, 
        cwd=cwd
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr, file=sys.stderr)
    return result.returncode == 0

def main():
    """Run all verification tests."""
    
    plugin_path = Path.home() / ".hermes/plugins/hermes-loop"
    dist_path = plugin_path / "dist"
    
    print("=" * 60)
    print("HERMES-LOOP PLUGIN CI/CD VERIFICATION TEST")
    print("=" * 60)
    
    all_passed = True
    
    # Test 1: Check pyproject.toml exists and is valid
    print("\n[TEST 1] Checking pyproject.toml...")
    if not (plugin_path / "pyproject.toml").exists():
        print("FAIL: pyproject.toml not found!")
        all_passed = False
    else:
        print("PASS: pyproject.toml exists")
    
    # Test 2: Run python -m build and verify outputs
    print("\n[TEST 2] Building distribution packages...")
    os.chdir(plugin_path)
    if not run_command("python3 -m build"):
        all_passed = False
    
    # Check for wheel file
    wheel_files = list(dist_path.glob("*.whl"))
    if wheel_files:
        print(f"PASS: Wheel created: {wheel_files[0].name}")
    else:
        print("FAIL: No .whl file found in dist/")
        all_passed = False
    
    # Check for tarball file  
    tarball_files = list(dist_path.glob("*.tar.gz"))
    if tarball_files:
        print(f"PASS: Tarball created: {tarball_files[0].name}")
    else:
        print("FAIL: No .tar.gz file found in dist/")
        all_passed = False
    
    # Test 3: Install wheel in virtual environment
    print("\n[TEST 3] Testing pip installation...")
    venv_path = Path("/tmp/test-venv-install")
    
    if venv_path.exists():
        subprocess.run(f"rm -rf {venv_path}", shell=True)
    
    if not run_command("python3 -m venv /tmp/test-venv-install"):
        all_passed = False
    
    os.chdir("/tmp/test-venv-install")
    if not run_command("source bin/activate && pip install --upgrade pip 2>&1 | tail -3"):
        all_passed = False
        
    # Install the wheel
    whl_file = str(list(dist_path.glob("*.whl"))[0])
    if not run_command(f"source bin/activate && pip install {whl_file}"):
        all_passed = False
    
    # Verify installation
    print("\n[TEST 4] Verifying installed package...")
    result = subprocess.run(
        "source bin/activate && pip show hermes-loop-plugin", 
        shell=True, 
        capture_output=True, 
        text=True
    )
    if result.returncode == 0:
        print("PASS: Package successfully installed via pip install")
        for line in result.stdout.split('\n'):
            if line.startswith(('Name:', 'Version:', 'License:')):
                print(f"       {line}")
    else:
        print("FAIL: Could not verify installation")
        all_passed = False
    
    # Test 5: Check plugin registration
    print("\n[TEST 5] Verifying plugin tool registration...")
    
    expected_tools = [
        "init_loop",
        "loop_status", 
        "complete_task",
        "add_blocking_issue",
        "reset_loop",
        "set_completion_promise"
    ]
    
    # Check the __init__.py for registered tools
    init_file = plugin_path / "hermes_loop_plugin/__init__.py"
    if init_file.exists():
        with open(init_file) as f:
            content = f.read()
        
        missing_tools = []
        for tool in expected_tools:
            if f'name="{tool}"' in content or f"name=\"{tool}\"" in content:
                print(f"       ✓ {tool}")
            else:
                print(f"       ✗ {tool} NOT FOUND")
                missing_tools.append(tool)
        
        if not missing_tools:
            print("PASS: All 6 tools are registered in the plugin")
        else:
            print(f"FAIL: Missing tools: {missing_tools}")
            all_passed = False
    else:
        print("FAIL: __init__.py not found!")
        all_passed = False
    
    # Test 6: Check entry points configuration
    print("\n[TEST 6] Verifying entry point configuration...")
    pyproject_file = plugin_path / "pyproject.toml"
    if pyproject_file.exists():
        with open(pyproject_file) as f:
            content = f.read()
        
        if 'hermes_agent.plugins' in content and 'hermes-loop' in content:
            print("PASS: Entry points configured correctly")
            # Show the entry point line
            for line in content.split('\n'):
                if 'hermes-loop' in line.lower():
                    print(f"       {line.strip()}")
        else:
            print("FAIL: Entry points not properly configured")
            all_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    if all_passed:
        print("\n✓ ALL TESTS PASSED!")
        print("\nThe hermes-loop plugin is ready for distribution:")
        print(f"  - Wheel package: {dist_path / 'hermes_loop_plugin-1.0.0-py3-none-any.whl'}")
        print(f"  - Source tarball: {dist_path / 'hermes_loop_plugin-1.0.0.tar.gz'}")
        print("  - All 6 tools registered and available")
        return 0
    else:
        print("\n✗ SOME TESTS FAILED!")
        print("Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
