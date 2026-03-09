# Design Document

## Overview

The FastAPI-Fast-Planner Interface is a REST API service that bridges HTTP clients with the ROS-based Fast-Planner trajectory planning system. The service translates HTTP requests into ROS messages, invokes Fast-Planner for trajectory computation, and returns results as JSON responses. This design enables integration of Fast-Planner into web applications, mobile apps, and other non-ROS systems.

The architecture follows a layered approach:
- **API Layer**: FastAPI endpoints handling HTTP requests/responses
- **ROS Bridge Layer**: Translates between HTTP and ROS message formats
- **Planning Client Layer**: Manages communication with Fast-Planner ROS nodes
- **Configuration Layer**: Manages service settings and ROS parameters

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                    HTTP Clients                          │
│            (Web Apps, Mobile, Scripts)                   │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/JSON (Planning + Depth Images)
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Service                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │           API Endpoints Layer                     │  │
│  │  /plan  /odometry  /health  /map/depth           │  │
│  └──────────────┬───────────────┬───────────────────┘  │
│                 │               │                        │
│  ┌──────────────▼──────────┐   │                        │
│  │  Request Validation     │   │                        │
│  │  (Pydantic Models)      │   │                        │
│  └──────────────┬──────────┘   │                        │
│                 │               │                        │
│  ┌──────────────▼──────────┐  ┌▼────────────────────┐  │
│  │   Planning Client       │  │  Depth Processor    │  │
│  │   (Trajectory)          │  │  (Image→PointCloud) │  │
│  └──────────────┬──────────┘  └─┬───────────────────┘  │
│                 │                │                       │
│  ┌──────────────▼────────────────▼───────────────────┐ │
│  │           ROS Bridge Layer                         │ │
│  │  (Message Conversion, Topic Management)           │ │
│  └──────────────────┬─────────────────────────────────┘ │
└────────────────────┬┴───────────────────────────────────┘
                     │ ROS Topics
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  ROS Environment                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Fast-Planner Node                         │  │
│  │  (Kinodynamic/Topological Planning)              │  │
│  │  ← Subscribes to /depth_cloud                    │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Odometry Publisher                        │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Depth Processing Flow

```
Depth Image (Base64) → Decode → Depth Array (HxW)
                                      ↓
                          Camera Intrinsics (fx, fy, cx, cy)
                                      ↓
                          3D Points (Camera Frame)
                                      ↓
                          Camera Pose (Position + Orientation)
                                      ↓
                          3D Points (Map Frame)
                                      ↓
                          Filter (Depth Range, Map Bounds)
                                      ↓
                          Downsample (Voxel Grid)
                                      ↓
                          PointCloud2 Message → ROS Topic
                                      ↓
                          Fast-Planner (Map Update)
```

### Technology Stack

- **FastAPI**: Modern Python web framework for building APIs
- **rospy**: Python ROS client library for ROS communication
- **Pydantic**: Data validation using Python type annotations
- **uvicorn**: ASGI server for running FastAPI application
- **asyncio**: Asynchronous I/O for non-blocking ROS communication

## Components and Interfaces

### 1. API Endpoints

#### POST /plan
Accepts planning request and returns trajectory.

**Request Body:**
```json
{
  "start": {
    "x": 0.0,
    "y": 0.0,
    "z": 1.0
  },
  "goal": {
    "x": 10.0,
    "y": 5.0,
    "z": 1.5
  },
  "max_velocity": 3.0,
  "max_acceleration": 2.0,
  "algorithm": "kinodynamic",
  "use_current_odom": false
}
```

**Response (Success - 200):**
```json
{
  "success": true,
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
  "planning_time_ms": 45.3,
  "ros_planning_time_ms": 38.1,
  "total_time_ms": 52.7
}
```

**Response (Failure - 422):**
```json
{
  "success": false,
  "error": {
    "code": "no_path_found",
    "message": "Fast-Planner could not find a collision-free path to the goal",
    "details": "Goal position may be unreachable or surrounded by obstacles"
  }
}
```

