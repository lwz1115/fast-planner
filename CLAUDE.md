# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a hybrid ROS/FastAPI project combining Fast-Planner (a quadrotor trajectory planning system) with a REST API interface. The project consists of:

1. **Fast-Planner ROS Package** (`src/Fast-Planner/`) - C++ ROS Noetic/Melodic packages for UAV trajectory planning
2. **FastAPI Service** (`fastapi_planner/`) - Python REST API bridge to expose Fast-Planner functionality via HTTP

## Architecture

### Fast-Planner (ROS C++)

Fast-Planner is organized into modular ROS packages under `src/Fast-Planner/fast_planner/`:

- **plan_env**: Online mapping using depth images/point clouds, builds ESDF (Euclidean Signed Distance Field)
- **path_searching**: Front-end path finding algorithms (kinodynamic A*, topological path search)
- **bspline**: B-spline trajectory representation
- **bspline_opt**: Gradient-based B-spline trajectory optimization
- **plan_manage**: High-level planning FSM (Finite State Machine), launches and coordinates all modules
- **poly_traj**: Polynomial trajectory utilities
- **traj_utils**: Visualization tools

### FastAPI Service (Python)

Located in `fastapi_planner/`, provides HTTP REST API to ROS:

- **main.py**: FastAPI application with planning endpoints
- **ros_bridge.py**: ROS topic publisher/subscriber bridge
- **planning_client.py**: ROS service client wrapper
- **depth_processor.py**: Depth image to point cloud conversion
- **models.py**: Pydantic data models for API
- **config.yaml**: Service configuration (ROS topics, planning parameters)

## Build and Run Commands

### ROS Fast-Planner

Build the ROS workspace:
```bash
cd /media/zzxl/数据/my_projects/fastplanner
catkin_make
source devel/setup.bash
```

Launch visualization (Rviz):
```bash
source devel/setup.bash
roslaunch plan_manage rviz.launch
```

Launch kinodynamic planning with simulator:
```bash
source devel/setup.bash
roslaunch plan_manage kino_replan.launch
```

Launch topological planning with simulator:
```bash
source devel/setup.bash
roslaunch plan_manage topo_replan.launch
```

### FastAPI Service

Run the FastAPI service (requires ROS environment):
```bash
source devel/setup.bash
cd fastapi_planner
python3 -m fastapi_planner.main
```

Or using Docker:
```bash
docker-compose up
```

Or using the start script:
```bash
./start.sh
```

### Testing

Test FastAPI endpoints:
```bash
cd fastapi_planner
python3 test_algorithm_selection.py
python3 test_depth_endpoints.py
python3 test_error_handling.py
```

## Key Configuration Files

### ROS Launch Files

- `src/Fast-Planner/fast_planner/plan_manage/launch/kino_replan.launch` - Kinodynamic planning configuration
- `src/Fast-Planner/fast_planner/plan_manage/launch/topo_replan.launch` - Topological planning configuration
- `src/Fast-Planner/fast_planner/plan_manage/launch/kino_algorithm.xml` - Kinodynamic algorithm parameters
- `src/Fast-Planner/fast_planner/plan_manage/launch/topo_algorithm.xml` - Topological algorithm parameters

Important launch parameters:
- `map_size_x/y/z`: Map boundaries (default: 40x20x5 meters)
- `odom_topic`: Odometry topic (default: `/state_ukf/odom`)
- `max_vel`: Maximum velocity (default: 3.0 m/s)
- `max_acc`: Maximum acceleration (default: 2.0-2.5 m/s²)
- `flight_type`: 1=manual goal selection, 2=waypoint following

### FastAPI Configuration

- `fastapi_planner/config.yaml` - Main configuration file
- `fastapi_planner/.env` - Environment variables (ROS_MASTER_URI, etc.)

Key config sections:
- `ros.topics`: ROS topic mappings
- `planning`: Velocity/acceleration limits, timeouts
- `depth`: Depth image processing parameters
- `service`: API host/port, CORS settings

## Important ROS Topics

### Subscribed Topics
- `/state_ukf/odom` (nav_msgs/Odometry) - Robot odometry
- `/pcl_render_node/depth` (sensor_msgs/Image) - Depth images
- `/pcl_render_node/camera_pose` (geometry_msgs/PoseStamped) - Camera pose
- `/pcl_render_node/cloud` (sensor_msgs/PointCloud2) - Point cloud input

### Published Topics
- `/move_base_simple/goal` (geometry_msgs/PoseStamped) - Planning goal
- `/planning/bspline` (plan_manage/Bspline) - Planned trajectory
- `/planning/pos_cmd` - Position commands
- `/depth_cloud` (sensor_msgs/PointCloud2) - Processed depth point cloud

## Development Workflow

### Modifying ROS Planning Code

1. Edit C++ files in `src/Fast-Planner/fast_planner/`
2. Rebuild: `catkin_make`
3. Source workspace: `source devel/setup.bash`
4. Test with launch files

### Modifying FastAPI Service

1. Edit Python files in `fastapi_planner/`
2. No rebuild needed (Python is interpreted)
3. Restart service: `python3 -m fastapi_planner.main`
4. API docs available at: `http://localhost:8000/docs`

### Docker Development

The project includes Docker support:
- `Dockerfile.dev` - Development container with ROS Noetic + Python
- `docker-compose.yml` - Service orchestration
- Volumes mount source code for live editing

## Dependencies

### ROS Dependencies
- ROS Noetic (Ubuntu 20.04) or Melodic (Ubuntu 18.04)
- NLopt v2.7.1 (non-linear optimization)
- Armadillo (linear algebra)
- Eigen3
- PCL (Point Cloud Library)

### Python Dependencies
See `fastapi_planner/requirements.txt`:
- fastapi
- uvicorn
- rospy
- pydantic
- numpy
- opencv-python

## Planning Algorithms

### Kinodynamic Planning
- Uses kinodynamic A* for initial path (respects dynamics)
- B-spline optimization for smoothness and clearance
- Suitable for fast, aggressive flight
- Launch: `roslaunch plan_manage kino_replan.launch`

### Topological Planning
- Samples multiple topologically distinct paths
- Path-guided optimization avoids local minima
- Better for complex environments with multiple routes
- Launch: `roslaunch plan_manage topo_replan.launch`

## Coordinate Frames

- **World Frame**: Fixed global frame
- **Body Frame**: UAV body frame
- **Camera Frame**: Depth camera frame (requires camera_pose transform)
- Default camera intrinsics in launch files: cx=321.05, cy=243.45, fx=fy=387.23

## Common Issues

### ROS Build Issues
- Ensure NLopt v2.7.1 is installed (not v2.7.0 or v2.8+)
- Check Eigen3 version compatibility
- Source ROS setup: `source /opt/ros/noetic/setup.bash`

### FastAPI Service Issues
- Verify ROS_MASTER_URI is set correctly
- Check ROS topics exist: `rostopic list`
- Ensure Fast-Planner nodes are running
- Check logs in `fastapi_planner/` for detailed errors

### Planning Failures
- Verify odometry is publishing
- Check map boundaries in launch files
- Ensure goal is within map bounds and collision-free
- Adjust max_vel/max_acc if planning fails

## File Naming Conventions

- ROS C++ headers: `snake_case.h`
- ROS C++ source: `snake_case.cpp`
- Python modules: `snake_case.py`
- Launch files: `snake_case.launch` or `.xml`
- Config files: `snake_case.yaml`
