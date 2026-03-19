"""
Data models for FastAPI-Fast-Planner Interface.

This module defines Pydantic models for request/response validation,
including position data, planning requests, trajectories, error responses,
and depth image processing.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, validator, root_validator
import logging
import base64


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



class CameraIntrinsics(BaseModel):
    """
    Camera intrinsic parameters for depth image processing.
    
    Requirements: 9.3, 11.1
    """
    fx: float = Field(..., gt=0, description="Focal length in x direction (pixels)")
    fy: float = Field(..., gt=0, description="Focal length in y direction (pixels)")
    cx: float = Field(..., ge=0, description="Principal point x coordinate (pixels)")
    cy: float = Field(..., ge=0, description="Principal point y coordinate (pixels)")
    width: int = Field(..., gt=0, le=10000, description="Image width (pixels)")
    height: int = Field(..., gt=0, le=10000, description="Image height (pixels)")

    @validator('fx', 'fy')
    def validate_focal_length(cls, v):
        """Validate focal length is positive and within reasonable range."""
        if v <= 0:
            raise ValueError("Focal length must be positive")
        if v > 10000:
            raise ValueError("Focal length exceeds reasonable range (max 10000 pixels)")
        return v

    @root_validator(skip_on_failure=True)
    def validate_principal_points(cls, values):
        """Validate principal points are within image dimensions."""
        cx = values.get('cx')
        cy = values.get('cy')
        width = values.get('width')
        height = values.get('height')
        
        if cx is not None and width is not None and cx >= width:
            raise ValueError(f"Principal point cx ({cx}) must be less than image width ({width})")
        
        if cy is not None and height is not None and cy >= height:
            raise ValueError(f"Principal point cy ({cy}) must be less than image height ({height})")
        
        return values

    @validator('width', 'height')
    def validate_dimensions(cls, v):
        """Validate image dimensions are reasonable."""
        if v <= 0:
            raise ValueError("Image dimensions must be positive")
        if v > 10000:
            raise ValueError("Image dimensions exceed reasonable range (max 10000 pixels)")
        return v

    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "fx": 525.0,
                "fy": 525.0,
                "cx": 319.5,
                "cy": 239.5,
                "width": 640,
                "height": 480
            }
        }


class CameraPose(BaseModel):
    """
    Camera pose in the map frame.
    
    Requirements: 9.4
    """
    position: Position = Field(..., description="Camera position in map frame")
    orientation: Quaternion = Field(..., description="Camera orientation as quaternion")

    @validator('orientation')
    def validate_quaternion_normalized(cls, v):
        """Warn if quaternion is not normalized."""
        magnitude = (v.x**2 + v.y**2 + v.z**2 + v.w**2) ** 0.5
        if abs(magnitude - 1.0) > 0.01:
            logger.warning(
                f"Quaternion magnitude {magnitude:.4f} is not normalized (expected 1.0). "
                "This may cause transformation errors."
            )
        return v

    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "position": {"x": 1.0, "y": 0.5, "z": 1.0},
                "orientation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0}
            }
        }


class DepthImageRequest(BaseModel):
    """
    Request to process a depth image and update the occupancy map.
    
    Requirements: 9.1, 9.2, 9.3, 9.4, 11.1, 11.2, 11.3, 11.4, 11.5
    """
    depth_image: str = Field(..., description="Base64 encoded depth image data")
    camera_intrinsics: CameraIntrinsics = Field(..., description="Camera intrinsic parameters")
    camera_pose: CameraPose = Field(..., description="Camera pose in map frame")
    depth_scale: float = Field(
        default=0.001,
        gt=0,
        le=1.0,
        description="Scale factor to convert depth values to meters"
    )
    timestamp: float = Field(..., gt=0, description="Timestamp of depth image capture (seconds since epoch)")
    frame_id: str = Field(
        default="camera_depth_optical_frame",
        min_length=1,
        max_length=100,
        description="Frame ID for the depth image"
    )
    encoding: Literal["16UC1", "32FC1"] = Field(
        default="16UC1",
        description="Depth image encoding format (16-bit unsigned int or 32-bit float)"
    )

    @validator('depth_image')
    def validate_base64(cls, v):
        """Validate base64 encoding of depth image."""
        if not v or len(v) == 0:
            raise ValueError("Depth image data cannot be empty")
        
        try:
            decoded = base64.b64decode(v, validate=True)
            if len(decoded) == 0:
                raise ValueError("Decoded depth image data is empty")
        except Exception as e:
            raise ValueError(f"Invalid base64 encoded image data: {str(e)}")
        
        return v

    @validator('depth_scale')
    def validate_depth_scale(cls, v):
        """Validate depth scale is positive and reasonable."""
        if v <= 0:
            raise ValueError("Depth scale must be positive")
        if v > 1.0:
            raise ValueError("Depth scale exceeds reasonable range (max 1.0)")
        return v

    @validator('timestamp')
    def validate_timestamp(cls, v):
        """Validate timestamp is positive."""
        if v <= 0:
            raise ValueError("Timestamp must be positive")
        return v

    @validator('frame_id')
    def validate_frame_id(cls, v):
        """Validate frame_id is not empty."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Frame ID cannot be empty")
        return v.strip()

    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "depth_image": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
                "camera_intrinsics": {
                    "fx": 525.0,
                    "fy": 525.0,
                    "cx": 319.5,
                    "cy": 239.5,
                    "width": 640,
                    "height": 480
                },
                "camera_pose": {
                    "position": {"x": 1.0, "y": 0.5, "z": 1.0},
                    "orientation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0}
                },
                "depth_scale": 0.001,
                "timestamp": 1234567890.123,
                "frame_id": "camera_depth_optical_frame",
                "encoding": "16UC1"
            }
        }


