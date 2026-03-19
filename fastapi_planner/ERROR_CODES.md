# Error Codes Quick Reference

This document provides a quick reference for all error codes returned by the FastAPI-Fast-Planner Interface.

## Error Code Format

All error responses follow this structure:
```json
{
  "code": "error_code",
  "message": "Human-readable message",
  "details": "Additional context (optional)"
}
```

## Validation Errors (400)

| Code | Message | When It Occurs |
|------|---------|----------------|
| `validation_error` | Invalid request parameters | Request body fails Pydantic validation |
| `value_error` | Invalid value in request | Value passes validation but fails business logic |
| `start_out_of_bounds` | Start position is outside map boundaries | Start position exceeds configured map limits |
| `goal_out_of_bounds` | Goal position is outside map boundaries | Goal position exceeds configured map limits |
| `invalid_algorithm` | Unsupported algorithm: {name} | Algorithm parameter is not "kinodynamic" or "topological" |

## Planning Failures (422)

| Code | Message | When It Occurs |
|------|---------|----------------|
| `no_path_found` | Fast-Planner could not find a collision-free path to the goal | No valid trajectory exists to reach the goal |
| `goal_in_collision` | Goal position is in collision with obstacles | Goal position overlaps with an obstacle |
| `start_in_collision` | Start position is in collision with obstacles | Start position overlaps with an obstacle |
| `trajectory_conversion_error` | Failed to convert B-spline trajectory to waypoints | Error during B-spline evaluation |
| `trajectory_validation_error` | Generated trajectory failed validation | Trajectory doesn't meet requirements |
| `no_trajectory_received` | No trajectory received from Fast-Planner | Fast-Planner didn't respond with a trajectory |

## Service Unavailable (503)

| Code | Message | When It Occurs |
|------|---------|----------------|
| `service_not_initialized` | Planning service is not initialized | Service is still starting up |
| `ros_disconnected` | ROS connection is not available | ROS Master is unreachable |
| `odometry_unavailable` | No recent odometry data available | Odometry topic not publishing or data too old |
| `ros_communication_error` | Failed to publish goal to Fast-Planner | Cannot send messages to ROS |

## Timeout Errors (504)

| Code | Message | When It Occurs |
|------|---------|----------------|
| `planning_timeout` | Planning timed out after {N} seconds | Fast-Planner didn't respond within timeout period |

## Internal Errors (500)

| Code | Message | When It Occurs |
|------|---------|----------------|
| `internal_error` | An unexpected error occurred | Unhandled exception in service code |

## Usage Examples

### Handling Specific Error Codes

```python
import requests

response = requests.post("http://localhost:8000/plan", json={...})

if response.status_code != 200:
    error = response.json()
    code = error["code"]
    
    if code == "no_path_found":
        print("Cannot reach goal - try a different position")
    elif code == "planning_timeout":
        print("Planning took too long - try a closer goal")
    elif code == "start_out_of_bounds":
        print("Start position is outside the map")
    elif code == "odometry_unavailable":
        print("Waiting for odometry data...")
    else:
        print(f"Error: {error['message']}")
```

### Retry Logic Based on Error Type

```python
def should_retry(error_code: str) -> bool:
    """Determine if request should be retried based on error code."""
    
    # Retry transient errors
    transient_errors = [
        "odometry_unavailable",
        "ros_communication_error",
        "service_not_initialized"
    ]
    
    # Don't retry permanent failures
    permanent_errors = [
        "start_out_of_bounds",
        "goal_out_of_bounds",
        "invalid_algorithm",
        "goal_in_collision",
        "start_in_collision"
    ]
    
    if error_code in transient_errors:
        return True
    elif error_code in permanent_errors:
        return False
    else:
        # Retry other errors with caution
        return True
```

### Error Code Categories

```python
VALIDATION_ERRORS = [
    "validation_error",
    "value_error",
    "start_out_of_bounds",
    "goal_out_of_bounds",
    "invalid_algorithm"
]

PLANNING_ERRORS = [
    "no_path_found",
    "goal_in_collision",
    "start_in_collision",
    "trajectory_conversion_error",
    "trajectory_validation_error",
    "no_trajectory_received"
]

SERVICE_ERRORS = [
    "service_not_initialized",
    "ros_disconnected",
    "odometry_unavailable",
    "ros_communication_error"
]

TIMEOUT_ERRORS = [
    "planning_timeout"
]

INTERNAL_ERRORS = [
    "internal_error"
]
```

## Common Scenarios

### Scenario 1: Position Out of Bounds

**Request:**
```json
{
  "start": {"x": 0, "y": 0, "z": 1},
  "goal": {"x": 100, "y": 0, "z": 1}
}
```

**Response (400):**
```json
{
  "code": "goal_out_of_bounds",
  "message": "Goal position is outside map boundaries",
  "details": "Map bounds: X=[0, 40], Y=[0, 20], Z=[0, 5]"
}
```

**Solution:** Adjust goal position to be within map boundaries.

### Scenario 2: No Path Found

**Request:**
```json
{
  "start": {"x": 0, "y": 0, "z": 1},
  "goal": {"x": 20, "y": 10, "z": 1}
}
```

**Response (422):**
```json
{
  "code": "no_path_found",
  "message": "Fast-Planner could not find a collision-free path to the goal",
  "details": "Goal position may be unreachable or surrounded by obstacles"
}
```

**Solution:** Try a different goal position or check for obstacles blocking the path.

### Scenario 3: Planning Timeout

**Request:**
```json
{
  "start": {"x": 0, "y": 0, "z": 1},
  "goal": {"x": 30, "y": 15, "z": 3}
}
```

**Response (504):**
```json
{
  "code": "planning_timeout",
  "message": "Planning timed out after 5.0 seconds",
  "details": "Fast-Planner did not return a trajectory within the timeout period. The goal may be unreachable or the planner is overloaded."
}
```

**Solution:** Try a closer goal, increase timeout in config, or check if planner is overloaded.

### Scenario 4: Odometry Unavailable

**Request:**
```json
{
  "start": {"x": 0, "y": 0, "z": 1},
  "goal": {"x": 10, "y": 5, "z": 1},
  "use_current_odom": true
}
```

**Response (503):**
```json
{
  "code": "odometry_unavailable",
  "message": "No recent odometry data available",
  "details": "Cannot use current odometry as start position"
}
```

**Solution:** Wait for odometry data to be published or don't use `use_current_odom` flag.

## Best Practices

1. **Check Status Code First**: Use HTTP status code to determine error category
2. **Use Error Code for Logic**: Use the `code` field for programmatic error handling
3. **Show Message to Users**: Display the `message` field to end users
4. **Log Details**: Log the `details` field for debugging
5. **Implement Retry Logic**: Retry transient errors (503) but not permanent failures (400, 422)
6. **Monitor Error Rates**: Track error codes to identify system issues

## See Also

- `ERROR_HANDLING.md` - Comprehensive error handling documentation
- `exceptions.py` - Exception class definitions
- `error_handlers.py` - Exception handler implementations