#### GET /odometry
Returns current quadrotor state.

**Response (Success - 200):**
```json
{
  "timestamp": 1234567890.123,
  "position": {"x": 1.2, "y": 0.5, "z": 1.0},
  "orientation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0},
  "linear_velocity": {"x": 0.5, "y": 0.0, "z": 0.0},
  "angular_velocity": {"x": 0.0, "y": 0.0, "z": 0.1}
}
```

#### GET /health
Returns service health status.

**Response (200):**
```json
{
  "status": "healthy",
  "ros_connected": true,
  "fast_planner_available": true,
  "uptime_seconds": 3600,
  "last_planning_success": 1234567890.123,
  "odometry_age_ms": 50
}
```

#### POST /map/depth
Processes depth image to update occupancy map.

**Request Body (multipart/form-data or JSON):**
```json
{
  "depth_image": "base64_encoded_image_data",
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
```

**Response (Success - 200):**
```json
{
  "success": true,
  "points_generated": 15234,
  "processing_time_ms": 125.3,
  "timestamp": 1234567890.123,
  "message": "Depth image processed and point cloud published successfully"
}
```

**Response (Failure - 400):**
```json
{
  "success": false,
  "error": {
    "code": "invalid_depth_image",
    "message": "Depth image dimensions do not match camera parameters",
    "details": "Expected 640x480, got 320x240"
  }
}
```

#### POST /map/depth/batch
Processes multiple depth images in batch.

**Request Body:**
```json
{
  "depth_images": [
    {
      "depth_image": "base64_encoded_image_data_1",
      "camera_intrinsics": {...},
      "camera_pose": {...},
      "depth_scale": 0.001,
      "timestamp": 1234567890.123
    },
    {
      "depth_image": "base64_encoded_image_data_2",
      "camera_intrinsics": {...},
      "camera_pose": {...},
      "depth_scale": 0.001,
      "timestamp": 1234567890.223
    }
  ]
}
```

**Response (200):**
```json
{
  "success": true,
  "total_images": 2,
  "successful": 2,
  "failed": 0,
  "results": [
    {
      "index": 0,
      "success": true,
      "points_generated": 15234,
      "processing_time_ms": 125.3
    },
    {
      "index": 1,
      "success": true,
      "points_generated": 14892,
      "processing_time_ms": 118.7
    }
  ],
  "total_processing_time_ms": 244.0
}
```

### 2. ROS Bridge Component

**Class: ROSBridge**

Responsibilities:
- Initialize ROS node and manage ROS lifecycle
- Subscribe to odometry topic
- Publish goal waypoints to Fast-Planner
- Subscribe to trajectory results from Fast-Planner
- Publish point clouds for map updates
- Handle ROS message conversions

**Key Methods:**
```python
class ROSBridge:
    def __init__(self, config: ROSConfig)
    def connect(self) -> bool
    def publish_goal(self, start: Position, goal: Position, params: PlanningParams) -> None
    def wait_for_trajectory(self, timeout: float) -> Optional[Trajectory]
    def get_latest_odometry(self) -> Optional[Odometry]
    def check_planner_status(self) -> bool
    def publish_point_cloud(self, points: np.ndarray, frame_id: str, timestamp: float) -> bool
    def shutdown(self) -> None
```

**ROS Topics:**
- Subscribe: `/state_ukf/odom` (nav_msgs/Odometry) - Quadrotor odometry
- Subscribe: `/planning/bspline` (plan_manage/Bspline) - Planned trajectory
- Publish: `/move_base_simple/goal` (geometry_msgs/PoseStamped) - Goal position
- Publish: `/planning/goal` (geometry_msgs/PoseStamped) - Alternative goal topic
- Publish: `/depth_cloud` (sensor_msgs/PointCloud2) - Point cloud from depth images

### 3. Planning Client Component

**Class: PlanningClient**

Responsibilities:
- Coordinate planning requests with ROS Bridge
- Implement timeout and retry logic
- Convert B-spline trajectory to waypoint trajectory
- Cache planning results

