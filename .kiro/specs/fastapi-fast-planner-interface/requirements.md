# Requirements Document

## Introduction

This document specifies the requirements for a FastAPI-based REST API service that interfaces with the Fast-Planner ROS system. The service will accept planning requests with necessary parameters and return control commands/trajectories for quadrotor navigation. This enables non-ROS applications to utilize Fast-Planner's robust trajectory planning capabilities through a standard HTTP interface.

## Glossary

- **Fast-Planner**: A ROS-based quadrotor trajectory planning system that generates collision-free, dynamically feasible trajectories
- **FastAPI Service**: The HTTP REST API server that bridges external applications with the Fast-Planner ROS system
- **Planning Request**: An HTTP request containing start position, goal position, and planning parameters
- **Control Command**: Position, velocity, and acceleration commands for quadrotor control
- **Trajectory**: A time-parameterized path consisting of position, velocity, and acceleration waypoints
- **ROS Bridge**: The component that translates HTTP requests to ROS messages and ROS responses back to HTTP
- **Odometry**: The current pose (position and orientation) and velocity of the quadrotor

## Requirements

### Requirement 1

**User Story:** As a robotics application developer, I want to send planning requests via HTTP POST, so that I can integrate Fast-Planner into my non-ROS application

#### Acceptance Criteria

1. WHEN the FastAPI Service receives a POST request at `/plan` endpoint with valid JSON payload, THE FastAPI Service SHALL return a 200 status code with trajectory data
2. WHEN the FastAPI Service receives a POST request with invalid JSON format, THE FastAPI Service SHALL return a 400 status code with error details
3. THE FastAPI Service SHALL accept planning parameters including start position (x, y, z), goal position (x, y, z), maximum velocity, and maximum acceleration
4. THE FastAPI Service SHALL validate that position coordinates are within configured map boundaries before processing
5. THE FastAPI Service SHALL validate that velocity and acceleration limits are positive values

### Requirement 2

**User Story:** As a robotics application developer, I want to receive trajectory waypoints with timestamps, so that I can execute the planned path on my quadrotor

#### Acceptance Criteria

1. WHEN a planning request succeeds, THE FastAPI Service SHALL return a trajectory containing at least position, velocity, acceleration, and timestamp for each waypoint
2. THE FastAPI Service SHALL return trajectory data in JSON format with clearly defined structure
3. WHEN the trajectory contains N waypoints, THE FastAPI Service SHALL ensure timestamps are monotonically increasing
4. THE FastAPI Service SHALL include trajectory metadata such as total duration and number of waypoints
5. THE FastAPI Service SHALL return trajectory waypoints at a frequency of at least 10 Hz (0.1 second intervals)

### Requirement 3

**User Story:** As a robotics application developer, I want to receive error messages when planning fails, so that I can handle failures appropriately in my application

#### Acceptance Criteria

1. WHEN Fast-Planner cannot find a valid path to the goal, THE FastAPI Service SHALL return a 422 status code with reason "no_path_found"
2. WHEN the goal position is in collision with obstacles, THE FastAPI Service SHALL return a 422 status code with reason "goal_in_collision"
3. WHEN the start position is in collision with obstacles, THE FastAPI Service SHALL return a 422 status code with reason "start_in_collision"
4. WHEN Fast-Planner times out during planning, THE FastAPI Service SHALL return a 504 status code with reason "planning_timeout"
5. THE FastAPI Service SHALL include descriptive error messages in the response body for all failure cases

### Requirement 4

**User Story:** As a system administrator, I want to configure the ROS connection parameters, so that I can deploy the service in different environments

#### Acceptance Criteria

1. THE FastAPI Service SHALL read ROS master URI from environment variable or configuration file
2. THE FastAPI Service SHALL read Fast-Planner topic names from configuration file
3. THE FastAPI Service SHALL read map size boundaries from configuration file
4. THE FastAPI Service SHALL validate ROS connection on startup and log connection status
5. WHEN ROS connection fails on startup, THE FastAPI Service SHALL exit with error code 1 and descriptive error message

### Requirement 5

**User Story:** As a robotics application developer, I want to query the current odometry state, so that I can use the current position as the start position for planning

#### Acceptance Criteria

1. THE FastAPI Service SHALL provide a GET endpoint at `/odometry` that returns current quadrotor state
2. WHEN odometry data is available, THE FastAPI Service SHALL return position (x, y, z), orientation (quaternion), linear velocity, and angular velocity
3. WHEN no odometry data has been received, THE FastAPI Service SHALL return a 503 status code with reason "odometry_unavailable"
4. THE FastAPI Service SHALL include timestamp of the odometry measurement in the response
5. THE FastAPI Service SHALL cache the most recent odometry message with maximum age of 1 second

### Requirement 6

**User Story:** As a robotics application developer, I want to check service health status, so that I can monitor whether the service is operational

#### Acceptance Criteria

1. THE FastAPI Service SHALL provide a GET endpoint at `/health` that returns service status
2. THE FastAPI Service SHALL return status "healthy" when ROS connection is active and Fast-Planner node is running
3. THE FastAPI Service SHALL return status "degraded" when ROS connection is active but Fast-Planner node is not responding
4. THE FastAPI Service SHALL return status "unhealthy" when ROS connection is lost
5. THE FastAPI Service SHALL include uptime and last successful planning timestamp in health response

