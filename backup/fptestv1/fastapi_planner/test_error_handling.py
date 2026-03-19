"""
Simple test script to verify error handling functionality.

This script tests that the error handling system correctly:
1. Creates proper error responses
2. Maps exceptions to correct HTTP status codes
3. Includes all required error information
4. Logs errors appropriately

Requirements: 3.1, 3.2, 3.3, 3.4, 3.5
"""

import sys
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_exception_classes():
    """Test that custom exception classes work correctly."""
    from exceptions import (
        ValidationException,
        PlanningFailureException,
        ServiceUnavailableException,
        TimeoutException,
        NoPathFoundException,
        GoalInCollisionException,
        StartInCollisionException,
        PlanningTimeoutException,
        OdometryUnavailableException,
        ROSConnectionException,
        PositionOutOfBoundsException,
        InvalidAlgorithmException
    )
    
    logger.info("Testing exception classes...")
    
    # Test ValidationException
    exc = ValidationException("test_code", "Test message", "Test details")
    assert exc.code == "test_code"
    assert exc.message == "Test message"
    assert exc.details == "Test details"
    assert exc.status_code == 400
    logger.info("✓ ValidationException works correctly")
    
    # Test PlanningFailureException
    exc = PlanningFailureException("test_code", "Test message", "Test details")
    assert exc.status_code == 422
    logger.info("✓ PlanningFailureException works correctly")
    
    # Test ServiceUnavailableException
    exc = ServiceUnavailableException("test_code", "Test message", "Test details")
    assert exc.status_code == 503
    logger.info("✓ ServiceUnavailableException works correctly")
    
    # Test TimeoutException
    exc = TimeoutException("test_code", "Test message", "Test details")
    assert exc.status_code == 504
    logger.info("✓ TimeoutException works correctly")
    
    # Test specific exceptions
    exc = NoPathFoundException()
    assert exc.code == "no_path_found"
    assert exc.status_code == 422
    logger.info("✓ NoPathFoundException works correctly")
    
    exc = GoalInCollisionException()
    assert exc.code == "goal_in_collision"
    assert exc.status_code == 422
    logger.info("✓ GoalInCollisionException works correctly")
    
    exc = StartInCollisionException()
    assert exc.code == "start_in_collision"
    assert exc.status_code == 422
    logger.info("✓ StartInCollisionException works correctly")
    
    exc = PlanningTimeoutException(5.0)
    assert exc.code == "planning_timeout"
    assert exc.status_code == 504
    assert "5.0" in exc.message
    logger.info("✓ PlanningTimeoutException works correctly")
    
    exc = OdometryUnavailableException()
    assert exc.code == "odometry_unavailable"
    assert exc.status_code == 503
    logger.info("✓ OdometryUnavailableException works correctly")
    
    exc = ROSConnectionException()
    assert exc.code == "ros_disconnected"
    assert exc.status_code == 503
    logger.info("✓ ROSConnectionException works correctly")
    
    exc = PositionOutOfBoundsException("start", "X=[0, 10], Y=[0, 10], Z=[0, 5]")
    assert exc.code == "start_out_of_bounds"
    assert exc.status_code == 400
    logger.info("✓ PositionOutOfBoundsException works correctly")
    
    exc = InvalidAlgorithmException("invalid", ["kinodynamic", "topological"])
    assert exc.code == "invalid_algorithm"
    assert exc.status_code == 400
    logger.info("✓ InvalidAlgorithmException works correctly")
    
    logger.info("All exception classes passed!")
    return True


def test_error_response_creation():
    """Test that error responses are created correctly."""
    from error_handlers import create_error_response
    from models import ErrorInfo
    
    logger.info("Testing error response creation...")
    
    # Create error response
    response = create_error_response(
        status_code=400,
        error_code="test_error",
        message="Test error message",
        details="Test error details"
    )
    
    assert response.status_code == 400
    content = response.body.decode('utf-8')
    assert "test_error" in content
    assert "Test error message" in content
    assert "Test error details" in content
    
    logger.info("✓ Error response creation works correctly")
    logger.info("Error response creation test passed!")
    return True


def test_error_info_model():
    """Test that ErrorInfo model works correctly."""
    from models import ErrorInfo
    
    logger.info("Testing ErrorInfo model...")
    
    # Create ErrorInfo instance
    error = ErrorInfo(
        code="test_code",
        message="Test message",
        details="Test details"
    )
    
    assert error.code == "test_code"
    assert error.message == "Test message"
    assert error.details == "Test details"
    
    # Test serialization
    error_dict = error.dict()
    assert error_dict["code"] == "test_code"
    assert error_dict["message"] == "Test message"
    assert error_dict["details"] == "Test details"
    
    logger.info("✓ ErrorInfo model works correctly")
    logger.info("ErrorInfo model test passed!")
    return True


def run_all_tests():
    """Run all error handling tests."""
    logger.info("=" * 60)
    logger.info("Running Error Handling Tests")
    logger.info("=" * 60)
    
    tests = [
        ("Exception Classes", test_exception_classes),
        ("Error Response Creation", test_error_response_creation),
        ("ErrorInfo Model", test_error_info_model),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        logger.info("")
        logger.info(f"Running: {test_name}")
        logger.info("-" * 60)
        try:
            if test_func():
                passed += 1
                logger.info(f"✓ {test_name} PASSED")
            else:
                failed += 1
                logger.error(f"✗ {test_name} FAILED")
        except Exception as e:
            failed += 1
            logger.error(f"✗ {test_name} FAILED with exception: {e}", exc_info=True)
    
    logger.info("")
    logger.info("=" * 60)
    logger.info(f"Test Results: {passed} passed, {failed} failed")
    logger.info("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
