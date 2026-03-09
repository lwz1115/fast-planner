# API Reference

Complete API reference for the FastAPI-Fast-Planner Interface.

## Base URL

```
http://localhost:8000
```

Replace `localhost:8000` with your service host and port.

## Authentication

Currently, the API does not require authentication. For production deployments, consider adding API key authentication or OAuth2.

## Common Headers

### Request Headers

- `Content-Type: application/json` - Required for POST requests
- `Accept: application/json` - Optional, defaults to JSON

### Response Headers

All responses include:
- `X-Request-ID` - Unique request identifier for correlation
- `X-Process-Time-MS` - Request processing time in milliseconds
- `Content-Type: application/json`

## Endpoints

### POST /plan

Plan a trajectory from start to goal position.

#### Request

**Method:** `POST`

**URL:** `/plan`

**Content-Type:** `application/json`

**Body Schema:**

```json
{
  "start": {
    "x": float,
    "y": float,
    "z": float
  },
  "goal": {
    "x": float,
    "y": float,
    "z": float
  },
  "max_velocity": float,        // Optional, default: 3.0
  "max_acceleration": float,    // Optional, default: 2.0
  "algorithm": string,          // Optional, default: "kinodynamic"
  "use_current_odom": boolean   // Optional, default: false
}
```

**Parameters:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `start` | Position | Yes | - | Starting position (x, y, z in meters) |
| `goal` | Position | Yes | - | Goal position (x, y, z in meters) |
| `max_velocity` | float | No | 3.0 | Maximum velocity in m/s (must be > 0 and ≤ max_velocity_limit) |
| `max_acceleration` | float | No | 2.0 | Maximum acceleration in m/s² (must be > 0 and ≤ max_acceleration_limit) |
| `algorithm` | string | No | "kinodynamic" | Planning algorithm: "kinodynamic" or "topological" |
| `use_current_odom` | boolean | No | false | Use current odometry as start position (ignores `start` field) |

**Validation Rules:**

- Positions must be within configured map boundaries
- `max_velocity` must be positive and ≤ `max_velocity_limit` (default 10.0 m/s)
- `max_acceleration` must be positive and ≤ `max_acceleration_limit` (default 10.0 m/s²)
- `algorithm` must be "kinodynamic" or "topological"

#### Response

**Success (200 OK):**

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
      {
        "timestamp": 0.1,
        "position": {"x": 0.05, "y": 0.02, "z": 1.0},
        "velocity": {"x": 0.5, "y": 0.2, "z": 0.0},
        "acceleration": {"x": 0.4, "y": 0.15, "z": 0.0}
      }
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

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether planning succeeded |
| `trajectory` | Trajectory | Planned trajectory (null if failed) |
| `trajectory.waypoints` | Waypoint[] | Array of trajectory waypoints |
| `trajectory.total_duration` | float | Total trajectory duration in seconds |
| `trajectory.num_waypoints` | int | Number of waypoints |
| `error` | ErrorInfo | Error information (null if succeeded) |
| `planning_time_ms` | float | Total planning time in milliseconds |
| `ros_planning_time_ms` | float | ROS planning time in milliseconds (null if failed) |
| `total_time_ms` | float | End-to-end request processing time in milliseconds |

**Waypoint Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | float | Time from trajectory start in seconds |
| `position` | Position | Position (x, y, z) in meters |
| `velocity` | Position | Velocity (x, y, z) in m/s |
| `acceleration` | Position | Acceleration (x, y, z) in m/s² |

**Error Responses:**

**400 Bad Request** - Invalid request parameters:

```json
{
  "code": "start_out_of_bounds",
  "message": "Start position is outside map boundaries",
  "details": "Map bounds: X=[0, 40], Y=[0, 20], Z=[0, 5]"
}
```

Error codes:
- `start_out_of_bounds` - Start position outside map
- `goal_out_of_bounds` - Goal position outside map
- `invalid_algorithm` - Unsupported algorithm specified
- `validation_error` - Other validation failures

**422 Unprocessable Entity** - Planning failed:

```json
{
  "code": "no_path_found",
  "message": "Fast-Planner could not find a collision-free path to the goal",
  "details": "Goal position may be unreachable or surrounded by obstacles"
}
```

Error codes:
- `no_path_found` - No collision-free path found
- `goal_in_collision` - Goal position collides with obstacles
- `start_in_collision` - Start position collides with obstacles
- `planning_failed` - Other planning failures

**503 Service Unavailable** - Service not available:

```json
{
  "code": "ros_connection_lost",
  "message": "ROS connection is not available",
  "details": "Cannot communicate with ROS Master or Fast-Planner node"
}
```

Error codes:
- `ros_connection_lost` - ROS connection unavailable
- `service_not_initialized` - Service still starting up
- `odometry_unavailable` - Odometry required but not available (when `use_current_odom: true`)

