"""
Pytest configuration for robust test cleanup.

This ensures Docker resources are cleaned up even if tests fail unexpectedly.
"""

import pytest
import atexit
from tests.helpers.cleanup import emergency_cleanup


@pytest.fixture(scope="session", autouse=True)
def ensure_cleanup_on_exit():
    """Ensure cleanup runs even if tests crash or are interrupted."""
    # Register cleanup to run when Python exits
    atexit.register(emergency_cleanup)
    
    yield
    
    # Also run cleanup at end of test session
    emergency_cleanup()


@pytest.fixture(autouse=True)  
def cleanup_between_tests():
    """Clean up any orphaned resources between individual tests."""
    yield
    
    # Quick check for orphaned containers between tests
    import subprocess
    try:
        result = subprocess.run([
            "docker", "ps", "-q", "--filter", "name=test"
        ], capture_output=True, text=True, timeout=10)
        
        if result.stdout.strip():
            print("⚠️ Found orphaned test containers, cleaning up...")
            emergency_cleanup()
    except:
        pass  # Don't let cleanup checking break tests


def pytest_sessionfinish(session, exitstatus):
    """Hook that runs when pytest session finishes."""
    print("\n🧹 Running final test cleanup...")
    emergency_cleanup()


def pytest_keyboard_interrupt(excinfo):
    """Hook that runs when tests are interrupted with Ctrl+C."""
    print("\n🛑 Test interrupted, running emergency cleanup...")
    emergency_cleanup()