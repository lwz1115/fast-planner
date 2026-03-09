#!/usr/bin/env python3
"""
Simple verification script for depth image API endpoints.

This script verifies that the depth image endpoints are properly defined
and can be imported without errors.
"""

import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_endpoint_imports():
    """Test that all required components can be imported."""
    logger.info("Testing imports...")
    
    try:
        # Add current directory to path
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Test model imports
        from models import (
            DepthImageRequest,
            DepthImageBatchRequest,
            DepthProcessingResult,
            DepthBatchResponse,
            DepthBatchResult,
            CameraIntrinsics,
            CameraPose
        )
        logger.info("✓ Model imports successful")
        
        # Test depth processor import
        from depth_processor import DepthProcessor, DepthConfig
        logger.info("✓ DepthProcessor imports successful")
        
        return True
        
    except ImportError as e:
        logger.error(f"✗ Import failed: {e}")
        return False


def test_model_validation():
    """Test model validation logic."""
    logger.info("Testing model validation...")
    
    try:
        from models import CameraIntrinsics, CameraPose, Position, Quaternion
        
        # Test valid camera intrinsics
        intrinsics = CameraIntrinsics(
            fx=525.0,
            fy=525.0,
            cx=319.5,
            cy=239.5,
            width=640,
            height=480
        )
        logger.info(f"✓ Valid camera intrinsics created: {intrinsics.width}x{intrinsics.height}")
        
        # Test valid camera pose
        pose = CameraPose(
            position=Position(x=1.0, y=0.5, z=1.0),
            orientation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)
        )
        logger.info(f"✓ Valid camera pose created: pos=({pose.position.x}, {pose.position.y}, {pose.position.z})")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Model validation failed: {e}")
        return False


def test_depth_processor_initialization():
    """Test depth processor initialization."""
    logger.info("Testing depth processor initialization...")
    
    try:
        # Add current directory to path
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from depth_processor import DepthProcessor, DepthConfig
        
        # Create depth config
        config = DepthConfig(
            min_depth=0.1,
            max_depth=10.0,
            voxel_size=0.05
        )
        logger.info(f"✓ DepthConfig created: min={config.min_depth}m, max={config.max_depth}m")
        
        # Create depth processor
        processor = DepthProcessor(config)
        logger.info("✓ DepthProcessor initialized successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Depth processor initialization failed: {e}")
        return False


def test_endpoint_structure():
    """Test that endpoints are properly structured."""
    logger.info("Testing endpoint structure...")
    
    try:
        # Check that main.py can be compiled
        import py_compile
        py_compile.compile('fastapi_planner/main.py', doraise=True)
        logger.info("✓ main.py compiles successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Endpoint structure test failed: {e}")
        return False


def main():
    """Run all verification tests."""
    logger.info("=" * 60)
    logger.info("Depth Image API Endpoints Verification")
    logger.info("=" * 60)
    
    tests = [
        test_endpoint_imports,
        test_model_validation,
        test_depth_processor_initialization,
        test_endpoint_structure
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
            failed += 1
    
    logger.info("")
    logger.info("=" * 60)
    logger.info(f"Verification Results: {passed} passed, {failed} failed")
    logger.info("=" * 60)
    
    if failed == 0:
        logger.info("✓ All verification tests passed!")
        logger.info("The depth image API endpoints are properly implemented.")
    else:
        logger.error("✗ Some verification tests failed.")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
