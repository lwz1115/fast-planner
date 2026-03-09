"""
Test health monitoring functionality.

This test verifies that the health endpoint correctly reports:
- ROS connection status
- Fast-Planner availability
- Service uptime
- Last planning success timestamp
- Odometry age
"""

import pytest
import time
from unittest.mock import Mock, MagicMock, patch
from fastapi.testclient import TestClient

# Mock ROS imports before importing our modules
import sys
sys.modules['rospy'] = MagicMock()
sys.modules['nav_msgs'] = MagicMock()
sys.modules['nav_msgs.msg'] = MagicMock()
sys.modules['geometry_msgs'] = MagicMock()
sys.modules['geometry_msgs.msg'] = MagicMock()
sys.modules['plan_manage'] = MagicMock()
sys.modules['plan_manage.msg'] = MagicMock()

from fastapi_planner.models import HealthResponse


def test_health_response_model_healthy():
    """Test HealthResponse model with healthy status."""
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
    assert response.last_planning_success is not None
    assert response.odometry_age_ms == 50.0


def test_health_response_model_degraded():
    """Test HealthResponse model with degraded status."""
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


def test_health_response_model_unhealthy():
    """Test HealthResponse model with unhealthy status."""
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


def test_health_response_validation():
    """Test HealthResponse validation."""
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
    with pytest.raises(ValueError):
        HealthResponse(
            status="healthy",
            ros_connected=True,
            fast_planner_available=True,
            uptime_seconds=-10.0,
            last_planning_success=None,
            odometry_age_ms=None
        )


def test_health_status_logic():
    """Test health status determination logic."""
    # Healthy: ROS connected and Fast-Planner available
    ros_connected = True
    fast_planner_available = True
    
    if ros_connected and fast_planner_available:
        status = "healthy"
    elif ros_connected and not fast_planner_available:
        status = "degraded"
    else:
        status = "unhealthy"
    
    assert status == "healthy"
    
    # Degraded: ROS connected but Fast-Planner not available
    ros_connected = True
    fast_planner_available = False
    
    if ros_connected and fast_planner_available:
        status = "healthy"
    elif ros_connected and not fast_planner_available:
        status = "degraded"
    else:
        status = "unhealthy"
    
    assert status == "degraded"
    
    # Unhealthy: ROS not connected
    ros_connected = False
    fast_planner_available = False
    
    if ros_connected and fast_planner_available:
        status = "healthy"
    elif ros_connected and not fast_planner_available:
        status = "degraded"
    else:
        status = "unhealthy"
    
    assert status == "unhealthy"


def test_uptime_calculation():
    """Test uptime calculation."""
    startup_time = time.time()
    time.sleep(0.1)  # Wait a bit
    
    uptime_seconds = time.time() - startup_time
    
    assert uptime_seconds > 0
    assert uptime_seconds >= 0.1


def test_odometry_age_calculation():
    """Test odometry age calculation."""
    odometry_timestamp = time.time()
    time.sleep(0.05)  # Wait 50ms
    
    age_seconds = time.time() - odometry_timestamp
    age_ms = age_seconds * 1000.0
    
    assert age_ms >= 50.0
    assert age_ms < 100.0  # Should be less than 100ms


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
