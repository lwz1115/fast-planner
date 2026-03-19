# Logging and Monitoring

This document describes the logging and monitoring capabilities of the FastAPI-Fast-Planner Interface.

## Overview

The service implements comprehensive logging and monitoring to support:
- **Request/Response Tracking**: Every request is logged with timing information
- **Performance Monitoring**: Planning times and success rates are tracked
- **Error Tracking**: All errors are logged with stack traces
- **Structured Logging**: Consistent log format with request correlation

## Logging Configuration

### Log Levels

The service supports standard Python logging levels:
- `DEBUG`: Detailed diagnostic information
- `INFO`: General informational messages (default)
- `WARNING`: Warning messages for potential issues
- `ERROR`: Error messages for failures
- `CRITICAL`: Critical errors requiring immediate attention

Configure the log level in `config.yaml`:

```yaml
service:
  log_level: "info"  # debug, info, warning, error, critical
```

Or via environment variable:
```bash
export LOG_LEVEL=debug
```

### Log Format

All logs follow a structured format:

```
YYYY-MM-DD HH:MM:SS - [request_id] - module_name - LEVEL - [file:line] - message | extra_fields
```

Example:
```
2025-11-11 10:30:45 - [abc123] - main - INFO - [main.py:234] - Planning completed successfully: 52 waypoints, planning_time=45.30ms, total_time=52.70ms | success=True, num_waypoints=52, algorithm=kinodynamic
```

### Request Correlation

Each request is assigned a unique request ID (8-character UUID) that appears in all related log entries. This enables tracing a request through the entire system.

The request ID is also returned in response headers:
- `X-Request-ID`: The unique request identifier
- `X-Process-Time-MS`: Total processing time in milliseconds

## Request/Response Logging

### Incoming Requests

Every incoming request is logged with:
- Request ID
- HTTP method and path
- Client IP address
- Query parameters

Example:
```
2025-11-11 10:30:45 - [abc123] - main - INFO - Incoming request: POST /plan | method=POST, path=/plan, client=192.168.1.100
```

### Responses

Every response is logged with:
- Request ID
- HTTP status code
- Processing time in milliseconds

Example:
```
2025-11-11 10:30:45 - [abc123] - main - INFO - Response: 200 (took 52.70ms) | status_code=200, process_time_ms=52.70
```

## Planning Performance Logging

### Planning Requests

Each planning request logs:
- Start and goal positions
- Planning parameters (velocity, acceleration, algorithm)
- Whether current odometry is used

Example:
```
2025-11-11 10:30:45 - [abc123] - main - INFO - Planning request received | start={'x': 0.0, 'y': 0.0, 'z': 1.0}, goal={'x': 10.0, 'y': 5.0, 'z': 1.5}, algorithm=kinodynamic
```

### Planning Results

Successful planning logs include:
- Number of waypoints
- Trajectory duration
- Planning time (ROS and total)
- Success rate

Example:
```
2025-11-11 10:30:45 - [abc123] - planning_client - INFO - Planning succeeded: 52 waypoints, duration=5.20s, planning_time=45.3ms, total_time=52.7ms | num_waypoints=52, trajectory_duration=5.2, planning_time_ms=45.3, ros_planning_time_ms=38.1, total_time_ms=52.7, success_rate=0.95
```

## Error Logging

### Error Categories

All errors are logged with appropriate severity:

1. **Validation Errors (400)**: Logged as WARNING
   - Invalid request parameters
   - Out-of-bounds positions
   - Invalid algorithm selection

2. **Planning Failures (422)**: Logged as WARNING
   - No path found
   - Start/goal in collision
   - Trajectory optimization failed

3. **Service Errors (503)**: Logged as ERROR
   - ROS connection lost
   - Odometry unavailable
   - Fast-Planner not responding

4. **Timeout Errors (504)**: Logged as WARNING
   - Planning timeout exceeded

5. **Internal Errors (500)**: Logged as ERROR with stack trace

### Stack Traces

Internal errors and unexpected exceptions include full stack traces:

```
2025-11-11 10:30:45 - [abc123] - main - ERROR - Unexpected error on /plan: ValueError: Invalid trajectory | error_code=internal_error, exception_type=ValueError
Traceback (most recent call last):
  File "main.py", line 234, in plan_trajectory
    ...
ValueError: Invalid trajectory
```

## Performance Metrics

### Metrics Endpoint

The `/metrics` endpoint provides real-time performance statistics:

```bash
curl http://localhost:8000/metrics
```

Response:
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

### Performance Logger

The `PerformanceLogger` class provides convenient methods for logging metrics:

```python
from fastapi_planner.logging_config import PerformanceLogger, get_logger

logger = get_logger(__name__)
perf_logger = PerformanceLogger(logger)

# Log timing
perf_logger.log_timing("planning", 45.3, success=True, algorithm="kinodynamic")

# Log rates
perf_logger.log_rate("success_rate", 95, 100)

# Log counters
perf_logger.log_counter("request_count", 42)
```

## Health Monitoring

### Health Endpoint

The `/health` endpoint provides service health status:

```bash
curl http://localhost:8000/health
```

Response:
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

Health status values:
- `healthy`: ROS connected and Fast-Planner available
- `degraded`: ROS connected but Fast-Planner not responding
- `unhealthy`: ROS connection lost

## Monitoring Best Practices

### Log Analysis

Use structured log fields for filtering and analysis:

```bash
# Filter by request ID
grep "abc123" service.log

# Filter by error code
grep "error_code=no_path_found" service.log

# Filter by planning time
grep "planning_time_ms" service.log | grep -E "planning_time_ms=[0-9]{3,}"
```

### Performance Monitoring

Monitor these key metrics:
- **Success Rate**: Should be > 90% in normal operation
- **Planning Time**: Should be < 100ms for most requests
- **Odometry Age**: Should be < 100ms when quadrotor is active
- **Uptime**: Track service restarts

### Alerting

Set up alerts for:
- Success rate drops below 80%
- Planning time exceeds 500ms consistently
- ROS connection lost (status = unhealthy)
- High error rate (> 10% of requests)

## Log Rotation

For production deployments, configure log rotation to prevent disk space issues:

```bash
# Using logrotate
/var/log/fastapi-planner/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 app app
}
```

## Integration with Monitoring Tools

### Prometheus

Export metrics to Prometheus using the `/metrics` endpoint with a custom exporter.

### ELK Stack

Ship logs to Elasticsearch for centralized logging and analysis:

```bash
# Using Filebeat
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/fastapi-planner/*.log
  json.keys_under_root: true
  json.add_error_key: true
```

### Grafana

Create dashboards to visualize:
- Request rate over time
- Success rate trends
- Planning time distribution
- Error rate by type

## Troubleshooting

### High Planning Times

Check logs for:
```bash
grep "planning_time_ms" service.log | awk '{print $NF}' | sort -n | tail -20
```

### Frequent Failures

Analyze error codes:
```bash
grep "error_code" service.log | cut -d'=' -f2 | cut -d',' -f1 | sort | uniq -c | sort -rn
```

### ROS Connection Issues

Monitor ROS connection status:
```bash
grep "ros_connected" service.log | tail -20
```

## Requirements

This logging and monitoring implementation satisfies:
- **Requirement 8.5**: Structured logging with appropriate log levels
- Request/response logging for debugging
- Planning time logging for performance monitoring
- Error logging with stack traces
