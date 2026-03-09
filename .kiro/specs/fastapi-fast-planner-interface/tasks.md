# Implementation Plan

- [x] 1. Set up project structure and dependencies
  - Create fastapi_planner/ directory at workspace root (same level as src/)
  - Create requirements.txt with FastAPI, uvicorn, rospy, pydantic dependencies
  - Create config.yaml template for service configuration in fastapi_planner/
  - Update existing Dockerfile.dev or create new Dockerfile to include FastAPI service
  - _Requirements: 4.1, 4.2, 4.3_

- [x] 2. Implement configuration management
  - Create config.py module to load YAML configuration
  - Implement ServiceConfig class with ROS, planning, and map parameters
  - Add environment variable override support
  - Add configuration validation on startup
  - _Requirements: 4.1, 4.2, 4.3_

- [x] 3. Implement data models
  - Create models.py with Pydantic models for Position, PlanRequest, Waypoint, Trajectory
  - Implement request validation with bounds checking for map size
  - Create PlanResponse, OdometryResponse, HealthResponse models
  - Create ErrorInfo model for error responses
  - _Requirements: 1.3, 1.4, 1.5, 2.1, 2.2, 3.1-3.5, 5.2, 6.2-6.4, 7.1, 7.4, 8.1-8.4_

- [x] 4. Implement ROS Bridge component
  - Create ros_bridge.py module with ROSBridge class
  - Implement ROS node initialization and connection management
  - Implement odometry subscriber with message caching (max age 1 second)
  - Implement goal publisher to /move_base_simple/goal topic
  - Implement trajectory subscriber to /planning/bspline topic
  - Add ROS connection validation and status checking
  - _Requirements: 4.4, 5.1-5.5_

- [x] 5. Implement B-spline trajectory conversion
  - Create trajectory_utils.py module
  - Implement B-spline evaluation function for position, velocity, acceleration
  - Implement conversion from plan_manage/Bspline message to waypoint list
  - Sample trajectory at 10 Hz (0.1 second intervals) as specified
  - Validate monotonically increasing timestamps
  - _Requirements: 2.1, 2.3, 2.4, 2.5_

- [x] 6. Implement Planning Client component
  - Create planning_client.py with PlanningClient class
  - Implement plan_trajectory async method with timeout handling
  - Add request-response correlation using trajectory IDs
  - Implement trajectory validation logic
  - Add planning time measurement (ROS and total time)
  - _Requirements: 1.1, 8.1, 8.2, 8.3, 8.4_

- [x] 7. Implement API endpoints
  - Create main.py with FastAPI application initialization
  - Implement POST /plan endpoint with request validation
  - Implement GET /odometry endpoint with availability checking
  - Implement GET /health endpoint with status checks
  - Add CORS middleware configuration
  - _Requirements: 1.1, 1.2, 5.1, 5.3, 6.1_

- [x] 8. Implement error handling
  - Create exception handlers for validation errors (400)
  - Create exception handlers for planning failures (422)
  - Create exception handlers for service unavailable (503)
  - Create exception handlers for timeout errors (504)
  - Implement error response formatting with ErrorInfo model
  - Add logging for all error cases
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 9. Implement health monitoring
  - Add ROS connection status checking in health endpoint
  - Add Fast-Planner node availability checking
  - Track service uptime since startup
  - Track last successful planning timestamp
  - Calculate and return odometry message age
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 10. Implement algorithm selection
  - Add algorithm parameter handling in PlanRequest model
  - Implement topic routing based on algorithm type (kinodynamic vs topological)
  - Set default algorithm to "kinodynamic"
  - Add validation for supported algorithm values
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [x] 11. Add startup and shutdown handling
  - Implement application startup event to initialize ROS connection
  - Add ROS connection validation on startup with exit on failure
  - Implement graceful shutdown to cleanup ROS resources
  - Add startup logging for configuration and connection status
  - _Requirements: 4.4, 4.5_

- [x] 12. Create configuration files
  - Create default config.yaml with all parameters documented
  - Create .env.example file for environment variables
  - Update docker-compose.yml if needed to expose FastAPI port
  - Document configuration options in README
  - _Requirements: 4.1, 4.2, 4.3_

- [x] 13. Add logging and monitoring
  - Configure structured logging with appropriate log levels
  - Add request/response logging for debugging
  - Add planning time logging for performance monitoring
  - Add error logging with stack traces
  - _Requirements: 8.5_

- [ ]* 14. Write unit tests
  - Write tests for data model validation
  - Write tests for B-spline trajectory conversion
  - Write tests for configuration loading
  - Write tests for error response formatting
  - _Requirements: All_

- [ ]* 15. Write integration tests
  - Create mock ROS environment for testing
  - Write end-to-end test for successful planning request
  - Write tests for error scenarios (no path, collision, timeout)
  - Write tests for odometry and health endpoints
  - _Requirements: All_

- [x] 16. Create documentation
  - Create README.md with installation and usage instructions
  - Document API endpoints with request/response examples
  - Create API documentation using FastAPI's automatic OpenAPI generation
  - Document ROS topic requirements and Fast-Planner setup
  - _Requirements: All_