**504 Gateway Timeout** - Planning timeout:

```json
{
  "code": "planning_timeout",
  "message": "Planning timed out after 5.0 seconds",
  "details": "Fast-Planner did not return a trajectory within the timeout period"
}
```

#### Examples

**Basic Planning Request:**

```bash
curl -X POST "http://localhost:8000/plan" \
  -H "Content-Type: application/json" \
  -d '{
    "start": {"x": 0.0, "y": 0.0, "z": 1.0},
    "goal": {"x": 10.0, "y": 5.0, "z": 1.5}
  }'
```

**Planning with Custom Parameters:**

```bash
curl -X POST "http://localhost:8000/plan" \
  -H "Content-Type: application/json" \
  -d '{
    "start": {"x": 0.0, "y": 0.0, "z": 1.0},
    "goal": {"x": 10.0, "y": 5.0, "z": 1.5},
    "max_velocity": 5.0,
    "max_acceleration": 3.0,
    "algorithm": "topological"
  }'
```

**Planning from Current Position:**

```bash
curl -X POST "http://localhost:8000/plan" \
  -H "Content-Type: application/json" \
  -d '{
    "start": {"x": 0.0, "y": 0.0, "z": 0.0},
    "goal": {"x": 10.0, "y": 5.0, "z": 1.5},
    "use_current_odom": true
  }'
```

**Python Example:**

```python
import requests

response = requests.post(
    "http://localhost:8000/plan",
    json={
        "start": {"x": 0.0, "y": 0.0, "z": 1.0},
        "goal": {"x": 10.0, "y": 5.0, "z": 1.5},
        "max_velocity": 3.0,
        "max_acceleration": 2.0,
        "algorithm": "kinodynamic"
    }
)

if response.status_code == 200:
    data = response.json()
    if data["success"]:
        print(f"Planning succeeded: {data['trajectory']['num_waypoints']} waypoints")
        print(f"Planning time: {data['planning_time_ms']:.2f}ms")
    else:
        print(f"Planning failed: {data['error']['message']}")
else:
    error = response.json()
    print(f"Error {response.status_code}: {error['message']}")
```

---

### GET /odometry

Get current quadrotor odometry state.

#### Request

**Method:** `GET`

**URL:** `/odometry`

**Parameters:** None

#### Response

**Success (200 OK):**

```json
{
  "timestamp": 1699876543.123,
  "position": {
    "x": 1.2,
    "y": 0.5,
    "z": 1.0
  },
  "orientation": {
    "x": 0.0,
    "y": 0.0,
    "z": 0.0,
    "w": 1.0
  },
  "linear_velocity": {
    "x": 0.5,
    "y": 0.0,
    "z": 0.0
  },
  "angular_velocity": {
    "x": 0.0,
    "y": 0.0,
    "z": 0.1
  }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | float | Unix timestamp of odometry measurement |
| `position` | Position | Current position (x, y, z) in meters |
| `orientation` | Quaternion | Current orientation as quaternion (x, y, z, w) |
| `linear_velocity` | Position | Linear velocity (x, y, z) in m/s |
| `angular_velocity` | Position | Angular velocity (x, y, z) in rad/s |

**Error Responses:**

**503 Service Unavailable** - Odometry not available:

```json
{
  "code": "odometry_unavailable",
  "message": "No recent odometry data available",
  "details": "Odometry data is either not being published or is too old (>1 second)"
}
```

#### Examples

**cURL:**

```bash
curl "http://localhost:8000/odometry"
```

**Python:**

```python
import requests

response = requests.get("http://localhost:8000/odometry")

if response.status_code == 200:
    odom = response.json()
    print(f"Position: ({odom['position']['x']:.2f}, "
          f"{odom['position']['y']:.2f}, "
          f"{odom['position']['z']:.2f})")
    print(f"Velocity: ({odom['linear_velocity']['x']:.2f}, "
          f"{odom['linear_velocity']['y']:.2f}, "
          f"{odom['linear_velocity']['z']:.2f})")
else:
    error = response.json()
    print(f"Error: {error['message']}")
```

---

### GET /health

Get service health status.

#### Request

**Method:** `GET`

**URL:** `/health`

**Parameters:** None

#### Response

**Success (200 OK):**

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

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Overall health status: "healthy", "degraded", or "unhealthy" |
| `ros_connected` | boolean | Whether ROS connection is active |
| `fast_planner_available` | boolean | Whether Fast-Planner node is responding |
| `uptime_seconds` | float | Service uptime in seconds |
| `last_planning_success` | float | Unix timestamp of last successful planning (null if none) |
| `odometry_age_ms` | float | Age of latest odometry in milliseconds (null if unavailable) |

**Status Values:**

- `healthy` - ROS connected and Fast-Planner available
- `degraded` - ROS connected but Fast-Planner not responding
- `unhealthy` - ROS connection lost

#### Examples

**cURL:**

```bash
curl "http://localhost:8000/health"
```

**Python:**

```python
import requests

