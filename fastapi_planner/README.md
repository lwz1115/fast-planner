# FastAPI-Fast-Planner Interface

A REST API service that provides HTTP access to the Fast-Planner ROS trajectory planning system.

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Setup](#setup)
- [Configuration](#configuration)
  - [config.yaml](#configyaml)
  - [Environment Variables](#environment-variables)
  - [Configuration Priority](#configuration-priority)
  - [Configuration Examples](#configuration-examples)
- [Docker Deployment](#docker-deployment)
- [Usage](#usage)
  - [Running the Service](#running-the-service)
  - [API Endpoints](#api-endpoints)
  - [Quick Start Examples](#quick-start-examples)
- [Depth Image Processing](#depth-image-processing)
  - [Overview](#depth-processing-overview)
  - [Camera Parameters](#camera-parameters)
  - [Supported Formats](#supported-depth-image-formats)
  - [Single Image Processing](#single-depth-image-processing)
  - [Batch Processing](#batch-depth-image-processing)
  - [Python Client Examples](#python-client-examples)
- [ROS Topic Requirements](#ros-topic-requirements)
  - [Required Topics](#required-topics)
  - [Algorithm-Specific Topics](#algorithm-specific-topics)
  - [Verifying Topics](#verifying-topics)
- [Fast-Planner Setup](#fast-planner-setup)
  - [Installation](#1-install-fast-planner)
  - [Configuration](#2-configure-fast-planner)
  - [Launching](#3-launch-fast-planner)
  - [Integration](#integration-with-fastapi-service)
- [API Documentation](#api-documentation)
- [Error Handling](#error-handling)
- [Logging and Monitoring](#logging-and-monitoring)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [Requirements](#requirements)

## Overview

## Project Structure

```
fastapi_planner/
├── __init__.py           # Package initialization
├── requirements.txt      # Python dependencies
├── config.yaml          # Service configuration
├── .env.example         # Environment variables template
└── README.md           # This file
```

## Installation

### Prerequisites

- ROS Noetic (or Melodic)
- Python 3.8+
- Fast-Planner ROS package installed and configured

### Setup

1. Install Python dependencies:
```bash
pip3 install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

3. Update configuration:
```bash
# Edit config.yaml to match your ROS setup
nano config.yaml
```

## Configuration

The service uses a combination of YAML configuration files and environment variables. Environment variables take precedence over YAML settings.

### config.yaml

The main configuration file (`config.yaml`) contains all service parameters organized into sections:

#### ROS Configuration (`ros`)

Controls ROS connection and topic routing:

```yaml
ros:
  master_uri: "http://localhost:11311"  # ROS Master URI
  node_name: "fastapi_planner_bridge"   # ROS node name for this service
  topics:
    odometry: "/state_ukf/odom"         # Odometry topic (nav_msgs/Odometry)
    goal: "/move_base_simple/goal"      # Default goal topic (geometry_msgs/PoseStamped)
    trajectory: "/planning/bspline"     # Trajectory result topic (plan_manage/Bspline)
    planning_goal: "/planning/goal"     # Alternative goal topic
    kinodynamic_goal: null              # Optional: Kinodynamic-specific goal topic
    topological_goal: null              # Optional: Topological-specific goal topic
```

**Parameters:**
- `master_uri`: ROS Master address (can be overridden by `ROS_MASTER_URI` env var)
- `node_name`: Name for the ROS node created by this service
- `topics.odometry`: Topic to subscribe for quadrotor odometry data
- `topics.goal`: Default topic to publish goal positions
- `topics.trajectory`: Topic to subscribe for planned B-spline trajectories
- `topics.kinodynamic_goal`: Optional algorithm-specific goal topic (uses `goal` if not set)
- `topics.topological_goal`: Optional algorithm-specific goal topic (uses `goal` if not set)

#### Planning Configuration (`planning`)

Controls planning behavior and limits:

```yaml
planning:
  default_max_velocity: 3.0           # Default max velocity (m/s)
  default_max_acceleration: 2.0       # Default max acceleration (m/s²)
  planning_timeout: 5.0               # Planning timeout (seconds)
  trajectory_sample_rate: 10.0        # Waypoint sampling rate (Hz)
  max_velocity_limit: 10.0            # Maximum allowed velocity (m/s)
  max_acceleration_limit: 10.0        # Maximum allowed acceleration (m/s²)
```

**Parameters:**
- `default_max_velocity`: Default velocity limit used when not specified in request
- `default_max_acceleration`: Default acceleration limit used when not specified in request
- `planning_timeout`: Maximum time to wait for Fast-Planner to compute trajectory
- `trajectory_sample_rate`: Frequency at which to sample B-spline trajectory (waypoints per second)
- `max_velocity_limit`: Hard limit for velocity validation (requests exceeding this are rejected)
- `max_acceleration_limit`: Hard limit for acceleration validation

#### Map Configuration (`map`)

Defines map boundaries for position validation:

```yaml
map:
  size_x: 40.0    # Map size in X direction (meters)
  size_y: 20.0    # Map size in Y direction (meters)
  size_z: 5.0     # Map size in Z direction (meters)
  origin_x: 0.0   # Map origin X coordinate
  origin_y: 0.0   # Map origin Y coordinate
  origin_z: 0.0   # Map origin Z coordinate
```

**Parameters:**
- `size_x`, `size_y`, `size_z`: Map dimensions in meters
- `origin_x`, `origin_y`, `origin_z`: Map origin coordinates (for coordinate transformation)

Position validation checks: `origin ≤ position ≤ origin + size`

#### Service Configuration (`service`)

Controls FastAPI service behavior:

```yaml
service:
  host: "0.0.0.0"              # Bind address
  port: 8000                   # Service port
  log_level: "info"            # Logging level (debug/info/warning/error/critical)
  enable_cors: true            # Enable CORS middleware
  cors_origins: ["*"]          # Allowed CORS origins
  docs_url: "/docs"            # Swagger UI documentation URL
  redoc_url: "/redoc"          # ReDoc documentation URL
  health_check:
    max_odometry_age: 1.0      # Max odometry age before considered stale (seconds)
    planner_check_interval: 5.0 # Interval to check Fast-Planner availability (seconds)
```

**Parameters:**
- `host`: Network interface to bind (0.0.0.0 = all interfaces)
- `port`: TCP port for HTTP service (can be overridden by `FASTAPI_PORT` env var)
- `log_level`: Logging verbosity (can be overridden by `LOG_LEVEL` env var)
- `enable_cors`: Enable Cross-Origin Resource Sharing for web clients
- `cors_origins`: List of allowed origins (use `["*"]` for all origins)
- `docs_url`: Path for Swagger UI documentation (set to `null` to disable)
- `redoc_url`: Path for ReDoc documentation (set to `null` to disable)
- `health_check.max_odometry_age`: Odometry older than this is considered stale
- `health_check.planner_check_interval`: How often to verify Fast-Planner is running

### Environment Variables

Environment variables override corresponding YAML settings. See `.env.example` for a template.

#### Required Environment Variables

None - all settings have defaults in `config.yaml`.

#### Optional Environment Variables

**ROS Configuration:**
- `ROS_MASTER_URI`: ROS Master address (overrides `ros.master_uri`)
  - Example: `http://192.168.1.100:11311`
- `ROS_IP`: IP address for ROS communication (used by ROS, not directly by service)
  - Example: `192.168.1.50`
- `ROS_HOSTNAME`: Hostname for ROS communication
  - Example: `robot-laptop`

**Service Configuration:**
- `FASTAPI_HOST`: Service bind address (overrides `service.host`)
  - Example: `0.0.0.0` (all interfaces) or `127.0.0.1` (localhost only)
- `FASTAPI_PORT`: Service port (overrides `service.port`)
  - Example: `8000`
- `LOG_LEVEL`: Logging level (overrides `service.log_level`)
  - Values: `debug`, `info`, `warning`, `error`, `critical`

**Configuration File:**
- `CONFIG_FILE`: Path to YAML configuration file
  - Default: `./config.yaml` (relative to fastapi_planner directory)
  - Example: `/etc/fastapi_planner/config.yaml`

### Configuration Priority

Settings are applied in the following order (later overrides earlier):

1. Default values in code
2. YAML configuration file (`config.yaml`)
3. Environment variables

### Configuration Validation

The service validates all configuration on startup:

- ROS Master URI format (must start with `http://` or `https://`)
- Port numbers (must be 1-65535)
- Positive values for timeouts, velocities, accelerations
- Map dimensions (must be positive)
- Log level (must be valid level name)

If validation fails, the service exits with an error message indicating the problem.

## Docker Deployment

The service is designed to run in a Docker container with ROS.

### Using Docker Compose (Recommended)

The easiest way to deploy is using Docker Compose:

```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f fastapi-planner

# Stop the service
docker-compose down
```

The `docker-compose.yml` file includes:
- Automatic service startup with ROS environment
- Volume mounts for development
- Health checks
- Network host mode for ROS communication
- Environment variable configuration

### Using Docker Directly

Build and run manually:

```bash
# Build the image
docker build -f Dockerfile.dev -t fastapi-planner .

# Run the container
docker run -it --network host \
  -e ROS_MASTER_URI=http://localhost:11311 \
  -e FASTAPI_PORT=8000 \
  -v $(pwd)/fastapi_planner:/root/catkin_ws/fastapi_planner \
  fastapi-planner

# Inside the container, start the service
source /opt/ros/noetic/setup.bash
source devel/setup.bash
python3 -m fastapi_planner.main
```

### Docker Configuration

The `Dockerfile.dev` includes:
- ROS Noetic base image (Ubuntu 20.04 + Python 3.8)
- All required dependencies (NLopt, Armadillo, etc.)
- FastAPI and Python dependencies
- Exposed ports: 8000 (FastAPI), 1919 (ROS)

**Note:** The container uses `network_mode: host` to communicate with ROS Master. Ensure ROS Master is running and accessible.

## Usage

### Running the Service

Start the FastAPI service:

```bash
# Make sure ROS is running first
roscore

# In another terminal, start the service
python3 -m fastapi_planner.main
```

Or use uvicorn directly:

```bash
uvicorn fastapi_planner.main:app --host 0.0.0.0 --port 8000
```

### API Endpoints

The service provides the following endpoints:

#### Planning Endpoints
- `POST /plan` - Request trajectory planning from start to goal
- `GET /odometry` - Get current quadrotor odometry state

#### Map Update Endpoints
- `POST /map/depth` - Process single depth image to update occupancy map
- `POST /map/depth/batch` - Process multiple depth images in batch

#### Monitoring Endpoints
- `GET /health` - Check service health and status
- `GET /metrics` - Get performance metrics and statistics
- `GET /` - Service information

#### Documentation Endpoints
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)

For detailed API documentation with request/response schemas and examples, see:
- **Interactive Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative Documentation**: http://localhost:8000/redoc (ReDoc)
- **API Reference**: See `API_REFERENCE.md` for detailed endpoint documentation

### Quick Start Examples

#### Plan a Trajectory

```bash
curl -X POST "http://localhost:8000/plan" \
  -H "Content-Type: application/json" \
  -d '{
    "start": {"x": 0.0, "y": 0.0, "z": 1.0},
    "goal": {"x": 10.0, "y": 5.0, "z": 1.5},
    "max_velocity": 3.0,
    "max_acceleration": 2.0,
    "algorithm": "kinodynamic"
  }'
```

**Response (Success):**
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
      },
      ...
    ],
    "total_duration": 5.2,
    "num_waypoints": 52
  },
  "error": null,
  "planning_time_ms": 45.3,
  "ros_planning_time_ms": 38.1,
  "total_time_ms": 52.7
}
```

#### Get Current Odometry

```bash
curl "http://localhost:8000/odometry"
```

**Response:**
```json
{
  "timestamp": 1699876543.123,
  "position": {"x": 1.2, "y": 0.5, "z": 1.0},
  "orientation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0},
  "linear_velocity": {"x": 0.5, "y": 0.0, "z": 0.0},
  "angular_velocity": {"x": 0.0, "y": 0.0, "z": 0.1}
}
```

#### Check Service Health

```bash
curl "http://localhost:8000/health"
```

**Response:**
```json
{
  "status": "healthy",
  "ros_connected": true,
  "fast_planner_available": true,
  "uptime_seconds": 3600.5,
  "last_planning_success": 1699876543.123,
  "odometry_age_ms": 50.2
}
```

#### Get Performance Metrics

```bash
curl "http://localhost:8000/metrics"
```

**Response:**
```json
{
  "uptime_seconds": 3600.5,
  "total_requests": 150,
  "successful_requests": 142,
  "failed_requests": 8,
  "success_rate_percent": 94.67,
  "last_planning_success": 1699876543.123,
  "ros_connected": true
}
```

#### Process Depth Image

```bash
curl -X POST "http://localhost:8000/map/depth" \
  -H "Content-Type: application/json" \
  -d '{
    "depth_image": "iVBORw0KGgoAAAANSUhEUgAAAAUA...",
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
    "timestamp": 1699876543.123,
    "frame_id": "camera_depth_optical_frame",
    "encoding": "16UC1"
  }'
```

**Response (Success):**
```json
{
  "success": true,
  "points_generated": 15234,
  "processing_time_ms": 125.3,
  "timestamp": 1699876543.123,
  "message": "Depth image processed and point cloud published successfully"
}
```

#### Process Batch Depth Images

```bash
curl -X POST "http://localhost:8000/map/depth/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "depth_images": [
      {
        "depth_image": "iVBORw0KGgoAAAANSUhEUgAAAAUA...",
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
        "timestamp": 1699876543.123
      }
    ]
  }'
```

**Response:**
```json
{
  "success": true,
  "total_images": 1,
  "successful": 1,
  "failed": 0,
  "results": [
    {
      "index": 0,
      "success": true,
      "points_generated": 15234,
      "processing_time_ms": 125.3
    }
  ],
  "total_processing_time_ms": 125.3
}
```

## Configuration Examples

### Example 1: Local Development

For local development with ROS running on the same machine:

**.env:**
```bash
ROS_MASTER_URI=http://localhost:11311
ROS_IP=127.0.0.1
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
LOG_LEVEL=debug
```

**config.yaml:** (use defaults)

### Example 2: Remote ROS Master

When ROS Master is running on a different machine:

**.env:**
```bash
ROS_MASTER_URI=http://192.168.1.100:11311
ROS_IP=192.168.1.50
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
```

**config.yaml:** (use defaults)

### Example 3: Custom Topics and Algorithms

When using custom topic names or algorithm-specific topics:

**config.yaml:**
```yaml
ros:
  master_uri: "http://localhost:11311"
  node_name: "fastapi_planner_bridge"
  topics:
    odometry: "/mavros/local_position/odom"
    goal: "/move_base_simple/goal"
    trajectory: "/planning/bspline"
    kinodynamic_goal: "/planning/kinodynamic/goal"
    topological_goal: "/planning/topological/goal"

planning:
  default_max_velocity: 2.5
  default_max_acceleration: 1.5
  planning_timeout: 10.0
```

### Example 4: Production Deployment

For production with stricter limits and monitoring:

**config.yaml:**
```yaml
planning:
  default_max_velocity: 2.0
  default_max_acceleration: 1.5
  planning_timeout: 8.0
  max_velocity_limit: 5.0
  max_acceleration_limit: 5.0

service:
  host: "0.0.0.0"
  port: 8000
  log_level: "warning"
  enable_cors: true
  cors_origins:
    - "https://myapp.example.com"
    - "https://dashboard.example.com"
  health_check:
    max_odometry_age: 0.5
    planner_check_interval: 3.0
```

**.env:**
```bash
ROS_MASTER_URI=http://robot-master:11311
LOG_LEVEL=warning
```

### Example 5: Large Environment

For larger maps and higher performance requirements:

**config.yaml:**
```yaml
map:
  size_x: 100.0
  size_y: 100.0
  size_z: 10.0
  origin_x: -50.0
  origin_y: -50.0
  origin_z: 0.0

planning:
  default_max_velocity: 5.0
  default_max_acceleration: 3.0
  planning_timeout: 15.0
  trajectory_sample_rate: 20.0
  max_velocity_limit: 15.0
  max_acceleration_limit: 10.0
```

## Depth Image Processing

The service provides endpoints for processing depth images to update the occupancy map used by Fast-Planner. Depth images are converted to 3D point clouds and published to ROS for map updates.

### Depth Processing Overview

The depth processing pipeline:

1. **Receive depth image** - Base64-encoded depth image with camera parameters
2. **Decode and validate** - Decode image data and validate dimensions/format
3. **Generate point cloud** - Convert depth pixels to 3D points using camera intrinsics
4. **Transform to world frame** - Apply camera pose transformation
5. **Publish to ROS** - Send point cloud to Fast-Planner's map update topic
6. **Return result** - Provide processing statistics and success status

### Camera Parameters

Camera intrinsic parameters define the projection model for depth-to-3D conversion:

#### Required Parameters

```json
{
  "fx": 525.0,      // Focal length in X (pixels)
  "fy": 525.0,      // Focal length in Y (pixels)
  "cx": 319.5,      // Principal point X (pixels)
  "cy": 239.5,      // Principal point Y (pixels)
  "width": 640,     // Image width (pixels)
  "height": 480     // Image height (pixels)
}
```

#### Parameter Descriptions

- **fx, fy**: Focal lengths in pixels (from camera calibration)
  - Typical values: 500-600 for VGA resolution
  - Can be different if pixels are non-square
  
- **cx, cy**: Principal point (optical center) in pixels
  - Usually near image center: (width/2, height/2)
  - May be offset due to lens distortion correction
  
- **width, height**: Image dimensions in pixels
  - Must match actual depth image size
  - Common resolutions: 640x480, 1280x720, 1920x1080

#### Camera Pose

Camera pose defines the position and orientation in world coordinates:

```json
{
  "position": {
    "x": 1.0,    // Camera position in meters
    "y": 0.5,
    "z": 1.0
  },
  "orientation": {
    "x": 0.0,    // Quaternion orientation
    "y": 0.0,
    "z": 0.0,
    "w": 1.0
  }
}
```

#### Obtaining Camera Parameters

**From ROS camera_info topic:**
```bash
# View camera info
rostopic echo /camera/depth/camera_info

# Extract parameters
# K matrix: [fx, 0, cx, 0, fy, cy, 0, 0, 1]
# fx = K[0], fy = K[4], cx = K[2], cy = K[5]
```

**From camera calibration file:**
```yaml
# camera.yaml
camera_matrix:
  rows: 3
  cols: 3
  data: [525.0, 0.0, 319.5, 0.0, 525.0, 239.5, 0.0, 0.0, 1.0]
```

### Supported Depth Image Formats

The service supports multiple depth image encodings:

#### Encoding Types

| Encoding | Bit Depth | Data Type | Typical Use |
|----------|-----------|-----------|-------------|
| `16UC1` | 16-bit | Unsigned integer | Most common (RealSense, Kinect) |
| `32FC1` | 32-bit | Float | High precision depth |
| `mono16` | 16-bit | Unsigned integer | Alternative format |

#### Depth Scale

The `depth_scale` parameter converts pixel values to meters:

```python
depth_in_meters = pixel_value * depth_scale
```

**Common depth scales:**
- **0.001** (1mm): RealSense D435, D455
- **0.0001** (0.1mm): High precision sensors
- **1.0**: Pre-scaled float images (32FC1)

#### Image Encoding

Depth images must be Base64-encoded before sending:

**Python example:**
```python
import base64
import cv2

# Read depth image
depth_image = cv2.imread('depth.png', cv2.IMREAD_UNCHANGED)

# Encode to bytes
_, buffer = cv2.imencode('.png', depth_image)

# Base64 encode
depth_base64 = base64.b64encode(buffer).decode('utf-8')
```

### Single Depth Image Processing

Process a single depth image to update the map.

#### Endpoint

```
POST /map/depth
```

#### Request Schema

```json
{
  "depth_image": "string (base64)",
  "camera_intrinsics": {
    "fx": "number",
    "fy": "number", 
    "cx": "number",
    "cy": "number",
    "width": "integer",
    "height": "integer"
  },
  "camera_pose": {
    "position": {"x": "number", "y": "number", "z": "number"},
    "orientation": {"x": "number", "y": "number", "z": "number", "w": "number"}
  },
  "depth_scale": "number (default: 0.001)",
  "timestamp": "number (optional)",
  "frame_id": "string (default: 'camera_depth_optical_frame')",
  "encoding": "string (default: '16UC1')"
}
```

#### Response Schema

```json
{
  "success": "boolean",
  "points_generated": "integer",
  "processing_time_ms": "number",
  "timestamp": "number",
  "message": "string"
}
```

#### Example Request

```bash
curl -X POST "http://localhost:8000/map/depth" \
  -H "Content-Type: application/json" \
  -d '{
    "depth_image": "iVBORw0KGgoAAAANSUhEUgAAAAUA...",
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
    "encoding": "16UC1"
  }'
```

### Batch Depth Image Processing

Process multiple depth images in a single request for efficiency.

#### Endpoint

```
POST /map/depth/batch
```

#### Request Schema

```json
{
  "depth_images": [
    {
      "depth_image": "string (base64)",
      "camera_intrinsics": {...},
      "camera_pose": {...},
      "depth_scale": "number",
      "timestamp": "number (optional)",
      "frame_id": "string (optional)",
      "encoding": "string (optional)"
    }
  ]
}
```

#### Response Schema

```json
{
  "success": "boolean",
  "total_images": "integer",
  "successful": "integer",
  "failed": "integer",
  "results": [
    {
      "index": "integer",
      "success": "boolean",
      "points_generated": "integer",
      "processing_time_ms": "number",
      "error": "string (if failed)"
    }
  ],
  "total_processing_time_ms": "number"
}
```

#### Example Request

```bash
curl -X POST "http://localhost:8000/map/depth/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "depth_images": [
      {
        "depth_image": "iVBORw0KGgoAAAANSUhEUgAAAAUA...",
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
        "timestamp": 1699876543.123
      },
      {
        "depth_image": "iVBORw0KGgoAAAANSUhEUgAAAAUA...",
        "camera_intrinsics": {
          "fx": 525.0,
          "fy": 525.0,
          "cx": 319.5,
          "cy": 239.5,
          "width": 640,
          "height": 480
        },
        "camera_pose": {
          "position": {"x": 1.5, "y": 0.5, "z": 1.0},
          "orientation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0}
        },
        "depth_scale": 0.001,
        "timestamp": 1699876543.223
      }
    ]
  }'
```

### Python Client Examples

#### Example 1: Send Single Depth Image from RealSense

```python
import requests
import base64
import cv2
import numpy as np
import pyrealsense2 as rs

# Configure RealSense
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
pipeline.start(config)

# Get camera intrinsics
profile = pipeline.get_active_profile()
depth_profile = rs.video_stream_profile(profile.get_stream(rs.stream.depth))
intrinsics = depth_profile.get_intrinsics()

try:
    # Capture frame
    frames = pipeline.wait_for_frames()
    depth_frame = frames.get_depth_frame()
    
    # Convert to numpy array
    depth_image = np.asanyarray(depth_frame.get_data())
    
    # Encode to base64
    _, buffer = cv2.imencode('.png', depth_image)
    depth_base64 = base64.b64encode(buffer).decode('utf-8')
    
    # Prepare request
    request_data = {
        "depth_image": depth_base64,
        "camera_intrinsics": {
            "fx": intrinsics.fx,
            "fy": intrinsics.fy,
            "cx": intrinsics.ppx,
            "cy": intrinsics.ppy,
            "width": intrinsics.width,
            "height": intrinsics.height
        },
        "camera_pose": {
            "position": {"x": 1.0, "y": 0.5, "z": 1.0},
            "orientation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0}
        },
        "depth_scale": 0.001,  # RealSense depth scale
        "encoding": "16UC1"
    }
    
    # Send request
    response = requests.post(
        "http://localhost:8000/map/depth",
        json=request_data
    )
    
    print(f"Success: {response.json()['success']}")
    print(f"Points generated: {response.json()['points_generated']}")
    print(f"Processing time: {response.json()['processing_time_ms']:.2f}ms")
    
finally:
    pipeline.stop()
```

#### Example 2: Send Depth Image from File

```python
import requests
import base64
import cv2

def send_depth_image(image_path, camera_params, camera_pose):
    """Send a depth image file to the API."""
    
    # Read depth image
    depth_image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    
    # Encode to base64
    _, buffer = cv2.imencode('.png', depth_image)
    depth_base64 = base64.b64encode(buffer).decode('utf-8')
    
    # Prepare request
    request_data = {
        "depth_image": depth_base64,
        "camera_intrinsics": camera_params,
        "camera_pose": camera_pose,
        "depth_scale": 0.001,
        "encoding": "16UC1"
    }
    
    # Send request
    response = requests.post(
        "http://localhost:8000/map/depth",
        json=request_data
    )
    
    return response.json()

# Example usage
camera_params = {
    "fx": 525.0,
    "fy": 525.0,
    "cx": 319.5,
    "cy": 239.5,
    "width": 640,
    "height": 480
}

camera_pose = {
    "position": {"x": 1.0, "y": 0.5, "z": 1.0},
    "orientation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0}
}

result = send_depth_image("depth_image.png", camera_params, camera_pose)
print(f"Result: {result}")
```

#### Example 3: Batch Processing Multiple Images

```python
import requests
import base64
import cv2
import glob

def process_depth_batch(image_paths, camera_params, camera_poses):
    """Process multiple depth images in batch."""
    
    depth_images = []
    
    for i, (image_path, pose) in enumerate(zip(image_paths, camera_poses)):
        # Read and encode image
        depth_image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        _, buffer = cv2.imencode('.png', depth_image)
        depth_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Add to batch
        depth_images.append({
            "depth_image": depth_base64,
            "camera_intrinsics": camera_params,
            "camera_pose": pose,
            "depth_scale": 0.001,
            "timestamp": 1699876543.0 + i * 0.1,
            "encoding": "16UC1"
        })
    
    # Send batch request
    response = requests.post(
        "http://localhost:8000/map/depth/batch",
        json={"depth_images": depth_images}
    )
    
    return response.json()

# Example usage
image_paths = glob.glob("depth_images/*.png")
camera_params = {
    "fx": 525.0,
    "fy": 525.0,
    "cx": 319.5,
    "cy": 239.5,
    "width": 640,
    "height": 480
}

# Generate poses (example: moving along X axis)
camera_poses = [
    {
        "position": {"x": i * 0.5, "y": 0.5, "z": 1.0},
        "orientation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0}
    }
    for i in range(len(image_paths))
]

result = process_depth_batch(image_paths, camera_params, camera_poses)
print(f"Total images: {result['total_images']}")
print(f"Successful: {result['successful']}")
print(f"Failed: {result['failed']}")
print(f"Total time: {result['total_processing_time_ms']:.2f}ms")
```

#### Example 4: Integration with ROS

```python
import rospy
import requests
import base64
import cv2
import numpy as np
from sensor_msgs.msg import Image, CameraInfo
from geometry_msgs.msg import PoseStamped
from cv_bridge import CvBridge

class DepthImagePublisher:
    def __init__(self, api_url="http://localhost:8000"):
        self.api_url = api_url
        self.bridge = CvBridge()
        self.camera_info = None
        self.camera_pose = None
        
        # Subscribe to topics
        rospy.Subscriber("/camera/depth/image_raw", Image, self.depth_callback)
        rospy.Subscriber("/camera/depth/camera_info", CameraInfo, self.info_callback)
        rospy.Subscriber("/camera/pose", PoseStamped, self.pose_callback)
    
    def info_callback(self, msg):
        """Store camera intrinsics."""
        self.camera_info = {
            "fx": msg.K[0],
            "fy": msg.K[4],
            "cx": msg.K[2],
            "cy": msg.K[5],
            "width": msg.width,
            "height": msg.height
        }
    
    def pose_callback(self, msg):
        """Store camera pose."""
        self.camera_pose = {
            "position": {
                "x": msg.pose.position.x,
                "y": msg.pose.position.y,
                "z": msg.pose.position.z
            },
            "orientation": {
                "x": msg.pose.orientation.x,
                "y": msg.pose.orientation.y,
                "z": msg.pose.orientation.z,
                "w": msg.pose.orientation.w
            }
        }
    
    def depth_callback(self, msg):
        """Process depth image and send to API."""
        if self.camera_info is None or self.camera_pose is None:
            rospy.logwarn("Waiting for camera info and pose...")
            return
        
        try:
            # Convert ROS image to numpy
            depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
            
            # Encode to base64
            _, buffer = cv2.imencode('.png', depth_image)
            depth_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Prepare request
            request_data = {
                "depth_image": depth_base64,
                "camera_intrinsics": self.camera_info,
                "camera_pose": self.camera_pose,
                "depth_scale": 0.001,
                "timestamp": msg.header.stamp.to_sec(),
                "frame_id": msg.header.frame_id,
                "encoding": msg.encoding
            }
            
            # Send to API
            response = requests.post(
                f"{self.api_url}/map/depth",
                json=request_data,
                timeout=1.0
            )
            
            if response.json()["success"]:
                rospy.loginfo(f"Processed depth image: {response.json()['points_generated']} points")
            else:
                rospy.logwarn(f"Failed to process depth image: {response.json()['message']}")
                
        except Exception as e:
            rospy.logerr(f"Error processing depth image: {e}")

if __name__ == "__main__":
    rospy.init_node("depth_image_publisher")
    publisher = DepthImagePublisher()
    rospy.spin()
```

## API Documentation

The service provides comprehensive API documentation through multiple interfaces:

### 1. Interactive Documentation (Swagger UI)

Access at: **http://localhost:8000/docs**

Features:
- Interactive API explorer - try endpoints directly from your browser
- View complete request/response schemas
- See example values and validation rules
- Download OpenAPI specification (JSON/YAML)
- Test authentication and error scenarios

### 2. Alternative Documentation (ReDoc)

Access at: **http://localhost:8000/redoc**

Features:
- Clean, readable documentation layout
- Detailed schema descriptions with examples
- Code samples in multiple languages
- Search functionality across all endpoints
- Responsive design for mobile viewing

### 3. API Reference Document

See `API_REFERENCE.md` for complete endpoint documentation including:
- Detailed request/response schemas
- All error codes and status codes
- Code examples in cURL and Python
- Parameter validation rules
- Common usage patterns

### 4. OpenAPI Specification

The service automatically generates an OpenAPI 3.0 specification:

**JSON Format:** http://localhost:8000/openapi.json

Use this specification to:
- Generate client libraries in any language
- Import into API testing tools (Postman, Insomnia)
- Generate documentation in other formats
- Validate requests/responses programmatically

### Automatic Documentation Generation

FastAPI automatically generates documentation from:
- Type hints and Pydantic models
- Docstrings in endpoint functions
- Response model definitions
- Exception handler configurations

The documentation is always up-to-date with the code - no manual updates required!

## Development

This is the base project structure. Implementation tasks are defined in:
`.kiro/specs/fastapi-fast-planner-interface/tasks.md`

## Error Handling

The service implements comprehensive error handling with structured error responses. See `ERROR_HANDLING.md` for detailed documentation on:

- Error categories and HTTP status codes
- Exception classes and usage
- Error response format
- Logging behavior
- Client error handling examples

## Logging and Monitoring

The service provides comprehensive logging and monitoring capabilities. See `LOGGING_MONITORING.md` for detailed documentation on:

- Structured logging configuration
- Request/response tracking with correlation IDs
- Performance metrics and monitoring
- Error logging with stack traces
- Health monitoring endpoints
- Integration with monitoring tools (Prometheus, ELK, Grafana)

## Troubleshooting

### Configuration Issues

**Service fails to start with "Configuration validation failed":**
- Check that all numeric values are positive
- Verify log level is one of: debug, info, warning, error, critical
- Ensure ROS Master URI starts with `http://` or `https://`
- Verify port number is between 1 and 65535

**"ROS Master not found" error:**
- Verify ROS Master is running: `roscore`
- Check `ROS_MASTER_URI` environment variable or `ros.master_uri` in config
- Test ROS connection: `rostopic list`
- Ensure network connectivity if using remote ROS Master

**"Configuration file not found" error:**
- Check `CONFIG_FILE` environment variable points to correct path
- Verify `config.yaml` exists in `fastapi_planner/` directory
- Use absolute path if running from different directory

**Environment variables not taking effect:**
- Verify environment variables are exported: `echo $ROS_MASTER_URI`
- Check variable names match exactly (case-sensitive)
- Restart service after changing environment variables
- Environment variables override YAML settings

**CORS errors in browser:**
- Set `enable_cors: true` in config.yaml
- Add your domain to `cors_origins` list
- Use `["*"]` for development (not recommended for production)

### ROS Communication Issues

**"Fast-Planner node not responding":**
- Verify Fast-Planner is running: `rosnode list | grep fast_planner`
- Check topic names match Fast-Planner configuration
- Verify topics exist: `rostopic list`
- Check topic types: `rostopic info /planning/bspline`

**"Odometry unavailable" error:**
- Verify odometry topic is publishing: `rostopic echo /state_ukf/odom`
- Check topic name in config matches your odometry source
- Ensure odometry is publishing at reasonable rate (>1 Hz)

**Planning requests timeout:**
- Increase `planning_timeout` in config.yaml
- Check Fast-Planner logs for errors
- Verify map and obstacles are loaded in Fast-Planner
- Test Fast-Planner directly with ROS tools

### Performance Issues

**Slow planning response:**
- Check `planning_timeout` setting (may be too high)
- Verify Fast-Planner is not overloaded
- Monitor CPU usage on ROS Master machine
- Consider reducing `trajectory_sample_rate` if not needed

**High memory usage:**
- Reduce `trajectory_sample_rate` to generate fewer waypoints
- Check for memory leaks in Fast-Planner
- Monitor with: `docker stats` (if using Docker)

## ROS Topic Requirements

The service requires the following ROS topics to be available:

### Required Topics

#### Odometry Topic (Subscribe)
- **Topic**: `/state_ukf/odom` (configurable via `ros.topics.odometry`)
- **Message Type**: `nav_msgs/Odometry`
- **Purpose**: Provides current quadrotor position, orientation, and velocities
- **Requirements**: 
  - Must publish at ≥1 Hz for reliable operation
  - Messages older than 1 second are considered stale
  - Used when `use_current_odom: true` in planning requests

#### Trajectory Topic (Subscribe)
- **Topic**: `/planning/bspline` (configurable via `ros.topics.trajectory`)
- **Message Type**: `plan_manage/Bspline`
- **Purpose**: Receives planned B-spline trajectories from Fast-Planner
- **Requirements**:
  - Published by Fast-Planner after successful planning
  - Contains B-spline control points and timing information
  - Converted to waypoints at configured sample rate (default 10 Hz)

#### Goal Topic (Publish)
- **Topic**: `/move_base_simple/goal` (configurable via `ros.topics.goal`)
- **Message Type**: `geometry_msgs/PoseStamped`
- **Purpose**: Sends goal positions to Fast-Planner
- **Requirements**:
  - Fast-Planner must subscribe to this topic
  - Can be algorithm-specific (see Algorithm Selection below)

### Algorithm-Specific Topics

The service supports algorithm-specific goal topics for kinodynamic and topological planning:

#### Kinodynamic Algorithm
- **Topic**: Configurable via `ros.topics.kinodynamic_goal`
- **Default**: Uses `ros.topics.goal` if not specified
- **Usage**: Set `algorithm: "kinodynamic"` in planning request

#### Topological Algorithm
- **Topic**: Configurable via `ros.topics.topological_goal`
- **Default**: Uses `ros.topics.goal` if not specified
- **Usage**: Set `algorithm: "topological"` in planning request

### Topic Configuration Example

```yaml
ros:
  topics:
    odometry: "/state_ukf/odom"
    goal: "/move_base_simple/goal"
    trajectory: "/planning/bspline"
    kinodynamic_goal: "/planning/kinodynamic/goal"  # Optional
    topological_goal: "/planning/topological/goal"  # Optional
```

### Verifying Topics

Check that required topics are available:

```bash
# List all topics
rostopic list

# Check odometry topic
rostopic echo /state_ukf/odom -n 1

# Check trajectory topic
rostopic info /planning/bspline

# Monitor goal publications
rostopic echo /move_base_simple/goal
```

## Fast-Planner Setup

### Prerequisites

The service requires Fast-Planner to be installed and running. Follow these steps:

### 1. Install Fast-Planner

```bash
# Clone Fast-Planner repository
cd ~/catkin_ws/src
git clone https://github.com/HKUST-Aerial-Robotics/Fast-Planner.git

# Install dependencies
sudo apt-get install ros-noetic-nlopt
sudo apt-get install libarmadillo-dev

# Build
cd ~/catkin_ws
catkin_make
source devel/setup.bash
```

### 2. Configure Fast-Planner

Edit Fast-Planner configuration files to match your environment:

**Map Configuration** (`plan_manage/config/`):
- Set map size to match `config.yaml` map dimensions
- Configure obstacle detection parameters
- Set planning algorithm parameters

**Launch Files** (`plan_manage/launch/`):
- Verify topic names match service configuration
- Configure algorithm-specific parameters
- Set visualization options

### 3. Launch Fast-Planner

#### Kinodynamic Planning

```bash
roslaunch plan_manage kino_replan.launch
```

This launches:
- Fast-Planner node with kinodynamic algorithm
- Map server and obstacle detection
- RViz visualization (optional)

#### Topological Planning

```bash
roslaunch plan_manage topo_replan.launch
```

This launches:
- Fast-Planner node with topological algorithm
- Map server and obstacle detection
- RViz visualization (optional)

### 4. Verify Fast-Planner

Check that Fast-Planner is running:

```bash
# Check Fast-Planner node
rosnode list | grep fast_planner

# Check subscribed topics
rosnode info /fast_planner_node

# Verify trajectory topic
rostopic info /planning/bspline
```

### 5. Test Planning

Send a test goal using ROS tools:

```bash
# Publish test goal
rostopic pub /move_base_simple/goal geometry_msgs/PoseStamped \
  "header:
    frame_id: 'world'
  pose:
    position: {x: 10.0, y: 5.0, z: 1.5}
    orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}"

# Monitor trajectory output
rostopic echo /planning/bspline
```

### Integration with FastAPI Service

Once Fast-Planner is running:

1. **Start the FastAPI service**:
   ```bash
   python3 -m fastapi_planner.main
   ```

2. **Verify connection**:
   ```bash
   curl http://localhost:8000/health
   ```
   
   Should return `"fast_planner_available": true`

3. **Send planning request**:
   ```bash
   curl -X POST http://localhost:8000/plan \
     -H "Content-Type: application/json" \
     -d '{"start": {"x": 0, "y": 0, "z": 1}, "goal": {"x": 10, "y": 5, "z": 1.5}}'
   ```

### Common Fast-Planner Issues

**Fast-Planner not responding:**
- Check that Fast-Planner node is running: `rosnode list`
- Verify topic subscriptions: `rosnode info /fast_planner_node`
- Check Fast-Planner logs for errors
- Ensure map and obstacles are loaded

**Planning always fails:**
- Verify map boundaries match configuration
- Check that start/goal positions are not in collision
- Increase planning timeout in Fast-Planner config
- Review Fast-Planner algorithm parameters

**Trajectory not received:**
- Verify trajectory topic name matches configuration
- Check message type: `rostopic type /planning/bspline`
- Monitor topic for publications: `rostopic hz /planning/bspline`
- Check Fast-Planner is publishing after planning

## Requirements

See `requirements.md` and `design.md` in `.kiro/specs/fastapi-fast-planner-interface/` for detailed specifications.