- [x] 17. Extend data models for depth image processing
  - Add CameraIntrinsics model with focal length, principal point, and image dimensions
  - Add CameraPose model with position and orientation (quaternion)
  - Add DepthImageRequest model with depth image data, camera parameters, and metadata
  - Add DepthImageBatchRequest model for batch processing
  - Add DepthProcessingResult and DepthBatchResponse models for responses
  - Add validation for base64 encoded image data
  - Add validation for camera parameter ranges
  - _Requirements: 9.1, 9.2, 9.3, 11.1, 11.2, 11.3, 11.4, 11.5, 14.1_

- [x] 18. Implement depth image processing core functionality
- [x] 18.1 Create depth_processor.py module with DepthProcessor class
  - Initialize with depth configuration (min/max depth, voxel size)
  - Set up numpy and opencv dependencies
  - _Requirements: 9.1, 13.1, 13.2, 13.3_

- [x] 18.2 Implement depth image decoding
  - Decode base64 encoded image data to numpy array
  - Support 16UC1 encoding (16-bit unsigned integer)
  - Support 32FC1 encoding (32-bit float)
  - Validate image dimensions match camera parameters
  - Handle decoding errors with appropriate exceptions
  - _Requirements: 9.2, 11.5, 12.4_

- [x] 18.3 Implement depth to point cloud conversion
  - Convert depth pixels to 3D points using camera intrinsics formula
  - Apply depth scale to convert raw values to meters
  - Filter out invalid depth values (zero, negative, NaN)
  - Apply depth range filtering (min_depth to max_depth)
  - Return numpy array of 3D points in camera frame
  - _Requirements: 10.1, 10.3, 10.4, 13.1, 13.2_

- [x] 18.4 Implement coordinate transformation
  - Transform points from camera frame to map frame using camera pose
  - Apply rotation using quaternion to rotation matrix conversion
  - Apply translation to get final map coordinates
  - Validate transformed points are within map boundaries
  - _Requirements: 10.2_

- [x] 18.5 Implement point cloud downsampling
  - Implement voxel grid downsampling to reduce point density
  - Use configurable voxel size from configuration
  - Preserve point distribution while reducing count
  - _Requirements: 13.3_

- [x] 19. Extend ROS Bridge for point cloud publishing
  - Add point cloud publisher to ROS Bridge class
  - Implement publish_point_cloud method accepting numpy array of points
  - Convert numpy points to sensor_msgs/PointCloud2 message format
  - Set appropriate header with timestamp and frame_id
  - Configure point cloud topic from configuration file
  - Add error handling for publishing failures
  - _Requirements: 10.5, 12.5, 13.4_

- [x] 20. Implement depth image API endpoints
- [x] 20.1 Implement POST /map/depth endpoint
  - Accept DepthImageRequest in request body
  - Validate request parameters
  - Call DepthProcessor to convert depth image to point cloud
  - Publish point cloud via ROS Bridge
  - Return DepthProcessingResult with success status and metrics
  - Handle and return appropriate error responses (400, 503)
  - _Requirements: 9.1, 12.1, 12.2, 12.3, 12.4, 12.5_

- [x] 20.2 Implement POST /map/depth/batch endpoint
  - Accept DepthImageBatchRequest with multiple depth images
  - Validate batch size does not exceed maximum (10 images)
  - Process each depth image sequentially
  - Continue processing on individual failures
  - Collect results for each image in batch
  - Return DepthBatchResponse with aggregated results
  - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_

- [x] 21. Update configuration for depth processing
  - Add depth section to config.yaml with min_depth, max_depth, voxel_size
  - Add max_batch_size parameter for batch processing
  - Add default_encoding parameter for depth images
  - Add point_cloud topic name to ROS topics configuration
  - Update Config class to load depth parameters
  - Add validation that min_depth < max_depth
  - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_

- [x] 22. Add error handling for depth processing
  - Create custom exceptions for depth processing errors
  - Add exception handler for invalid depth image format
  - Add exception handler for dimension mismatch
  - Add exception handler for ROS publishing failures
  - Add logging for depth processing errors
  - _Requirements: 12.4, 12.5_

- [ ]* 23. Write unit tests for depth processing
  - Test depth image decoding for 16UC1 and 32FC1 formats
  - Test depth to point cloud conversion with known camera parameters
  - Test coordinate transformation with known poses
  - Test depth range filtering removes out-of-range points
  - Test point cloud downsampling reduces point count
  - Test invalid depth value handling (zeros, negatives, NaN)
  - Test camera parameter validation
  - _Requirements: 9.1-9.5, 10.1-10.5, 11.1-11.5_

- [ ]* 24. Write integration tests for depth endpoints
  - Test POST /map/depth with valid depth image
  - Test POST /map/depth with invalid image format
  - Test POST /map/depth with dimension mismatch
  - Test POST /map/depth/batch with multiple images
  - Test batch processing with partial failures
  - Test ROS point cloud message publishing
  - Verify point cloud data correctness
  - _Requirements: 12.1-12.5, 14.1-14.5_

- [x] 25. Update documentation for depth processing
  - Document depth image API endpoints in README
  - Add examples for single and batch depth image requests
  - Document camera parameter requirements
  - Document supported depth image formats
  - Add example code for sending depth images from Python client
  - Update API reference with depth processing endpoints
  - _Requirements: 9.1-9.5, 11.1-11.5, 14.1-14.5_
