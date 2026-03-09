"""
Test logging configuration and functionality.

This test verifies that the logging system is properly configured
and can handle various logging scenarios.

Requirements: 8.5
"""

import logging
from io import StringIO

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logging_config import (
    configure_logging,
    get_logger,
    PerformanceLogger,
    StructuredFormatter
)


def test_logging_configuration():
    """Test that logging can be configured with different levels."""
    # Test INFO level
    configure_logging("INFO")
    logger = get_logger(__name__)
    assert logger.level <= logging.INFO
    
    # Test DEBUG level
    configure_logging("DEBUG")
    assert logger.level <= logging.DEBUG
    
    # Test WARNING level
    configure_logging("WARNING")
    assert logger.level <= logging.WARNING
    
    print("✓ Logging configuration test passed")


def test_structured_formatter():
    """Test that structured formatter adds request IDs and extra fields."""
    formatter = StructuredFormatter(
        fmt='%(asctime)s - [%(request_id)s] - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create a log record
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="Test message",
        args=(),
        exc_info=None
    )
    
    # Format without request_id
    formatted = formatter.format(record)
    assert "[-]" in formatted  # Default request_id
    assert "Test message" in formatted
    
    # Format with request_id
    record.request_id = "abc123"
    formatted = formatter.format(record)
    assert "[abc123]" in formatted
    
    print("✓ Structured formatter test passed")


def test_performance_logger():
    """Test performance logger functionality."""
    # Configure logging to capture output
    configure_logging("INFO")
    logger = get_logger(__name__)
    perf_logger = PerformanceLogger(logger)
    
    # Test timing log
    perf_logger.log_timing("test_operation", 45.3, success=True, algorithm="test")
    
    # Test rate log
    perf_logger.log_rate("success_rate", 95, 100)
    
    # Test counter log
    perf_logger.log_counter("request_count", 42)
    
    print("✓ Performance logger test passed")


def test_logger_hierarchy():
    """Test that loggers can be created with different names."""
    configure_logging("INFO")
    
    logger1 = get_logger("module1")
    logger2 = get_logger("module2")
    
    assert logger1.name == "module1"
    assert logger2.name == "module2"
    assert logger1 != logger2
    
    print("✓ Logger hierarchy test passed")


def test_log_levels():
    """Test that different log levels work correctly."""
    configure_logging("DEBUG")
    logger = get_logger(__name__)
    
    # Capture log output
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    
    # Log at different levels
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    
    output = stream.getvalue()
    assert "Debug message" in output
    assert "Info message" in output
    assert "Warning message" in output
    assert "Error message" in output
    
    print("✓ Log levels test passed")


def run_all_tests():
    """Run all logging tests."""
    print("\n=== Running Logging Tests ===\n")
    
    try:
        test_logging_configuration()
        test_structured_formatter()
        test_performance_logger()
        test_logger_hierarchy()
        test_log_levels()
        
        print("\n=== All Logging Tests Passed ===\n")
        return True
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}\n")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
