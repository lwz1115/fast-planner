# Depth Processing Error Handling Implementation

## Overview

This document describes the error handling implementation for depth image processing in the FastAPI-Fast-Planner Interface.

## Custom Exceptions

### 1. DepthProcessingException (Base Class)
- **Status Code**: 400 (Bad Request)
- **Purpose**: Base exception for all depth processing validation errors
- **Requirements**: 12.4

### 2. InvalidDepthImageException
- **Status Code**: 400 (Bad Request)
- **Error Code**: `invalid_depth_image`
- **Raised When**:
  - Base64 decoding fails
  - Image data is corrupted or invalid
  - Image format cannot be parsed
- **Example**:
  ```python
  raise InvalidDepthImageException(details="Failed to decode base64 image data")
  ```

### 3. DepthImageDimensionMismatchException
- **Status Code**: 400 (Bad Request)
- **Error Code**: `dimension_mismatch`
- **Raised When**:
  - Depth image dimensions don't match camera intrinsics
  - Decoded image size doesn't match expected size
- **Example**:
  ```python
  raise DepthImageDimensionMismatchException(
      expected_dims="640x480",
      actual_dims="320x240"
  )
  ```

### 4. InvalidDepthEncodingException
- **Status Code**: 400 (Bad Request)
- **Error Code**: `invalid_encoding`
- **Raised When**:
  - Unsupported depth encoding format is specified
  - Only "16UC1" and "32FC1" are supported
- **Example**:
  ```python
  raise InvalidDepthEncodingException(encoding="INVALID")
  ```

### 5. ROSPublishFailedException
- **Status Code**: 503 (Service Unavailable)
- **Error Code**: `ros_publish_failed`
- **Raised When**:
  - Point cloud publishing to ROS topic fails
  - ROS connection is unavailable during publishing
- **Requirements**: 12.5
- **Example**:
  ```python
  raise ROSPublishFailedException(details="Failed to publish 15234 points to ROS topic")
  ```

## Exception Handlers

### depth_processing_exception_handler
- Handles all depth processing validation errors (400)
- Logs error details with structured logging
- Returns standardized error response with ErrorInfo model

### ros_publish_failed_exception_handler
- Handles ROS publishing failures (503)
- Logs error with ROS connection context
- Returns service unavailable response

## Error Flow

### Single Depth Image Processing (/map/depth)

```
Request → Validation → Decode Image → Convert to Point Cloud → Transform → Downsample → Publish to ROS
                ↓            ↓                    ↓                 ↓            ↓              ↓
         ValidationError  InvalidDepth    DimensionMismatch   InvalidDepth  InvalidDepth  ROSPublishFailed
                          ImageException      Exception       ImageException ImageException  Exception
                                ↓                    ↓                 ↓            ↓              ↓
                          400 Response         400 Response      400 Response 400 Response  503 Response
```

### Batch Processing (/map/depth/batch)

- Each image is processed independently
- Errors in one image don't stop processing of others
- Individual errors are captured in DepthBatchResult
- Batch continues even if some images fail
- Final response includes success/failure counts and individual results

## Logging

All depth processing errors are logged with:
- **Error Level**: ERROR for validation errors, CRITICAL for unexpected errors
- **Structured Fields**:
  - `error_code`: Machine-readable error code
  - `path`: API endpoint path
  - `details`: Additional error context
  - `request_id`: Request correlation ID
  - `image_index`: For batch processing

### Example Log Output

```
ERROR:depth_processor:Depth image decoding failed: Image data size mismatch for 16UC1 encoding. Expected 614400 bytes for 640x480, got 100 bytes
ERROR:error_handlers:Depth processing error: invalid_depth_image - Invalid depth image format
```

## Error Response Format

All depth processing errors return a standardized JSON response:

```json
{
  "code": "invalid_depth_image",
  "message": "Invalid depth image format",
  "details": "Image data size mismatch for 16UC1 encoding. Expected 614400 bytes for 640x480, got 100 bytes"
}
```

## Testing

A comprehensive test suite (`test_depth_error_handling.py`) verifies:
1. All exceptions can be imported
2. Exceptions have correct status codes and error codes
3. Exception handlers are properly registered
4. Depth processor raises appropriate exceptions
5. Main.py imports and uses the exceptions correctly

Run tests with:
```bash
python3 fastapi_planner/test_depth_error_handling.py
```

## Integration with FastAPI

Exception handlers are registered in `error_handlers.py`:
```python
def register_exception_handlers(app):
    # Depth processing handlers (must be before ValidationException)
    app.add_exception_handler(DepthProcessingException, depth_processing_exception_handler)
    app.add_exception_handler(InvalidDepthImageException, depth_processing_exception_handler)
    app.add_exception_handler(DepthImageDimensionMismatchException, depth_processing_exception_handler)
    app.add_exception_handler(InvalidDepthEncodingException, depth_processing_exception_handler)
    app.add_exception_handler(ROSPublishFailedException, ros_publish_failed_exception_handler)
    # ... other handlers
```

## Requirements Coverage

- **Requirement 12.4**: Invalid depth image format handling ✓
- **Requirement 12.5**: ROS publishing failure handling ✓

All depth processing errors are properly caught, logged, and returned with appropriate HTTP status codes and error messages.
