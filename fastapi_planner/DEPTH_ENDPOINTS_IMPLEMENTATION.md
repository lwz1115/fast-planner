# Depth Image API Endpoints Implementation

## Overview

This document describes the implementation of the depth image processing API endpoints for the FastAPI-Fast-Planner Interface. These endpoints allow clients to upload depth images which are converted to 3D point clouds and published to ROS for map updates.

## Implemented Endpoints

### 1. POST /map/depth

**Purpose**: Process a single depth image and publish the resulting point cloud to ROS.

**Request Body**: `DepthImageRequest`
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

**Response**: `DepthProcessingResult`
```json
{
  "success": true,
  "points_generated": 15234,
  "processing_time_ms": 125.3,
  "timestamp": 1234567890.123,
  "message": "Depth image processed and point cloud published successfully"
}
```

**Status Codes**:
- 200: Success
- 400: Invalid depth image or parameters
- 503: ROS publishing failed

**Processing Pipeline**:
1. Decode base64 encoded depth image
2. Convert depth pixels to 3D points using camera intrinsics
3. Transform points from camera frame to map frame
4. Filter points outside map boundaries
5. Downsample point cloud using voxel grid
6. Publish to ROS topic `/depth_cloud`

### 2. POST /map/depth/batch

**Purpose**: Process multiple depth images in a single request.

**Request Body**: `DepthImageBatchRequest`
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

**Response**: `DepthBatchResponse`
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
      "processing_time_ms": 125.3,
      "error": null
    },
    {
      "index": 1,
      "success": true,
      "points_generated": 14892,
      "processing_time_ms": 118.7,
      "error": null
    }
  ],
  "total_processing_time_ms": 244.0
}
```

**Status Codes**:
- 200: Success (even if some images fail)
- 400: Invalid batch request
- 503: Service unavailable

**Features**:
- Processes up to 10 images per batch
- Continues processing even if individual images fail
- Returns detailed results for each image
- Aggregates success/failure counts

## Implementation Details

### Components Modified

1. **main.py**
   - Added imports for depth processing models and DepthProcessor
   - Added global `depth_processor` instance
   - Initialized DepthProcessor in startup lifespan
   - Implemented `/map/depth` endpoint
   - Implemented `/map/depth/batch` endpoint

2. **depth_processor.py**
   - Fixed import to use relative imports instead of absolute

### Integration with Existing System

The depth endpoints integrate seamlessly with the existing FastAPI-Fast-Planner Interface:

- **ROS Bridge**: Uses existing `publish_point_cloud()` method to publish point clouds
- **Configuration**: Uses existing map boundaries from config for filtering
- **Logging**: Uses existing logging infrastructure with request IDs
- **Error Handling**: Follows existing error handling patterns
- **Middleware**: Benefits from existing logging and CORS middleware

### Error Handling

Both endpoints implement comprehensive error handling:

1. **Validation Errors (400)**:
   - Invalid base64 encoding
   - Dimension mismatch between image and camera parameters
   - Invalid camera parameters
   - Out of range depth values

2. **Service Errors (503)**:
   - ROS connection lost
   - Point cloud publishing failed
   - Service not initialized

3. **Internal Errors (500)**:
   - Unexpected exceptions during processing

### Logging

All operations are logged with appropriate detail:
- Request received with parameters
- Processing steps and metrics
- Success/failure with point counts and timing
- Errors with full context

### Performance Considerations

- **Downsampling**: Voxel grid downsampling reduces point cloud size
- **Map Filtering**: Points outside map boundaries are filtered early
- **Batch Processing**: Sequential processing with individual error handling
- **Timing Metrics**: All operations include timing information

## Testing

A verification script `test_depth_endpoints.py` has been created to validate:
- Model imports
- Model validation
- DepthProcessor initialization
- Endpoint structure

All tests pass successfully.

## Requirements Satisfied

### Task 20.1 - POST /map/depth endpoint
✅ Accept DepthImageRequest in request body
✅ Validate request parameters
✅ Call DepthProcessor to convert depth image to point cloud
✅ Publish point cloud via ROS Bridge
✅ Return DepthProcessingResult with success status and metrics
✅ Handle and return appropriate error responses (400, 503)

### Task 20.2 - POST /map/depth/batch endpoint
✅ Accept DepthImageBatchRequest with multiple depth images
✅ Validate batch size does not exceed maximum (10 images)
✅ Process each depth image sequentially
✅ Continue processing on individual failures
✅ Collect results for each image in batch
✅ Return DepthBatchResponse with aggregated results

## Usage Example

### Single Depth Image

```python
import requests
import base64

# Read depth image
with open('depth_image.png', 'rb') as f:
    depth_data = base64.b64encode(f.read()).decode('utf-8')

# Prepare request
request = {
    "depth_image": depth_data,
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
    "encoding": "16UC1"
}

# Send request
response = requests.post('http://localhost:8000/map/depth', json=request)
result = response.json()

print(f"Success: {result['success']}")
print(f"Points generated: {result['points_generated']}")
print(f"Processing time: {result['processing_time_ms']}ms")
```

### Batch Processing

```python
import requests
import base64

# Prepare batch request with multiple images
batch_request = {
    "depth_images": [
        {
            "depth_image": depth_data_1,
            "camera_intrinsics": {...},
            "camera_pose": {...},
            "depth_scale": 0.001,
            "timestamp": 1234567890.123
        },
        {
            "depth_image": depth_data_2,
            "camera_intrinsics": {...},
            "camera_pose": {...},
            "depth_scale": 0.001,
            "timestamp": 1234567890.223
        }
    ]
}

# Send batch request
response = requests.post('http://localhost:8000/map/depth/batch', json=batch_request)
result = response.json()

print(f"Total images: {result['total_images']}")
print(f"Successful: {result['successful']}")
print(f"Failed: {result['failed']}")
print(f"Total time: {result['total_processing_time_ms']}ms")

# Check individual results
for r in result['results']:
    print(f"Image {r['index']}: {r['success']} - {r['points_generated']} points")
```

## Next Steps

The following tasks remain to complete the depth processing feature:

- Task 21: Update configuration for depth processing parameters
- Task 22: Add custom error handling for depth processing
- Task 23: Write unit tests for depth processing (optional)
- Task 24: Write integration tests for depth endpoints (optional)
- Task 25: Update documentation for depth processing

## Conclusion

The depth image API endpoints have been successfully implemented and integrated into the FastAPI-Fast-Planner Interface. The implementation follows the existing patterns and conventions, provides comprehensive error handling, and includes detailed logging for debugging and monitoring.