class DepthImageBatchRequest(BaseModel):
    """
    Request to process multiple depth images in batch.
    
    Requirements: 14.1, 14.2, 14.5
    """
    depth_images: List[DepthImageRequest] = Field(
        ...,
        min_items=1,
        max_items=10,
        description="List of depth images to process (max 10)"
    )

    @validator('depth_images')
    def validate_batch_size(cls, v):
        """Validate batch size is within limits."""
        if len(v) == 0:
            raise ValueError("Batch must contain at least one depth image")
        if len(v) > 10:
            raise ValueError("Batch size cannot exceed 10 images")
        return v

    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "depth_images": [
                    {
                        "depth_image": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
                        "camera_intrinsics": {
                            "fx": 525.0,
                            "fy": 525.0,
                            "cx": 319.5,
                            "cy": 239.5,
                            "width": 640,
                            "height": 480
                        },
                        "camera_pose": {
                            "position": {"x": 1.0, "y": 0.5, "z": 1.0},
                            "orientation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0}
                        },
                        "depth_scale": 0.001,
                        "timestamp": 1234567890.123,
                        "frame_id": "camera_depth_optical_frame",
                        "encoding": "16UC1"
                    }
                ]
            }
        }


class DepthProcessingResult(BaseModel):
    """
    Result of processing a single depth image.
    
    Requirements: 12.1, 12.2, 12.3
    """
    success: bool = Field(..., description="Whether depth processing succeeded")
    points_generated: int = Field(..., ge=0, description="Number of valid 3D points generated")
    processing_time_ms: float = Field(..., ge=0, description="Processing time in milliseconds")
    timestamp: float = Field(..., gt=0, description="Timestamp of the processed depth image")
    message: str = Field(..., description="Processing status message")
    error: Optional[ErrorInfo] = Field(None, description="Error information if processing failed")

    @validator('points_generated')
    def validate_points_generated(cls, v):
        """Validate points generated is non-negative."""
        if v < 0:
            raise ValueError("Points generated must be non-negative")
        return v

    @validator('processing_time_ms')
    def validate_processing_time(cls, v):
        """Validate processing time is non-negative."""
        if v < 0:
            raise ValueError("Processing time must be non-negative")
        return v

    @root_validator(skip_on_failure=True)
    def validate_success_fields(cls, values):
        """Ensure error is present on failure."""
        success = values.get('success')
        error = values.get('error')

        if not success and error is None:
            raise ValueError("Failed processing result must include error information")

        return values

    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "success": True,
                "points_generated": 15234,
                "processing_time_ms": 125.3,
                "timestamp": 1234567890.123,
                "message": "Depth image processed and point cloud published successfully",
                "error": None
            }
        }


class DepthBatchResult(BaseModel):
    """
    Result of processing a single depth image in a batch.
    
    Requirements: 14.3, 14.4
    """
    index: int = Field(..., ge=0, description="Index of the depth image in the batch")
    success: bool = Field(..., description="Whether processing succeeded for this image")
    points_generated: Optional[int] = Field(None, ge=0, description="Number of valid points generated")
    processing_time_ms: Optional[float] = Field(None, ge=0, description="Processing time in milliseconds")
    error: Optional[ErrorInfo] = Field(None, description="Error information if processing failed")

    @validator('index')
    def validate_index(cls, v):
        """Validate index is non-negative."""
        if v < 0:
            raise ValueError("Index must be non-negative")
        return v

    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "index": 0,
                "success": True,
                "points_generated": 15234,
                "processing_time_ms": 125.3,
                "error": None
            }
        }


class DepthBatchResponse(BaseModel):
    """
    Response for batch depth image processing.
    
    Requirements: 14.1, 14.2, 14.3, 14.4, 14.5
    """
    success: bool = Field(..., description="Whether all images were processed successfully")
    total_images: int = Field(..., gt=0, description="Total number of images in batch")
    successful: int = Field(..., ge=0, description="Number of successfully processed images")
    failed: int = Field(..., ge=0, description="Number of failed images")
    results: List[DepthBatchResult] = Field(..., description="Individual results for each image")
    total_processing_time_ms: float = Field(..., ge=0, description="Total processing time for all images")

    @validator('total_images')
    def validate_total_images(cls, v):
        """Validate total images is positive."""
        if v <= 0:
            raise ValueError("Total images must be positive")
        return v

    @root_validator(skip_on_failure=True)
    def validate_counts(cls, values):
        """Validate that successful + failed = total_images and results match."""
        total = values.get('total_images')
        successful = values.get('successful')
        failed = values.get('failed')
        results = values.get('results')

        if total is not None and successful is not None and failed is not None:
            if successful + failed != total:
                raise ValueError(
                    f"Successful ({successful}) + Failed ({failed}) must equal total images ({total})"
                )

        if results is not None and total is not None:
            if len(results) != total:
                raise ValueError(
                    f"Number of results ({len(results)}) must match total images ({total})"
                )

        return values

    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "success": True,
                "total_images": 2,
                "successful": 2,
                "failed": 0,
                "results": [
                    {
                        "index": 0,
                        "success": True,
                        "points_generated": 15234,
                        "processing_time_ms": 125.3,
                        "error": None
                    },
                    {
                        "index": 1,
                        "success": True,
                        "points_generated": 14892,
                        "processing_time_ms": 118.7,
                        "error": None
                    }
                ],
                "total_processing_time_ms": 244.0
            }
        }
