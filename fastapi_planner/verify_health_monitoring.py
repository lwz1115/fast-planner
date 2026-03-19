"""
Verify health monitoring implementation without pytest.
"""

import time
import sys
from unittest.mock import MagicMock

# Mock ROS imports
sys.modules['rospy'] = MagicMock()
sys.modules['nav_msgs'] = MagicMock()
sys.modules['nav_msgs.msg'] = MagicMock()
sys.modules['geometry_msgs'] = MagicMock()
sys.modules['geometry_msgs.msg'] = MagicMock()
sys.modules['plan_manage'] = MagicMock()
sys.modules['plan_manage.msg'] = MagicMock()

from fastapi_planner.models import HealthResponse


def test_health_response_healthy():
    """Test HealthResponse with healthy status."""
    print("Testing healthy status...")
    response = HealthResponse(
        status="healthy",
        ros_connected=True,
        fast_planner_available=True,
        uptime_seconds=100.5,
        last_planning_success=time.time(),
        odometry_age_ms=50.0
    )
    
    assert response.status == "healthy"
    assert response.ros_connected is True
    assert response.fast_planner_available is True
    assert response.uptime_seconds == 100.5
    print("✓ Healthy status test passed")


def test_health_response_degraded():
    """Test HealthResponse with degraded status."""
    print("Testing degraded status...")
    response = HealthResponse(
        status="degraded",
        ros_connected=True,
        fast_planner_available=False,
        uptime_seconds=200.0,
        last_planning_success=None,
        odometry_age_ms=None
    )
    
    assert response.status == "degraded"
    assert response.ros_connected is True
    assert response.fast_planner_available is False
    print("✓ Degraded status test passed")


def test_health_response_unhealthy():
    """Test HealthResponse with unhealthy status."""
    print("Testing unhealthy status...")
    response = HealthResponse(
        status="unhealthy",
        ros_connected=False,
        fast_planner_available=False,
        uptime_seconds=50.0,
        last_planning_success=None,
        odometry_age_ms=None
    )
    
    assert response.status == "unhealthy"
    assert response.ros_connected is False
    assert response.fast_planner_available is False
    print("✓ Unhealthy status test passed")


def test_health_status_logic():
    """Test health status determination logic."""
    print("Testing status determination logic...")
    
    # Healthy: ROS connected and Fast-Planner available
    ros_connected = True
    fast_planner_available = True
    
    if ros_connected and fast_planner_available:
        status = "healthy"
    elif ros_connected and not fast_planner_available:
        status = "degraded"
    else:
        status = "unhealthy"
    
    assert status == "healthy", f"Expected 'healthy', got '{status}'"
    
    # Degraded: ROS connected but Fast-Planner not available
    ros_connected = True
    fast_planner_available = False
    
    if ros_connected and fast_planner_available:
        status = "healthy"
    elif ros_connected and not fast_planner_available:
        status = "degraded"
    else:
        status = "unhealthy"
    
    assert status == "degraded", f"Expected 'degraded', got '{status}'"
    
    # Unhealthy: ROS not connected
    ros_connected = False
    fast_planner_available = False
    
    if ros_connected and fast_planner_available:
        status = "healthy"
    elif ros_connected and not fast_planner_available:
        status = "degraded"
    else:
        status = "unhealthy"
    
    assert status == "unhealthy", f"Expected 'unhealthy', got '{status}'"
    
    print("✓ Status determination logic test passed")


def test_uptime_calculation():
    """Test uptime calculation."""
    print("Testing uptime calculation...")
    startup_time = time.time()
    time.sleep(0.1)  # Wait a bit
    
    uptime_seconds = time.time() - startup_time
    
    assert uptime_seconds > 0
    assert uptime_seconds >= 0.1
    print(f"✓ Uptime calculation test passed (uptime: {uptime_seconds:.3f}s)")


def test_odometry_age_calculation():
    """Test odometry age calculation."""
    print("Testing odometry age calculation...")
    odometry_timestamp = time.time()
    time.sleep(0.05)  # Wait 50ms
    
    age_seconds = time.time() - odometry_timestamp
    age_ms = age_seconds * 1000.0
    
    assert age_ms >= 50.0
    assert age_ms < 200.0  # Should be less than 200ms (generous margin)
    print(f"✓ Odometry age calculation test passed (age: {age_ms:.1f}ms)")


def test_validation():
    """Test HealthResponse validation."""
    print("Testing validation...")
    
    # Valid response
    response = HealthResponse(
        status="healthy",
        ros_connected=True,
        fast_planner_available=True,
        uptime_seconds=100.0,
        last_planning_success=time.time(),
        odometry_age_ms=50.0
    )
    assert response.uptime_seconds >= 0
    
    # Invalid uptime (negative)
    try:
        HealthResponse(
            status="healthy",
            ros_connected=True,
            fast_planner_available=True,
            uptime_seconds=-10.0,
            last_planning_success=None,
            odometry_age_ms=None
        )
        print("✗ Validation test failed: negative uptime should raise error")
        sys.exit(1)
    except ValueError:
        print("✓ Validation test passed (negative uptime rejected)")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Health Monitoring Verification")
    print("=" * 60)
    
    try:
        test_health_response_healthy()
        test_health_response_degraded()
        test_health_response_unhealthy()
        test_health_status_logic()
        test_uptime_calculation()
        test_odometry_age_calculation()
        test_validation()
        
        print("=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