**Key Methods:**
```python
class PlanningClient:
    def __init__(self, ros_bridge: ROSBridge, config: PlanningConfig)
    async def plan_trajectory(self, request: PlanRequest) -> PlanResponse
    def _convert_bspline_to_waypoints(self, bspline: BsplineMsg) -> List[Waypoint]
    def _validate_trajectory(self, trajectory: Trajectory) -> bool
```

### 4. Depth Processing Component

**Class: DepthProcessor**

Responsibilities:
- Decode and validate depth images
- Convert depth images to 3D point clouds
- Transform points from camera frame to map frame
- Filter invalid depth values
- Apply downsampling for performance optimization

**Key Methods:**
```python
class DepthProcessor:
    def __init__(self, config: DepthConfig)
    def decode_depth_image(self, image_data: bytes, encoding: str) -> np.ndarray
    def depth_to_pointcloud(
        self, 
        depth_image: np.ndarray,
        intrinsics: CameraIntrinsics,
        depth_scale: float
    ) -> np.ndarray
    def transform_pointcloud(
        self,
        points: np.ndarray,
        camera_pose: Pose
    ) -> np.ndarray
    def filter_depth_range(
        self,
        points: np.ndarray,
        min_depth: float,
        max_depth: float
    ) -> np.ndarray
    def downsample_pointcloud(
        self,
        points: np.ndarray,
        voxel_size: float
    ) -> np.ndarray
    async def process_depth_image(
        self,
        request: DepthImageRequest
    ) -> DepthProcessingResult
```

**Algorithm: Depth to Point Cloud Conversion**

1. For each pixel (u, v) in depth image:
   - Read depth value d
   - Skip if d is invalid (0, negative, or out of range)
   - Convert to 3D point in camera frame:
     ```
     X_cam = (u - cx) * d / fx
     Y_cam = (v - cy) * d / fy
     Z_cam = d
     ```

2. Transform points from camera frame to map frame:
   - Apply rotation: `P_map_rot = R_cam_to_map * P_cam`
   - Apply translation: `P_map = P_map_rot + T_cam_to_map`

3. Filter points:
   - Remove points outside depth range [min_depth, max_depth]
   - Remove points outside map boundaries

4. Downsample (optional):
   - Apply voxel grid filter with configurable voxel size
   - Reduces point density for performance

**Dependencies:**
- `numpy`: Array operations and transformations
- `opencv-python` (cv2): Image decoding and processing
- `scipy`: Spatial transformations
- `open3d` (optional): Advanced point cloud processing

### 5. Configuration Component

**Class: ServiceConfig**

Configuration loaded from YAML file or environment variables:

```yaml
ros:
  master_uri: "http://localhost:11311"
  node_name: "fastapi_planner_bridge"
  topics:
    odometry: "/state_ukf/odom"
    goal: "/move_base_simple/goal"
    trajectory: "/planning/bspline"
    point_cloud: "/depth_cloud"
  
planning:
  default_max_velocity: 3.0
  default_max_acceleration: 2.0
  planning_timeout: 5.0
  trajectory_sample_rate: 10.0
  
map:
  size_x: 40.0
  size_y: 20.0
  size_z: 5.0
  origin_x: -20.0
  origin_y: -10.0
  origin_z: 0.0

depth:
  min_depth: 0.1
  max_depth: 10.0
  voxel_size: 0.05
  max_batch_size: 10
  default_encoding: "16UC1"
  
service:
  host: "0.0.0.0"
  port: 8000
  log_level: "info"
```

## Data Models

### Request Models (Pydantic)

