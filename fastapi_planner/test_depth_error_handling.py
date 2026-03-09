#!/usr/bin/env python3
"""
Test script for depth processing error handling.

This script verifies that custom exceptions are properly defined and
can be raised/caught correctly.
"""

import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_exception_imports():
    """Test that all depth processing exceptions can be imported."""
    logger.info("Testing exception imports...")
    
    try:
        from exceptions import (
            DepthProcessingException,
            InvalidDepthImageException,
            DepthImageDimensionMismatchException,
            InvalidDepthEncodingException,
            ROSPublishFailedException
        )
        logger.info("✓ All depth processing exceptions imported successfully")
        return True
        
    except ImportError as e:
        logger.error(f"✗ Exception import failed: {e}")
        return False


def test_exception_creation():
    """Test that exceptions can be created with proper attributes."""
    logger.info("Testing exception creation...")
    
    try:
        from exceptions import (
            InvalidDepthImageException,
            DepthImageDimensionMismatchException,
            InvalidDepthEncodingException,
            ROSPublishFailedException
        )
        
        # Test InvalidDepthImageException
        exc1 = InvalidDepthImageException(details="Test error")
        assert exc1.code == "invalid_depth_image"
        assert exc1.status_code == 400
        assert "Test error" in exc1.details
        logger.info(f"✓ InvalidDepthImageException: code={exc1.code}, status={exc1.status_code}")
        
        # Test DepthImageDimensionMismatchException
        exc2 = DepthImageDimensionMismatchException(
            expected_dims="640x480",
            actual_dims="320x240"
        )
        assert exc2.code == "dimension_mismatch"
        assert exc2.status_code == 400
        assert "640x480" in exc2.details
        assert "320x240" in exc2.details
        logger.info(f"✓ DepthImageDimensionMismatchException: code={exc2.code}, status={exc2.status_code}")
        
        # Test InvalidDepthEncodingException
        exc3 = InvalidDepthEncodingException(encoding="INVALID")
        assert exc3.code == "invalid_encoding"
        assert exc3.status_code == 400
        assert "INVALID" in exc3.message
        logger.info(f"✓ InvalidDepthEncodingException: code={exc3.code}, status={exc3.status_code}")
        
        # Test ROSPublishFailedException
        exc4 = ROSPublishFailedException(details="Publishing failed")
        assert exc4.code == "ros_publish_failed"
        assert exc4.status_code == 503
        assert "Publishing failed" in exc4.details
        logger.info(f"✓ ROSPublishFailedException: code={exc4.code}, status={exc4.status_code}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Exception creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_exception_handlers_import():
    """Test that exception handlers can be imported."""
    logger.info("Testing exception handler imports...")
    
    try:
        from error_handlers import (
            depth_processing_exception_handler,
            ros_publish_failed_exception_handler,
            register_exception_handlers
        )
        logger.info("✓ Exception handlers imported successfully")
        return True
        
    except ImportError as e:
        logger.error(f"✗ Exception handler import failed: {e}")
        return False


def test_depth_processor_raises_exceptions():
    """Test that depth processor raises custom exceptions."""
    logger.info("Testing depth processor exception raising...")
    
    try:
        from depth_processor import DepthProcessor
        from config import DepthConfig
        from exceptions import (
            InvalidDepthImageException,
            DepthImageDimensionMismatchException,
            InvalidDepthEncodingException
        )
        import base64
        
        # Create depth processor
        config = DepthConfig(min_depth=0.1, max_depth=10.0, voxel_size=0.05)
        processor = DepthProcessor(config)
        
        # Test 1: Invalid base64 data
        try:
            processor.decode_depth_image(
                "invalid_base64!!!",
                "16UC1",
                640,
                480
            )
            logger.error("✗ Should have raised InvalidDepthImageException for invalid base64")
            return False
        except InvalidDepthImageException as e:
            logger.info(f"✓ Correctly raised InvalidDepthImageException for invalid base64: {e.code}")
        
        # Test 2: Invalid encoding
        valid_base64 = base64.b64encode(b"test").decode('utf-8')
        try:
            processor.decode_depth_image(
                valid_base64,
                "INVALID_ENCODING",
                640,
                480
            )
            logger.error("✗ Should have raised InvalidDepthEncodingException")
            return False
        except InvalidDepthEncodingException as e:
            logger.info(f"✓ Correctly raised InvalidDepthEncodingException: {e.code}")
        
        # Test 3: Dimension mismatch (wrong size data)
        small_data = base64.b64encode(b"x" * 100).decode('utf-8')
        try:
            processor.decode_depth_image(
                small_data,
                "16UC1",
                640,
                480
            )
            logger.error("✗ Should have raised InvalidDepthImageException for size mismatch")
            return False
        except InvalidDepthImageException as e:
            logger.info(f"✓ Correctly raised InvalidDepthImageException for size mismatch: {e.code}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Depth processor exception test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_main_py_imports_exceptions():
    """Test that main.py imports the new exceptions."""
    logger.info("Testing main.py exception imports...")
    
    try:
        # Check that main.py contains the exception imports
        with open('fastapi_planner/main.py', 'r') as f:
            content = f.read()
            
        required_imports = [
            'InvalidDepthImageException',
            'DepthImageDimensionMismatchException',
            'InvalidDepthEncodingException',
            'ROSPublishFailedException'
        ]
        
        for imp in required_imports:
            if imp not in content:
                logger.error(f"✗ main.py does not import {imp}")
                return False
        
        logger.info("✓ main.py imports all required exceptions")
        return True
        
    except Exception as e:
        logger.error(f"✗ main.py import check failed: {e}")
        return False


def main():
    """Run all error handling tests."""
    logger.info("=" * 60)
    logger.info("Depth Processing Error Handling Verification")
    logger.info("=" * 60)
    
    tests = [
        test_exception_imports,
        test_exception_creation,
        test_exception_handlers_import,
        test_depth_processor_raises_exceptions,
        test_main_py_imports_exceptions
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            logger.info("")
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            logger.error(f"✗ Test {test.__name__} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    logger.info("")
    logger.info("=" * 60)
    logger.info(f"Test Results: {passed} passed, {failed} failed")
    logger.info("=" * 60)
    
    if failed == 0:
        logger.info("✓ All error handling tests passed!")
        logger.info("Depth processing error handling is properly implemented.")
    else:
        logger.error("✗ Some error handling tests failed.")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
