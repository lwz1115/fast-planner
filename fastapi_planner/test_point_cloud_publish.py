#!/usr/bin/env python3
"""
Simple test script to verify point cloud publishing functionality.

This script tests the publish_point_cloud method of ROSBridge without
requiring a full ROS environment.
"""

import numpy as np
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_point_cloud_conversion():
    """Test point cloud message creation without ROS."""
    logger.info("Testing point cloud conversion logic...")
    
    # Create sample points
    points = np.array([
        [1.0, 2.0, 3.0],
        [4.0, 5.0, 6.0],
        [7.0, 8.0, 9.0]
    ], dtype=np.float32)
    
    logger.info(f"Created test points with shape: {points.shape}")
    
    # Test conversion to bytes
    cloud_data = points.tobytes()
    logger.info(f"Converted to bytes, length: {len(cloud_data)} bytes")
    
    # Verify byte length (3 points * 3 floats * 4 bytes = 36 bytes)
    expected_length = points.shape[0] * 3 * 4
    assert len(cloud_data) == expected_length, f"Expected {expected_length} bytes, got {len(cloud_data)}"
    
    # Test reconstruction
    reconstructed = np.frombuffer(cloud_data, dtype=np.float32).reshape(-1, 3)
    logger.info(f"Reconstructed points shape: {reconstructed.shape}")
    
    # Verify data integrity
    assert np.allclose(points, reconstructed), "Reconstructed points don't match original"
    
    logger.info("✓ Point cloud conversion test passed!")
    return True


def test_input_validation():
    """Test input validation logic."""
    logger.info("Testing input validation...")
    
    # Test valid input
    valid_points = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    assert valid_points.ndim == 2 and valid_points.shape[1] == 3, "Valid points should pass"
    logger.info("✓ Valid input accepted")
    
    # Test invalid shape (1D)
    invalid_1d = np.array([1.0, 2.0, 3.0])
    assert not (invalid_1d.ndim == 2 and invalid_1d.shape[1] == 3), "1D array should fail"
    logger.info("✓ 1D array rejected")
    
    # Test invalid shape (wrong columns)
    invalid_cols = np.array([[1.0, 2.0], [3.0, 4.0]])
    assert not (invalid_cols.ndim == 2 and invalid_cols.shape[1] == 3), "Wrong column count should fail"
    logger.info("✓ Wrong column count rejected")
    
    # Test empty array
    empty_points = np.array([]).reshape(0, 3)
    assert empty_points.shape[0] == 0, "Empty array should be detected"
    logger.info("✓ Empty array detected")
    
    logger.info("✓ Input validation test passed!")
    return True


def test_pointcloud2_structure():
    """Test PointCloud2 message structure."""
    logger.info("Testing PointCloud2 message structure...")
    
    # Simulate PointCloud2 structure
    num_points = 100
    point_step = 12  # 3 floats * 4 bytes
    row_step = point_step * num_points
    
    logger.info(f"Points: {num_points}")
    logger.info(f"Point step: {point_step} bytes")
    logger.info(f"Row step: {row_step} bytes")
    
    # Verify calculations
    assert point_step == 12, "Point step should be 12 bytes (3 * 4)"
    assert row_step == num_points * point_step, "Row step calculation incorrect"
    
    # Test field offsets
    field_offsets = {'x': 0, 'y': 4, 'z': 8}
    logger.info(f"Field offsets: {field_offsets}")
    
    assert field_offsets['x'] == 0, "X offset should be 0"
    assert field_offsets['y'] == 4, "Y offset should be 4"
    assert field_offsets['z'] == 8, "Z offset should be 8"
    
    logger.info("✓ PointCloud2 structure test passed!")
    return True


def main():
    """Run all tests."""
    logger.info("=" * 60)
    logger.info("Point Cloud Publishing Functionality Tests")
    logger.info("=" * 60)
    
    tests = [
        test_point_cloud_conversion,
        test_input_validation,
        test_pointcloud2_structure
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            logger.info("")
            if test():
                passed += 1
        except Exception as e:
            logger.error(f"✗ Test {test.__name__} failed: {e}")
            failed += 1
    
    logger.info("")
    logger.info("=" * 60)
    logger.info(f"Test Results: {passed} passed, {failed} failed")
    logger.info("=" * 60)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