```python
class Position(BaseModel):
    x: float
    y: float
    z: float

class Quaternion(BaseModel):
    x: float
    y: float
    z: float
    w: float

class PlanRequest(BaseModel):
    start: Position
    goal: Position
    max_velocity: float = Field(gt=0, le=10.0, default=3.0)
    max_acceleration: float = Field(gt=0, le=10.0, default=2.0)
    algorithm: Literal["kinodynamic", "topological"] = "kinodynamic"
    use_current_odom: bool = False
    
    @validator('start', 'goal')
    def validate_position_bounds(cls, v, values, config):
        # Validate against map boundaries
        pass

class Waypoint(BaseModel):
    timestamp: float
    position: Position
    velocity: Position
    acceleration: Position

class Trajectory(BaseModel):
    waypoints: List[Waypoint]
    total_duration: float
    num_waypoints: int

class PlanResponse(BaseModel):
    success: bool
    trajectory: Optional[Trajectory]
    error: Optional[ErrorInfo]
    planning_time_ms: float
    ros_planning_time_ms: Optional[float]
    total_time_ms: float

class CameraIntrinsics(BaseModel):
    fx: float = Field(gt=0, description="Focal length in x direction (pixels)")
    fy: float = Field(gt=0, description="Focal length in y direction (pixels)")
    cx: float = Field(ge=0, description="Principal point x coordinate (pixels)")
    cy: float = Field(ge=0, description="Principal point y coordinate (pixels)")
    width: int = Field(gt=0, description="Image width (pixels)")
    height: int = Field(gt=0, description="Image height (pixels)")

class CameraPose(BaseModel):
    position: Position
    orientation: Quaternion

class DepthImageRequest(BaseModel):
    depth_image: str = Field(..., description="Base64 encoded depth image data")
    camera_intrinsics: CameraIntrinsics
    camera_pose: CameraPose
    depth_scale: float = Field(gt=0, default=0.001, description="Scale factor to convert depth values to meters")
    timestamp: float = Field(..., description="Timestamp of depth image capture")
    frame_id: str = Field(default="camera_depth_optical_frame", description="Frame ID for the depth image")
    encoding: Literal["16UC1", "32FC1"] = Field(default="16UC1", description="Depth image encoding format")
    
    @validator('depth_image')
    def validate_base64(cls, v):
        # Validate base64 encoding
        import base64
        try:
            base64.b64decode(v)
        except Exception:
            raise ValueError("Invalid base64 encoded image data")
        return v

class DepthImageBatchRequest(BaseModel):
    depth_images: List[DepthImageRequest] = Field(..., max_items=10)
    
    @validator('depth_images')
    def validate_batch_size(cls, v):
        if len(v) == 0:
            raise ValueError("Batch must contain at least one depth image")
        if len(v) > 10:
            raise ValueError("Batch size cannot exceed 10 images")
        return v

class DepthProcessingResult(BaseModel):
    success: bool
    points_generated: int = Field(ge=0)
    processing_time_ms: float = Field(ge=0)
    timestamp: float
    message: str
    error: Optional[ErrorInfo] = None

class DepthBatchResult(BaseModel):
    index: int
    success: bool
    points_generated: Optional[int] = None
    processing_time_ms: Optional[float] = None
    error: Optional[ErrorInfo] = None

class DepthBatchResponse(BaseModel):
    success: bool
    total_images: int
    successful: int
    failed: int
    results: List[DepthBatchResult]
    total_processing_time_ms: float
```

### ROS Message Mapping

**Odometry Mapping:**
- ROS: `nav_msgs/Odometry`
- API: `OdometryResponse` (Pydantic model)

**Goal Mapping:**
- API: `PlanRequest.goal`
- ROS: `geometry_msgs/PoseStamped`

**Trajectory Mapping:**
- ROS: `plan_manage/Bspline` (B-spline control points)
- API: `Trajectory` (sampled waypoints)

The B-spline trajectory needs to be evaluated at regular intervals (10 Hz) to generate discrete waypoints with position, velocity, and acceleration.

**Point Cloud Mapping:**
- API: `DepthImageRequest` (depth image + camera parameters)
- Processing: Convert to 3D points using camera intrinsics and pose
- ROS: `sensor_msgs/PointCloud2` (XYZ point cloud)

