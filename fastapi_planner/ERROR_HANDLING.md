# Error Handling Documentation

This document describes the error handling implementation for the FastAPI-Fast-Planner Interface.

## Overview

The error handling system provides comprehensive, structured error responses for all failure scenarios. It maps Python exceptions to appropriate HTTP status codes and returns consistent error information to clients.

## Architecture

The error handling system consists of three main components:

1. **Custom Exception Classes** (`exceptions.py`): Define specific exception types for different error scenarios
2. **Exception Handlers** (`error_handlers.py`): Convert exceptions to HTTP responses with proper status codes
3. **Error Response Model** (`models.py`): Standardized error information structure

## Error Categories

### 1. Validation Errors (400 Bad Request)

**Status Code:** 400

**When Used:** Request parameters are invalid, out of bounds, or fail validation checks

**Exception Classes:**
- `ValidationException`: Base class for validation errors
- `PositionOutOfBoundsException`: Start or goal position outside map boundaries
- `InvalidAlgorithmException`: Unsupported algorithm specified

**Example Response:**
```json
{
  "code": "start_out_of_bounds",
  "message": "Start position is outside map boundaries",
  "details": "Map bounds: X=[0, 40], Y=[0, 20], Z=[0, 5]"
}
```

### 2. Planning Failures (422 Unprocessable Entity)

**Status Code:** 422

**When Used:** Fast-Planner cannot complete the planning request

**Exception Classes:**
- `PlanningFailureException`: Base class for planning failures
- `NoPathFoundException`: No collision-free path found to goal
- `GoalInCollisionException`: Goal position collides with obstacles
- `StartInCollisionException`: Start position collides with obstacles

**Example Response:**
```json
{
  "code": "no_path_found",
  "message": "Fast-Planner could not find a collision-free path to the goal",
  "details": "Goal position may be unreachable or surrounded by obstacles"
}
```

### 3. Service Unavailable (503 Service Unavailable)

**Status Code:** 503

**When Used:** Required services or data are not available

**Exception Classes:**
- `ServiceUnavailableException`: Base class for service unavailability
- `OdometryUnavailableException`: Odometry data not available or too old
- `ROSConnectionException`: ROS connection lost or unavailable

**Example Response:**
```json
{
  "code": "odometry_unavailable",
  "message": "No recent odometry data available",
  "details": "Odometry data is either not being published or is too old (>1 second)"
}
```

### 4. Timeout Errors (504 Gateway Timeout)

**Status Code:** 504

**When Used:** Operations exceed configured timeout periods

**Exception Classes:**
- `TimeoutException`: Base class for timeout errors
- `PlanningTimeoutException`: Planning operation timed out

**Example Response:**
```json
{
  "code": "planning_timeout",
  "message": "Planning timed out after 5.0 seconds",
  "details": "Fast-Planner did not return a trajectory within the timeout period. The goal may be unreachable or the planner is overloaded."
}
```

## Error Response Format

All error responses follow the `ErrorInfo` model structure:

```python
{
  "code": str,      # Machine-readable error code
  "message": str,   # Human-readable error message
  "details": str    # Additional error context (optional)
}
```

## Logging

All errors are logged with appropriate severity levels:

- **WARNING**: Expected errors (validation, planning failures, timeouts)
- **ERROR**: Unexpected errors, service unavailability, internal errors

Log entries include:
- Error code
- Error message
- Request path
- Additional context (details, stack traces for unexpected errors)

Example log entry:
```
2025-11-11 10:30:15,123 - fastapi_planner.error_handlers - WARNING - Planning failure: no_path_found - Fast-Planner could not find a collision-free path to the goal
```

## Usage Examples

### Raising Exceptions in Code

```python
from fastapi_planner.exceptions import (
    NoPathFoundException,
    PositionOutOfBoundsException,
    PlanningTimeoutException
)

# Raise specific exception
if not path_found:
    raise NoPathFoundException(
        details="Goal may be surrounded by obstacles"
    )

# Raise with custom details
if position_out_of_bounds:
    raise PositionOutOfBoundsException(
        position_type="goal",
        bounds_info="X=[0, 40], Y=[0, 20], Z=[0, 5]"
    )

# Raise timeout exception
if timeout_occurred:
    raise PlanningTimeoutException(
        timeout_seconds=5.0,
        details="Planner may be overloaded"
    )
```

### Handling Errors in Client Code

```python
import requests

response = requests.post(
    "http://localhost:8000/plan",
    json={
        "start": {"x": 0, "y": 0, "z": 1},
        "goal": {"x": 100, "y": 0, "z": 1}  # Out of bounds
    }
)

if response.status_code == 400:
    error = response.json()
    print(f"Validation error: {error['message']}")
    print(f"Details: {error['details']}")
elif response.status_code == 422:
    error = response.json()
    print(f"Planning failed: {error['message']}")
elif response.status_code == 503:
    error = response.json()
    print(f"Service unavailable: {error['message']}")
elif response.status_code == 504:
    error = response.json()
    print(f"Timeout: {error['message']}")
```

## Exception Handler Registration

Exception handlers are automatically registered during application startup:

```python
from fastapi_planner.error_handlers import register_exception_handlers

app = FastAPI()
register_exception_handlers(app)
```

This registers handlers for:
- Custom exception classes (ValidationException, PlanningFailureException, etc.)
- Standard Python exceptions (ValueError, Exception)
- Pydantic validation errors (RequestValidationError, ValidationError)

## Testing

The error handling system includes comprehensive tests in `test_error_handling.py`:

```bash
cd fastapi_planner
python test_error_handling.py
```

Tests verify:
- Exception classes have correct status codes
- Error responses include all required fields
- ErrorInfo model serialization works correctly

## Requirements Coverage

This implementation satisfies the following requirements:

- **3.1**: No path found errors return 422 with "no_path_found" code
- **3.2**: Goal collision errors return 422 with "goal_in_collision" code
- **3.3**: Start collision errors return 422 with "start_in_collision" code
- **3.4**: Timeout errors return 504 with "planning_timeout" code
- **3.5**: All error responses include descriptive messages and details

## Best Practices

1. **Use Specific Exceptions**: Prefer specific exception classes (e.g., `NoPathFoundException`) over generic ones
2. **Include Details**: Always provide helpful details in exception messages
3. **Log Before Raising**: Log error context before raising exceptions for debugging
4. **Don't Catch and Re-raise**: Let exception handlers convert exceptions to responses
5. **Test Error Paths**: Ensure error scenarios are covered by tests

## Future Enhancements

Potential improvements to the error handling system:

1. **Error Codes Enum**: Define error codes as constants to prevent typos
2. **Localization**: Support multiple languages for error messages
3. **Error Metrics**: Track error rates and types for monitoring
4. **Retry Hints**: Include retry-after headers for transient errors
5. **Error Documentation**: Auto-generate error code documentation from exception classes