response = requests.get("http://localhost:8000/health")
health = response.json()

print(f"Status: {health['status']}")
print(f"ROS Connected: {health['ros_connected']}")
print(f"Fast-Planner Available: {health['fast_planner_available']}")
print(f"Uptime: {health['uptime_seconds']:.1f}s")

if health['status'] != 'healthy':
    print("WARNING: Service is not fully operational!")
```

---

### GET /metrics

Get performance metrics and statistics.

#### Request

**Method:** `GET`

**URL:** `/metrics`

**Parameters:** None

#### Response

**Success (200 OK):**

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

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `uptime_seconds` | float | Service uptime in seconds |
| `total_requests` | int | Total planning requests received |
| `successful_requests` | int | Number of successful planning requests |
| `failed_requests` | int | Number of failed planning requests |
| `success_rate_percent` | float | Success rate as percentage (0-100) |
| `last_planning_success` | float | Unix timestamp of last successful planning (null if none) |
| `ros_connected` | boolean | Whether ROS connection is active |

#### Examples

**cURL:**

```bash
curl "http://localhost:8000/metrics"
```

**Python:**

```python
import requests

response = requests.get("http://localhost:8000/metrics")
metrics = response.json()

print(f"Total Requests: {metrics['total_requests']}")
print(f"Success Rate: {metrics['success_rate_percent']:.2f}%")
print(f"Uptime: {metrics['uptime_seconds']:.1f}s")
```

---

### GET /

Root endpoint with service information.

#### Request

**Method:** `GET`

**URL:** `/`

**Parameters:** None

#### Response

**Success (200 OK):**

```json
{
  "service": "FastAPI-Fast-Planner Interface",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs",
  "health": "/health",
  "metrics": "/metrics"
}
```

#### Examples

**cURL:**

```bash
curl "http://localhost:8000/"
```

---

## Interactive Documentation

The service provides auto-generated interactive API documentation:

### Swagger UI

**URL:** http://localhost:8000/docs

Features:
- Interactive API explorer
- Try out endpoints directly from browser
- View request/response schemas
- See example values
- Download OpenAPI specification

### ReDoc

**URL:** http://localhost:8000/redoc

Features:
- Clean, readable documentation
- Detailed schema descriptions
- Code samples
- Search functionality

## Error Handling

All error responses follow a consistent format:

```json
{
  "code": "error_code",
  "message": "Human-readable error message",
  "details": "Additional error context (optional)"
}
```

### HTTP Status Codes

| Status Code | Meaning | When Used |
|-------------|---------|-----------|
| 200 | OK | Request succeeded |
| 400 | Bad Request | Invalid request parameters |
| 422 | Unprocessable Entity | Planning failed (no path, collision, etc.) |
| 503 | Service Unavailable | ROS or Fast-Planner unavailable |
| 504 | Gateway Timeout | Planning timeout exceeded |
| 500 | Internal Server Error | Unexpected server error |

### Common Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `start_out_of_bounds` | 400 | Start position outside map boundaries |
| `goal_out_of_bounds` | 400 | Goal position outside map boundaries |
| `invalid_algorithm` | 400 | Unsupported algorithm specified |
| `validation_error` | 400 | Request validation failed |
| `no_path_found` | 422 | No collision-free path found |
| `goal_in_collision` | 422 | Goal position collides with obstacles |
| `start_in_collision` | 422 | Start position collides with obstacles |
| `planning_failed` | 422 | Planning failed for other reasons |
| `odometry_unavailable` | 503 | Odometry data not available |
| `ros_connection_lost` | 503 | ROS connection unavailable |
| `service_not_initialized` | 503 | Service still starting up |
| `planning_timeout` | 504 | Planning exceeded timeout |
| `internal_error` | 500 | Unexpected server error |

For detailed error handling documentation, see `ERROR_HANDLING.md`.

## Rate Limiting

Currently, the API does not implement rate limiting. For production deployments, consider adding rate limiting to prevent abuse.

## CORS

Cross-Origin Resource Sharing (CORS) is configurable via `config.yaml`:

```yaml
service:
  enable_cors: true
  cors_origins:
    - "https://myapp.example.com"
    - "https://dashboard.example.com"
```

For development, use `["*"]` to allow all origins (not recommended for production).

## Versioning

The current API version is 1.0.0. Future versions may introduce breaking changes with appropriate version prefixes (e.g., `/v2/plan`).

## Support

For issues, questions, or feature requests:
- Check the troubleshooting section in `README.md`
- Review error handling documentation in `ERROR_HANDLING.md`
- Check logging and monitoring in `LOGGING_MONITORING.md`
- Review requirements and design documents in `.kiro/specs/fastapi-fast-planner-interface/`