Point cloud message structure:
```python
# sensor_msgs/PointCloud2
header:
  stamp: timestamp from depth image
  frame_id: "map" (after transformation)
height: 1 (unorganized point cloud)
width: number of valid points
fields: [x, y, z] (float32 each)
is_bigendian: False
point_step: 12 (3 floats * 4 bytes)
row_step: width * point_step
data: binary point data
is_dense: True (no invalid points)
```

## Error Handling

### Error Categories

1. **Validation Errors (400)**
   - Invalid JSON format
   - Missing required fields
   - Out-of-bounds parameters
   - Invalid algorithm selection
   - Invalid depth image format
   - Depth image dimensions mismatch
   - Invalid camera parameters
   - Invalid base64 encoding

2. **Planning Errors (422)**
   - No path found
   - Start/goal in collision
   - Trajectory optimization failed

3. **Service Errors (503)**
   - ROS connection lost
   - Odometry unavailable
   - Fast-Planner node not responding
   - Point cloud publishing failed

4. **Timeout Errors (504)**
   - Planning timeout exceeded
   - ROS communication timeout

### Error Response Format

```python
class ErrorInfo(BaseModel):
    code: str  # Machine-readable error code
    message: str  # Human-readable message
    details: Optional[str]  # Additional context
```

### Exception Handling Strategy

- FastAPI exception handlers for each error category
- Graceful degradation when ROS connection is lost
- Automatic reconnection attempts for transient failures
- Comprehensive logging for debugging

## Testing Strategy

### Unit Tests

1. **API Endpoint Tests**
   - Test request validation with valid/invalid inputs
   - Test response serialization
   - Test error handling for each endpoint
   - Test depth image endpoint with various image formats
   - Test batch processing endpoint

2. **ROS Bridge Tests**
   - Mock ROS publishers/subscribers
   - Test message conversion functions
   - Test timeout handling
   - Test point cloud publishing

3. **Planning Client Tests**
   - Mock ROS Bridge responses
   - Test B-spline to waypoint conversion
   - Test trajectory validation

4. **Depth Processing Tests**
   - Test depth image decoding (16UC1, 32FC1)
   - Test depth to point cloud conversion with known camera parameters
   - Test coordinate transformation from camera to map frame
   - Test depth range filtering
   - Test point cloud downsampling
   - Test invalid depth value handling (zeros, negatives, out of range)

### Integration Tests

1. **End-to-End Planning Test**
   - Start mock ROS environment
   - Send planning request via HTTP
   - Verify trajectory response format
   - Verify ROS messages published correctly

2. **End-to-End Depth Processing Test**
   - Send depth image via HTTP
   - Verify point cloud generation
   - Verify ROS PointCloud2 message published
   - Test with real depth image samples

3. **Error Scenario Tests**
   - Test behavior when ROS is unavailable
   - Test behavior when Fast-Planner fails
   - Test timeout scenarios
   - Test depth processing with invalid images

4. **Performance Tests**
   - Measure request latency
   - Test concurrent request handling
   - Verify memory usage under load
   - Measure depth processing performance with various image sizes
   - Test batch processing throughput

### Testing Tools

- **pytest**: Python testing framework
- **httpx**: Async HTTP client for API testing
- **rospy_mock**: Mock ROS environment for testing
- **pytest-asyncio**: Async test support

## Deployment Considerations

### Docker Container

Package service as Docker container with:
- Python 3.8+ runtime
- ROS Noetic/Melodic installation
- FastAPI application
- Configuration files
- OpenCV and NumPy for image processing
- Optional: Open3D for advanced point cloud processing

### Environment Variables

```bash
ROS_MASTER_URI=http://localhost:11311
ROS_IP=192.168.1.100
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
CONFIG_FILE=/app/config.yaml
LOG_LEVEL=info
```

### Monitoring

- Health check endpoint for container orchestration
- Prometheus metrics for planning success rate, latency
- Structured logging for debugging

### Security

- Optional API key authentication
- Rate limiting to prevent abuse
- Input validation to prevent injection attacks
- CORS configuration for web clients