### Requirement 7

**User Story:** As a robotics application developer, I want to specify planning algorithm type, so that I can choose between kinodynamic and topological planning

#### Acceptance Criteria

1. THE FastAPI Service SHALL accept an optional "algorithm" parameter with values "kinodynamic" or "topological"
2. WHEN no algorithm is specified, THE FastAPI Service SHALL use "kinodynamic" as default
3. THE FastAPI Service SHALL publish planning requests to the appropriate ROS topic based on algorithm selection
4. WHEN an unsupported algorithm value is provided, THE FastAPI Service SHALL return a 400 status code with list of valid algorithms
5. THE FastAPI Service SHALL document supported algorithms in the API schema

### Requirement 8

**User Story:** As a robotics application developer, I want to receive planning computation time, so that I can assess real-time performance

#### Acceptance Criteria

1. THE FastAPI Service SHALL measure time from request receipt to trajectory response
2. THE FastAPI Service SHALL include "planning_time_ms" field in successful response containing computation time in milliseconds
3. THE FastAPI Service SHALL include "ros_planning_time_ms" field containing the time Fast-Planner took to compute trajectory
4. THE FastAPI Service SHALL include "total_time_ms" field containing end-to-end request processing time
5. THE FastAPI Service SHALL log planning times for performance monitoring

### Requirement 9

**User Story:** As a robotics application developer, I want to upload depth images to build occupancy maps, so that I can update the planning environment dynamically based on sensor data

#### Acceptance Criteria

1. THE FastAPI Service SHALL provide a POST endpoint at `/map/depth` that accepts depth image data
2. THE FastAPI Service SHALL accept depth images in common formats including PNG, JPEG, and raw depth arrays
3. THE FastAPI Service SHALL accept camera intrinsic parameters including focal length, principal point, and image dimensions
4. THE FastAPI Service SHALL accept camera pose including position and orientation relative to the map frame
5. THE FastAPI Service SHALL validate that depth image dimensions match the provided camera parameters

### Requirement 10

**User Story:** As a robotics application developer, I want the service to convert depth images to 3D point clouds, so that obstacle information can be integrated into the planning map

#### Acceptance Criteria

1. WHEN the FastAPI Service receives a valid depth image, THE FastAPI Service SHALL convert depth pixels to 3D points using camera intrinsics
2. THE FastAPI Service SHALL transform 3D points from camera frame to map frame using provided camera pose
3. THE FastAPI Service SHALL filter out invalid depth values including zero, negative, and values exceeding maximum range
4. THE FastAPI Service SHALL apply depth range limits with configurable minimum and maximum depth thresholds
5. THE FastAPI Service SHALL publish the generated point cloud to ROS topic for Fast-Planner consumption

### Requirement 11

**User Story:** As a robotics application developer, I want to specify depth image metadata, so that the service can correctly interpret and process the depth data

#### Acceptance Criteria

1. THE FastAPI Service SHALL accept depth scale parameter to convert raw depth values to meters
2. THE FastAPI Service SHALL accept timestamp for the depth image measurement
3. THE FastAPI Service SHALL accept frame_id to identify the coordinate frame of the depth image
4. THE FastAPI Service SHALL accept optional depth encoding format including 16-bit unsigned integer and 32-bit float
5. WHEN depth encoding is not specified, THE FastAPI Service SHALL use 16-bit unsigned integer as default

### Requirement 12

**User Story:** As a robotics application developer, I want to receive confirmation when depth images are processed, so that I can verify map updates are applied

#### Acceptance Criteria

1. WHEN depth image processing succeeds, THE FastAPI Service SHALL return a 200 status code with processing summary
2. THE FastAPI Service SHALL include number of valid points generated in the response
3. THE FastAPI Service SHALL include processing time in milliseconds in the response
4. WHEN depth image processing fails due to invalid parameters, THE FastAPI Service SHALL return a 400 status code with error details
5. WHEN ROS point cloud publishing fails, THE FastAPI Service SHALL return a 503 status code with reason "ros_publish_failed"

### Requirement 13

**User Story:** As a robotics application developer, I want to configure depth processing parameters, so that I can optimize map quality for different sensors and environments

#### Acceptance Criteria

1. THE FastAPI Service SHALL read minimum depth threshold from configuration file with default value of 0.1 meters
2. THE FastAPI Service SHALL read maximum depth threshold from configuration file with default value of 10.0 meters
3. THE FastAPI Service SHALL read point cloud downsampling voxel size from configuration file
4. THE FastAPI Service SHALL read ROS point cloud topic name from configuration file
5. THE FastAPI Service SHALL validate that minimum depth is less than maximum depth on startup

### Requirement 14

**User Story:** As a robotics application developer, I want to send multiple depth images in batch, so that I can efficiently update the map from multiple camera views

#### Acceptance Criteria

1. THE FastAPI Service SHALL provide a POST endpoint at `/map/depth/batch` that accepts multiple depth images
2. THE FastAPI Service SHALL process each depth image in the batch sequentially
3. THE FastAPI Service SHALL return processing results for each depth image in the batch
4. WHEN one depth image in the batch fails processing, THE FastAPI Service SHALL continue processing remaining images
5. THE FastAPI Service SHALL limit batch size to a maximum of 10 depth images per request
