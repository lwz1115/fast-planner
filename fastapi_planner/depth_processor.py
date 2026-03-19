"""
Depth image processing module for FastAPI-Fast-Planner Interface.

This module handles conversion of depth images to 3D point clouds,
coordinate transformations, and point cloud filtering/downsampling.

Requirements: 9.1, 9.2, 10.1-10.5, 11.1-11.5, 13.1-13.3
"""

import base64
import logging
import time
from typing import Tuple, Optional
import numpy as np

from config import DepthConfig
from models import (
    DepthImageRequest,
    DepthProcessingResult,
    CameraIntrinsics,
    CameraPose,
    ErrorInfo
)
from exceptions import (
    InvalidDepthImageException,
    DepthImageDimensionMismatchException,
    InvalidDepthEncodingException
)


logger = logging.getLogger(__name__)


class DepthProcessor:
    """
    Processes depth images to generate 3D point clouds for map updates.
    
    This class handles:
    - Decoding base64 encoded depth images
    - Converting depth images to 3D point clouds using camera intrinsics
    - Transforming points from camera frame to map frame
    - Filtering invalid depth values and out-of-range points
    - Downsampling point clouds using voxel grid filtering
    
    Requirements: 9.1, 9.2, 10.1-10.5, 13.1-13.3
    """
    
    def __init__(self, config: DepthConfig):
        """
        Initialize the depth processor with configuration.
        
        Args:
            config: Depth processing configuration
        """
        self.config = config
        logger.info("DepthProcessor initialized")

    def decode_depth_image(
        self,
        image_data: str,
        encoding: str,
        expected_width: int,
        expected_height: int
    ) -> np.ndarray:
        """
        Decode base64 encoded depth image to numpy array.
        
        Supports two encoding formats:
        - 16UC1: 16-bit unsigned integer (typical for depth cameras)
        - 32FC1: 32-bit float (for processed depth data)
        
        Args:
            image_data: Base64 encoded image data
            encoding: Image encoding format ("16UC1" or "32FC1")
            expected_width: Expected image width in pixels
            expected_height: Expected image height in pixels
            
        Returns:
            Numpy array of depth values with shape (height, width)
            
        Raises:
            ValueError: If decoding fails or dimensions don't match
            
        Requirements: 9.2, 11.5, 12.4
        """
        try:
            # Decode base64 to bytes
            image_bytes = base64.b64decode(image_data)
            
            # Convert bytes to numpy array
            if encoding == "16UC1":
                # 16-bit unsigned integer (2 bytes per pixel)
                expected_size = expected_width * expected_height * 2
                if len(image_bytes) != expected_size:
                    error_msg = (
                        f"Image data size mismatch for 16UC1 encoding. "
                        f"Expected {expected_size} bytes for {expected_width}x{expected_height}, "
                        f"got {len(image_bytes)} bytes"
                    )
                    logger.error(f"Depth image decoding failed: {error_msg}")
                    raise InvalidDepthImageException(details=error_msg)
                
                # Decode as 16-bit unsigned integers
                depth_array = np.frombuffer(image_bytes, dtype=np.uint16)
                depth_array = depth_array.reshape((expected_height, expected_width))
                
            elif encoding == "32FC1":
                # 32-bit float (4 bytes per pixel)
                expected_size = expected_width * expected_height * 4
                if len(image_bytes) != expected_size:
                    error_msg = (
                        f"Image data size mismatch for 32FC1 encoding. "
                        f"Expected {expected_size} bytes for {expected_width}x{expected_height}, "
                        f"got {len(image_bytes)} bytes"
                    )
                    logger.error(f"Depth image decoding failed: {error_msg}")
                    raise InvalidDepthImageException(details=error_msg)
                
                # Decode as 32-bit floats
                depth_array = np.frombuffer(image_bytes, dtype=np.float32)
                depth_array = depth_array.reshape((expected_height, expected_width))
                
            else:
                logger.error(f"Unsupported encoding format: {encoding}")
                raise InvalidDepthEncodingException(encoding)
            
            # Validate dimensions
            actual_height, actual_width = depth_array.shape
            if actual_width != expected_width or actual_height != expected_height:
                logger.error(
                    f"Dimension mismatch: expected {expected_width}x{expected_height}, "
                    f"got {actual_width}x{actual_height}"
                )
                raise DepthImageDimensionMismatchException(
                    expected_dims=f"{expected_width}x{expected_height}",
                    actual_dims=f"{actual_width}x{actual_height}"
                )
            
            logger.debug(
                f"Successfully decoded {encoding} depth image: "
                f"{actual_width}x{actual_height}, "
                f"value range [{depth_array.min():.2f}, {depth_array.max():.2f}]"
            )
            
            return depth_array
            
        except base64.binascii.Error as e:
            error_msg = f"Failed to decode base64 image data: {str(e)}"
            logger.error(error_msg)
            raise InvalidDepthImageException(details=error_msg)
        except (InvalidDepthImageException, DepthImageDimensionMismatchException, InvalidDepthEncodingException):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            error_msg = f"Failed to decode depth image: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise InvalidDepthImageException(details=error_msg)

    def depth_to_pointcloud(
        self,
        depth_image: np.ndarray,
        intrinsics: CameraIntrinsics,
        depth_scale: float
    ) -> np.ndarray:
        """
        Convert depth image to 3D point cloud in camera frame.
        
        Uses the pinhole camera model to convert depth pixels to 3D points:
        X_cam = (u - cx) * depth / fx
        Y_cam = (v - cy) * depth / fy
        Z_cam = depth
        
        Args:
            depth_image: Depth image array with shape (height, width)
            intrinsics: Camera intrinsic parameters
            depth_scale: Scale factor to convert raw depth values to meters
            
        Returns:
            Numpy array of 3D points in camera frame with shape (N, 3)
            where N is the number of valid points
            
        Requirements: 10.1, 10.3, 10.4, 13.1, 13.2
        """
        height, width = depth_image.shape
        
        # Validate dimensions match intrinsics
        if width != intrinsics.width or height != intrinsics.height:
            logger.error(
                f"Depth image dimensions ({width}x{height}) do not match "
                f"camera intrinsics ({intrinsics.width}x{intrinsics.height})"
            )
            raise DepthImageDimensionMismatchException(
                expected_dims=f"{intrinsics.width}x{intrinsics.height}",
                actual_dims=f"{width}x{height}"
            )
        
        # Extract camera parameters
        fx = intrinsics.fx
        fy = intrinsics.fy
        cx = intrinsics.cx
        cy = intrinsics.cy
        
        # Create pixel coordinate grids
        u_coords, v_coords = np.meshgrid(
            np.arange(width, dtype=np.float32),
            np.arange(height, dtype=np.float32),
            indexing='xy'
        )
        
        # Convert depth values to meters
        depth_meters = depth_image.astype(np.float32) * depth_scale
        
        # Filter out invalid depth values
        # Invalid: zero, negative, NaN, or outside configured range
        valid_mask = (
            (depth_meters > 0) &
            np.isfinite(depth_meters) &
            (depth_meters >= self.config.min_depth) &
            (depth_meters <= self.config.max_depth)
        )
        
        # Count invalid points for logging
        total_pixels = width * height
        valid_pixels = np.sum(valid_mask)
        invalid_pixels = total_pixels - valid_pixels
        
        if valid_pixels == 0:
            logger.warning("No valid depth values found in image")
            return np.empty((0, 3), dtype=np.float32)
        
        # Extract valid coordinates and depths
        u_valid = u_coords[valid_mask]
        v_valid = v_coords[valid_mask]
        depth_valid = depth_meters[valid_mask]
        
        # Convert to 3D points in camera frame using pinhole camera model
        X_cam = (u_valid - cx) * depth_valid / fx
        Y_cam = (v_valid - cy) * depth_valid / fy
        Z_cam = depth_valid
        
        # Stack into Nx3 array
        points_camera = np.stack([X_cam, Y_cam, Z_cam], axis=1)
        
        logger.debug(
            f"Converted depth image to point cloud: "
            f"{valid_pixels}/{total_pixels} valid points "
            f"({100.0 * valid_pixels / total_pixels:.1f}%), "
            f"filtered {invalid_pixels} invalid points"
        )
        
        return points_camera

    def quaternion_to_rotation_matrix(self, qx: float, qy: float, qz: float, qw: float) -> np.ndarray:
        """
        Convert quaternion to 3x3 rotation matrix.
        
        Args:
            qx, qy, qz, qw: Quaternion components
            
        Returns:
            3x3 rotation matrix as numpy array
        """
        # Normalize quaternion
        norm = np.sqrt(qx**2 + qy**2 + qz**2 + qw**2)
        if norm < 1e-10:
            error_msg = "Quaternion has zero magnitude"
            logger.error(error_msg)
            raise InvalidDepthImageException(details=error_msg)
        
        qx, qy, qz, qw = qx/norm, qy/norm, qz/norm, qw/norm
        
        # Compute rotation matrix elements
        # Using formula from https://www.euclideanspace.com/maths/geometry/rotations/conversions/quaternionToMatrix/
        R = np.array([
            [1 - 2*(qy**2 + qz**2),     2*(qx*qy - qz*qw),     2*(qx*qz + qy*qw)],
            [    2*(qx*qy + qz*qw), 1 - 2*(qx**2 + qz**2),     2*(qy*qz - qx*qw)],
            [    2*(qx*qz - qy*qw),     2*(qy*qz + qx*qw), 1 - 2*(qx**2 + qy**2)]
        ], dtype=np.float32)
        
        return R
    
    def transform_pointcloud(
        self,
        points_camera: np.ndarray,
        camera_pose: CameraPose,
        map_bounds: Optional[Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]] = None
    ) -> np.ndarray:
        """
        Transform point cloud from camera frame to map frame.
        
        Applies rotation and translation to convert points from camera coordinates
        to map coordinates. Optionally filters points outside map boundaries.
        
        Args:
            points_camera: Nx3 array of points in camera frame
            camera_pose: Camera pose (position and orientation) in map frame
            map_bounds: Optional tuple of ((x_min, x_max), (y_min, y_max), (z_min, z_max))
                       for filtering points outside map boundaries
            
        Returns:
            Nx3 array of points in map frame (may have fewer points if filtered)
            
        Requirements: 10.2
        """
        if points_camera.shape[0] == 0:
            return points_camera
        
        # Extract camera pose
        position = camera_pose.position
        orientation = camera_pose.orientation
        
        # Convert quaternion to rotation matrix
        R = self.quaternion_to_rotation_matrix(
            orientation.x,
            orientation.y,
            orientation.z,
            orientation.w
        )
        
        # Apply rotation: P_map_rot = R * P_cam
        # points_camera is Nx3, R is 3x3
        # We want to compute R @ P_cam.T, then transpose back
        points_rotated = (R @ points_camera.T).T
        
        # Apply translation: P_map = P_map_rot + T
        translation = np.array([position.x, position.y, position.z], dtype=np.float32)
        points_map = points_rotated + translation
        
        # Filter points outside map boundaries if provided
        if map_bounds is not None:
            (x_min, x_max), (y_min, y_max), (z_min, z_max) = map_bounds
            
            valid_mask = (
                (points_map[:, 0] >= x_min) & (points_map[:, 0] <= x_max) &
                (points_map[:, 1] >= y_min) & (points_map[:, 1] <= y_max) &
                (points_map[:, 2] >= z_min) & (points_map[:, 2] <= z_max)
            )
            
            points_filtered = points_map[valid_mask]
            
            num_filtered = points_map.shape[0] - points_filtered.shape[0]
            if num_filtered > 0:
                logger.debug(
                    f"Filtered {num_filtered} points outside map boundaries "
                    f"({100.0 * num_filtered / points_map.shape[0]:.1f}%)"
                )
            
            return points_filtered
        
        logger.debug(f"Transformed {points_map.shape[0]} points to map frame")
        return points_map

    def downsample_pointcloud(self, points: np.ndarray, voxel_size: Optional[float] = None) -> np.ndarray:
        """
        Downsample point cloud using voxel grid filtering.
        
        Divides 3D space into voxels of specified size and keeps only one point
        per voxel (the centroid of all points in that voxel). This reduces point
        density while preserving overall distribution.
        
        Args:
            points: Nx3 array of 3D points
            voxel_size: Voxel size in meters (uses config default if None)
            
        Returns:
            Mx3 array of downsampled points where M <= N
            
        Requirements: 13.3
        """
        if points.shape[0] == 0:
            return points
        
        if voxel_size is None:
            voxel_size = self.config.voxel_size
        
        if voxel_size <= 0:
            error_msg = f"Voxel size must be positive, got {voxel_size}"
            logger.error(error_msg)
            raise InvalidDepthImageException(details=error_msg)
        
        # Quantize points to voxel grid
        # Each point is assigned to a voxel based on its coordinates
        voxel_indices = np.floor(points / voxel_size).astype(np.int32)
        
        # Create unique voxel keys by combining x, y, z indices
        # Use a dictionary to group points by voxel
        voxel_dict = {}
        for i, voxel_idx in enumerate(voxel_indices):
            # Create hashable key from voxel indices
            key = tuple(voxel_idx)
            if key not in voxel_dict:
                voxel_dict[key] = []
            voxel_dict[key].append(points[i])
        
        # Compute centroid for each voxel
        downsampled_points = []
        for voxel_points in voxel_dict.values():
            # Average all points in this voxel
            centroid = np.mean(voxel_points, axis=0)
            downsampled_points.append(centroid)
        
        downsampled = np.array(downsampled_points, dtype=np.float32)
        
        reduction_ratio = 100.0 * (1.0 - downsampled.shape[0] / points.shape[0])
        logger.debug(
            f"Downsampled point cloud from {points.shape[0]} to {downsampled.shape[0]} points "
            f"({reduction_ratio:.1f}% reduction) using voxel size {voxel_size}m"
        )
        
        return downsampled
    
    async def process_depth_image(self, request: DepthImageRequest) -> DepthProcessingResult:
        """
        Process a depth image request end-to-end.
        
        This is the main entry point for depth image processing. It:
        1. Decodes the depth image
        2. Converts to 3D point cloud in camera frame
        3. Transforms to map frame
        4. Downsamples the point cloud
        
        Args:
            request: Depth image processing request
            
        Returns:
            Processing result with point cloud and metrics
            
        Requirements: 9.1, 10.1-10.5, 12.1-12.3
        """
        start_time = time.time()
        
        try:
            # Step 1: Decode depth image
            depth_array = self.decode_depth_image(
                request.depth_image,
                request.encoding,
                request.camera_intrinsics.width,
                request.camera_intrinsics.height
            )
            
            # Step 2: Convert to point cloud in camera frame
            points_camera = self.depth_to_pointcloud(
                depth_array,
                request.camera_intrinsics,
                request.depth_scale
            )
            
            if points_camera.shape[0] == 0:
                processing_time = (time.time() - start_time) * 1000
                return DepthProcessingResult(
                    success=True,
                    points_generated=0,
                    processing_time_ms=processing_time,
                    timestamp=request.timestamp,
                    message="No valid depth points found in image"
                )
            
            # Step 3: Transform to map frame
            # Note: Map bounds filtering will be applied if configured
            points_map = self.transform_pointcloud(
                points_camera,
                request.camera_pose,
                map_bounds=None  # Will be set by caller if needed
            )
            
            # Step 4: Downsample point cloud
            points_downsampled = self.downsample_pointcloud(points_map)
            
            processing_time = (time.time() - start_time) * 1000
            
            return DepthProcessingResult(
                success=True,
                points_generated=points_downsampled.shape[0],
                processing_time_ms=processing_time,
                timestamp=request.timestamp,
                message=f"Successfully processed depth image: {points_downsampled.shape[0]} points generated"
            )
            
        except (InvalidDepthImageException, DepthImageDimensionMismatchException, InvalidDepthEncodingException) as e:
            # Re-raise custom depth processing exceptions to be handled by exception handlers
            logger.error(f"Depth processing validation error: {e.code} - {e.message}")
            raise
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            logger.error(f"Unexpected error during depth processing: {str(e)}", exc_info=True)
            # Wrap unexpected errors in our custom exception
            raise InvalidDepthImageException(details=f"Unexpected error: {str(e)}")
