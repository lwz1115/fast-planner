"""
Data models for FastAPI-Fast-Planner Interface.

This module defines Pydantic models for request/response validation,
including position data, planning requests, trajectories, and error responses.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, validator, root_validator
import logging


logger = logging.getLogger(__name__)


class Position(BaseModel):
    """3D position coordinates."""
    x: float = Field(..., description="X coordinate in meters")
    y: float = Field(..., description="Y coordinate in meters")
    z: float = Field(..., description="Z coordinate in meters")

    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "x": 1.0,
                "y": 2.0,
                "z": 1.5
            }
        }


class Quaternion(BaseModel):
    """Quaternion orientation representation."""
    x: float = Field(..., description="X component")
    y: float = Field(..., description="Y component")
    z: float = Field(..., description="Z component")
    w: float = Field(..., description="W component")

    @validator('w', 'x', 'y', 'z')
    def validate_quaternion_components(cls, v):
        """Ensure quaternion components are finite."""
        if not (-1.0 <= v <= 1.0):
            logger.warning(f"Quaternion component {v} is outside typical range [-1, 1]")
        return v

    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "x": 0.0,
                "y": 0.0,
                "z": 0.0,
                "w": 1.0
            }
        }



class PlanRequest(BaseModel):
    """
    Planning request containing start/goal positions and planning parameters.
    
    Requirements: 1.3, 1.4, 1.5, 7.1, 7.4
    """
    start: Position = Field(..., description="Start position for planning")
    goal: Position = Field(..., description="Goal position for planning")
    max_velocity: float = Field(
        default=3.0,
        gt=0,
        le=10.0,
        description="Maximum velocity constraint (m/s)"
    )
    max_acceleration: float = Field(
        default=2.0,
        gt=0,
        le=10.0,
        description="Maximum acceleration constraint (m/s^2)"
    )
    algorithm: Literal["kinodynamic", "topological"] = Field(
        default="kinodynamic",
        description="Planning algorithm to use"
    )
    use_current_odom: bool = Field(
        default=False,
        description="Use current odometry as start position (ignores start field)"
    )

    @validator('max_velocity')
    def validate_max_velocity(cls, v):
        """Validate velocity is positive and within reasonable bounds."""
        if v <= 0:
            raise ValueError("Maximum velocity must be positive")
        if v > 10.0:
            raise ValueError("Maximum velocity cannot exceed 10.0 m/s")
        return v

    @validator('max_acceleration')
    def validate_max_acceleration(cls, v):
        """Validate acceleration is positive and within reasonable bounds."""
        if v <= 0:
            raise ValueError("Maximum acceleration must be positive")
        if v > 10.0:
            raise ValueError("Maximum acceleration cannot exceed 10.0 m/s^2")
        return v

    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "start": {"x": 0.0, "y": 0.0, "z": 1.0},
                "goal": {"x": 10.0, "y": 5.0, "z": 1.5},
                "max_velocity": 3.0,
                "max_acceleration": 2.0,
                "algorithm": "kinodynamic",
                "use_current_odom": False
            }
        }



class Waypoint(BaseModel):
    """
    Single waypoint in a trajectory with position, velocity, and acceleration.
    
    Requirements: 2.1
    """
    timestamp: float = Field(..., ge=0, description="Time from trajectory start (seconds)")
    position: Position = Field(..., description="Position at this waypoint")
    velocity: Position = Field(..., description="Velocity at this waypoint (m/s)")
    acceleration: Position = Field(..., description="Acceleration at this waypoint (m/s^2)")

    @validator('timestamp')
    def validate_timestamp(cls, v):
        """Ensure timestamp is non-negative."""
        if v < 0:
            raise ValueError("Timestamp must be non-negative")
        return v

    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "timestamp": 0.0,
                "position": {"x": 0.0, "y": 0.0, "z": 1.0},
                "velocity": {"x": 0.5, "y": 0.2, "z": 0.0},
                "acceleration": {"x": 0.1, "y": 0.05, "z": 0.0}
            }
        }


class Trajectory(BaseModel):
    """
    Complete trajectory with waypoints and metadata.
    
    Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
    """
    waypoints: List[Waypoint] = Field(..., min_items=1, description="List of trajectory waypoints")
    total_duration: float = Field(..., gt=0, description="Total trajectory duration (seconds)")
    num_waypoints: int = Field(..., gt=0, description="Number of waypoints in trajectory")

    @validator('waypoints')
    def validate_waypoints_timestamps(cls, v):
        """Ensure waypoints have monotonically increasing timestamps."""
        if len(v) < 1:
            raise ValueError("Trajectory must contain at least one waypoint")
        
        for i in range(1, len(v)):
            if v[i].timestamp <= v[i-1].timestamp:
                raise ValueError(
                    f"Waypoint timestamps must be monotonically increasing. "
                    f"Waypoint {i} timestamp {v[i].timestamp} <= previous {v[i-1].timestamp}"
                )
        return v

    @validator('num_waypoints')
    def validate_num_waypoints_matches(cls, v, values):
        """Ensure num_waypoints matches actual waypoint count."""
        if 'waypoints' in values and len(values['waypoints']) != v:
            raise ValueError(
                f"num_waypoints ({v}) does not match actual waypoint count ({len(values['waypoints'])})"
            )
        return v

    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "waypoints": [
                    {
                        "timestamp": 0.0,
                        "position": {"x": 0.0, "y": 0.0, "z": 1.0},
                        "velocity": {"x": 0.0, "y": 0.0, "z": 0.0},
                        "acceleration": {"x": 0.5, "y": 0.2, "z": 0.0}
                    }
                ],
                "total_duration": 5.2,
                "num_waypoints": 52
            }
        }



class ErrorInfo(BaseModel):
    """
    Error information for failed requests.
    
    Requirements: 3.1, 3.2, 3.3, 3.4, 3.5
    """
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[str] = Field(None, description="Additional error context and details")

    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "code": "no_path_found",
                "message": "Fast-Planner could not find a collision-free path to the goal",
                "details": "Goal position may be unreachable or surrounded by obstacles"
            }
        }


class PlanResponse(BaseModel):
    """
    Response for planning requests.
    
    Requirements: 2.1, 2.2, 3.5, 8.1, 8.2, 8.3, 8.4
    """
    success: bool = Field(..., description="Whether planning succeeded")
    trajectory: Optional[Trajectory] = Field(None, description="Planned trajectory (if successful)")
    error: Optional[ErrorInfo] = Field(None, description="Error information (if failed)")
    planning_time_ms: float = Field(..., ge=0, description="Total planning computation time (milliseconds)")
    ros_planning_time_ms: Optional[float] = Field(
        None,
        ge=0,
        description="Time Fast-Planner took to compute trajectory (milliseconds)"
    )
    total_time_ms: float = Field(..., ge=0, description="End-to-end request processing time (milliseconds)")

    @root_validator(skip_on_failure=True)
    def validate_success_fields(cls, values):
        """Ensure trajectory is present on success and error is present on failure."""
        success = values.get('success')
        trajectory = values.get('trajectory')
        error = values.get('error')

        if success and trajectory is None:
            raise ValueError("Successful response must include trajectory")
        
        if not success and error is None:
            raise ValueError("Failed response must include error information")

        return values

    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "success": True,
                "trajectory": {
                    "waypoints": [
                        {
                            "timestamp": 0.0,
                            "position": {"x": 0.0, "y": 0.0, "z": 1.0},
                            "velocity": {"x": 0.0, "y": 0.0, "z": 0.0},
                            "acceleration": {"x": 0.5, "y": 0.2, "z": 0.0}
                        }
                    ],
                    "total_duration": 5.2,
                    "num_waypoints": 52
                },
                "error": None,
                "planning_time_ms": 45.3,
                "ros_planning_time_ms": 38.1,
                "total_time_ms": 52.7
            }
        }



class OdometryResponse(BaseModel):
    """
    Current quadrotor odometry state.
    
    Requirements: 5.2
    """
    timestamp: float = Field(..., description="Timestamp of odometry measurement (seconds since epoch)")
    position: Position = Field(..., description="Current position")
    orientation: Quaternion = Field(..., description="Current orientation (quaternion)")
    linear_velocity: Position = Field(..., description="Current linear velocity (m/s)")
    angular_velocity: Position = Field(..., description="Current angular velocity (rad/s)")

    @validator('timestamp')
    def validate_timestamp(cls, v):
        """Ensure timestamp is positive."""
        if v <= 0:
            raise ValueError("Timestamp must be positive")
        return v

    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "timestamp": 1234567890.123,
                "position": {"x": 1.2, "y": 0.5, "z": 1.0},
                "orientation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0},
                "linear_velocity": {"x": 0.5, "y": 0.0, "z": 0.0},
                "angular_velocity": {"x": 0.0, "y": 0.0, "z": 0.1}
            }
        }


class HealthResponse(BaseModel):
    """
    Service health status information.
    
    Requirements: 6.2, 6.3, 6.4, 6.5
    """
    status: Literal["healthy", "degraded", "unhealthy"] = Field(
        ...,
        description="Overall service health status"
    )
    ros_connected: bool = Field(..., description="Whether ROS connection is active")
    fast_planner_available: bool = Field(..., description="Whether Fast-Planner node is responding")
    uptime_seconds: float = Field(..., ge=0, description="Service uptime in seconds")
    last_planning_success: Optional[float] = Field(
        None,
        description="Timestamp of last successful planning (seconds since epoch)"
    )
    odometry_age_ms: Optional[float] = Field(
        None,
        ge=0,
        description="Age of most recent odometry message (milliseconds)"
    )

    @validator('uptime_seconds')
    def validate_uptime(cls, v):
        """Ensure uptime is non-negative."""
        if v < 0:
            raise ValueError("Uptime must be non-negative")
        return v

    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "status": "healthy",
                "ros_connected": True,
                "fast_planner_available": True,
                "uptime_seconds": 3600.5,
                "last_planning_success": 1234567890.123,
                "odometry_age_ms": 50.2
            }
        }
