"""
Planning Client component for FastAPI-Fast-Planner Interface.

This module coordinates planning requests with the ROS Bridge, handles timeouts,
converts B-spline trajectories to waypoints, validates trajectories, and measures
planning performance.

Requirements: 1.1, 8.1, 8.2, 8.3, 8.4
"""

import logging
import time
import asyncio
import uuid
from typing import Optional, Dict
from datetime import datetime
import threading

try:
    from plan_manage.msg import Bspline
    ROS_AVAILABLE = True
except ImportError:
    ROS_AVAILABLE = False
    logging.warning("ROS packages not available. PlanningClient will not function.")

from ros_bridge import ROSBridge
from config import PlanningConfig
from models import PlanRequest, PlanResponse, Trajectory, ErrorInfo, Position
from trajectory_utils import convert_bspline_to_trajectory, validate_trajectory
from exceptions import (
    OdometryUnavailableException,
    PlanningTimeoutException,
    ServiceUnavailableException,
    PlanningFailureException,
    NoPathFoundException
)


logger = logging.getLogger(__name__)


class PlanningClient:
    """
    Client for coordinating trajectory planning requests with Fast-Planner.
    
    Manages the request-response flow, timeout handling, trajectory conversion,
    and performance measurement for planning operations.
    """

    def __init__(self, ros_bridge: ROSBridge, config: PlanningConfig):
        """
        Initialize Planning Client.
        
        Args:
            ros_bridge: ROSBridge instance for ROS communication
            config: Planning configuration parameters
        """
        if not ROS_AVAILABLE:
            raise RuntimeError("ROS packages are not available. Cannot initialize PlanningClient.")
        
        self.ros_bridge = ros_bridge
        self.config = config
        
        # Track planning requests and responses
        self._pending_requests: Dict[str, asyncio.Event] = {}
        self._request_responses: Dict[str, Optional[Bspline]] = {}
        self._request_lock = threading.Lock()
        self._event_loop: Optional[asyncio.AbstractEventLoop] = None
        
        # Performance tracking
        self._last_planning_success: Optional[float] = None
        self._planning_count = 0
        self._success_count = 0
        
        # Register trajectory callback with ROS Bridge
        self.ros_bridge.set_trajectory_callback(self._on_trajectory_received)
        
        logger.info("PlanningClient initialized")

    def _on_trajectory_received(self, trajectory_msg: Bspline) -> None:
        """
        Callback invoked when trajectory is received from Fast-Planner.
        
        This is called by the ROS Bridge when a new trajectory message arrives.
        We store the trajectory and signal any waiting requests.
        
        Args:
            trajectory_msg: B-spline trajectory from Fast-Planner
        """
        logger.info("Trajectory received in PlanningClient callback")
        
        # For now, we'll use a simple approach: store the latest trajectory
        # and signal all pending requests. In a production system with multiple
        # concurrent requests, we'd need trajectory IDs for correlation.
        with self._request_lock:
            # Store trajectory for all pending requests
            for request_id in list(self._pending_requests.keys()):
                self._request_responses[request_id] = trajectory_msg
                # Signal the waiting coroutine
                if request_id in self._pending_requests and self._event_loop:
                    # Set event in thread-safe manner using the stored event loop
                    try:
                        self._event_loop.call_soon_threadsafe(self._pending_requests[request_id].set)
                        logger.info(f"Signaled event for request {request_id}")
                    except Exception as e:
                        logger.error(f"Failed to signal event: {e}", exc_info=True)

    async def plan_trajectory(self, request: PlanRequest) -> PlanResponse:
        """
        Plan a trajectory from start to goal position.
        
        This is the main entry point for planning requests. It:
        1. Validates the request
        2. Publishes goal to Fast-Planner via ROS Bridge
        3. Waits for trajectory response with timeout
        4. Converts B-spline to waypoint trajectory
        5. Validates the trajectory
        6. Measures and returns timing information
        
        Args:
            request: Planning request with start, goal, and parameters
            
        Returns:
            PlanResponse with trajectory or error information
            
        Requirements: 1.1, 8.1, 8.2, 8.3, 8.4
        """
        # Generate unique request ID for correlation
        request_id = str(uuid.uuid4())
        
        # Start timing for total request processing
        total_start_time = time.time()
        
        # Store the current event loop for the callback
        if self._event_loop is None:
            self._event_loop = asyncio.get_event_loop()
        
        logger.info(f"Planning request {request_id}: start={request.start.dict()}, "
                   f"goal={request.goal.dict()}, algorithm={request.algorithm}")
        
        try:
            # Determine start position (use current odometry if requested)
            start_position = request.start
            if request.use_current_odom:
                odometry = self.ros_bridge.get_odometry()
                if odometry is None:
                    logger.error("Cannot use current odometry: data unavailable")
                    raise OdometryUnavailableException(
                        details="Cannot use current odometry as start position"
                    )
                start_position = odometry.position
                logger.info(f"Using current odometry as start: {start_position.dict()}")
            
            # Create event for this request
            event = asyncio.Event()
            with self._request_lock:
                self._pending_requests[request_id] = event
                self._request_responses[request_id] = None
            
            # Publish goal to Fast-Planner
            ros_planning_start_time = time.time()
            
            success = self.ros_bridge.publish_goal(
                start=start_position,
                goal=request.goal,
                algorithm=request.algorithm
            )
            
            if not success:
                logger.error("Failed to publish goal to Fast-Planner")
                raise ServiceUnavailableException(
                    code="ros_communication_error",
                    message="Failed to publish goal to Fast-Planner",
                    details="ROS connection may be lost or goal publisher not initialized"
                )
            
            # Wait for trajectory response with timeout
            try:
                await asyncio.wait_for(
                    event.wait(),
                    timeout=self.config.planning_timeout
                )
            except asyncio.TimeoutError:
                logger.warning(f"Planning timeout after {self.config.planning_timeout}s")
                self._planning_count += 1
                raise PlanningTimeoutException(
                    timeout_seconds=self.config.planning_timeout
                )
            finally:
                # Clean up request tracking
                with self._request_lock:
                    self._pending_requests.pop(request_id, None)
            
            # Get the trajectory response
            with self._request_lock:
                bspline_msg = self._request_responses.pop(request_id, None)
            
            if bspline_msg is None:
                logger.error("No trajectory received from Fast-Planner")
                self._planning_count += 1
                raise NoPathFoundException(
                    details="Fast-Planner did not return a trajectory"
                )
            
            # Calculate ROS planning time
            ros_planning_time_ms = (time.time() - ros_planning_start_time) * 1000.0
            
            # Convert B-spline to waypoint trajectory
            try:
                trajectory = self._convert_bspline_to_waypoints(bspline_msg)
            except Exception as e:
                logger.error(f"Failed to convert B-spline to waypoints: {e}", exc_info=True)
                self._planning_count += 1
                raise PlanningFailureException(
                    code="trajectory_conversion_error",
                    message="Failed to convert B-spline trajectory to waypoints",
                    details=str(e)
                )
            
            # Validate trajectory
            if not self._validate_trajectory(trajectory):
                logger.error("Trajectory validation failed")
                self._planning_count += 1
                raise PlanningFailureException(
                    code="trajectory_validation_error",
                    message="Generated trajectory failed validation",
                    details="Trajectory does not meet requirements (monotonic timestamps, positive duration, etc.)"
                )
            
            # Calculate total time
            total_time_ms = (time.time() - total_start_time) * 1000.0
            planning_time_ms = ros_planning_time_ms  # For now, same as ROS time
            
            # Update success tracking
            self._last_planning_success = time.time()
            self._planning_count += 1
            self._success_count += 1
            
            # Log planning performance metrics
            logger.info(
                f"Planning succeeded: {trajectory.num_waypoints} waypoints, "
                f"duration={trajectory.total_duration:.2f}s, "
                f"planning_time={planning_time_ms:.1f}ms, "
                f"total_time={total_time_ms:.1f}ms",
                extra={
                    "request_id": request_id,
                    "success": True,
                    "num_waypoints": trajectory.num_waypoints,
                    "trajectory_duration": trajectory.total_duration,
                    "planning_time_ms": planning_time_ms,
                    "ros_planning_time_ms": ros_planning_time_ms,
                    "total_time_ms": total_time_ms,
                    "algorithm": request.algorithm,
                    "success_rate": self._success_count / self._planning_count if self._planning_count > 0 else 0
                }
            )
            
            # Return successful response
            return PlanResponse(
                success=True,
                trajectory=trajectory,
                error=None,
                planning_time_ms=planning_time_ms,
                ros_planning_time_ms=ros_planning_time_ms,
                total_time_ms=total_time_ms
            )
            
        except (OdometryUnavailableException, PlanningTimeoutException, 
                ServiceUnavailableException, PlanningFailureException, NoPathFoundException):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error during planning: {e}", exc_info=True)
            self._planning_count += 1
            raise PlanningFailureException(
                code="internal_error",
                message="Internal error during planning",
                details=str(e)
            )

    def _convert_bspline_to_waypoints(self, bspline_msg: Bspline) -> Trajectory:
        """
        Convert B-spline message to waypoint trajectory.
        
        Uses the trajectory_utils module to evaluate the B-spline at regular
        intervals and generate waypoints with position, velocity, and acceleration.
        
        Args:
            bspline_msg: B-spline trajectory from Fast-Planner
            
        Returns:
            Trajectory with sampled waypoints
            
        Raises:
            ValueError: If conversion fails
            
        Requirements: 2.1, 2.3, 2.4, 2.5
        """
        try:
            trajectory = convert_bspline_to_trajectory(
                bspline_msg,
                sample_rate=self.config.trajectory_sample_rate
            )
            logger.debug(f"Converted B-spline to {trajectory.num_waypoints} waypoints")
            return trajectory
        except Exception as e:
            logger.error(f"B-spline conversion failed: {e}", exc_info=True)
            raise

    def _validate_trajectory(self, trajectory: Trajectory) -> bool:
        """
        Validate that trajectory meets all requirements.
        
        Checks:
        - At least one waypoint
        - Monotonically increasing timestamps
        - Positive duration
        - Waypoint count matches
        
        Args:
            trajectory: Trajectory to validate
            
        Returns:
            True if valid, False otherwise
            
        Requirements: 2.3, 2.4
        """
        try:
            is_valid = validate_trajectory(trajectory)
            if is_valid:
                logger.debug("Trajectory validation passed")
            else:
                logger.warning("Trajectory validation failed")
            return is_valid
        except Exception as e:
            logger.error(f"Trajectory validation error: {e}", exc_info=True)
            return False

    def _create_error_response(
        self,
        code: str,
        message: str,
        details: Optional[str] = None,
        total_time_ms: float = 0.0
    ) -> PlanResponse:
        """
        Create an error response for failed planning requests.
        
        Args:
            code: Machine-readable error code
            message: Human-readable error message
            details: Additional error context
            total_time_ms: Total request processing time
            
        Returns:
            PlanResponse with error information
            
        Requirements: 3.1, 3.2, 3.3, 3.4, 3.5
        """
        self._planning_count += 1
        
        error_info = ErrorInfo(
            code=code,
            message=message,
            details=details
        )
        
        return PlanResponse(
            success=False,
            trajectory=None,
            error=error_info,
            planning_time_ms=0.0,
            ros_planning_time_ms=None,
            total_time_ms=total_time_ms
        )

    def get_last_planning_success(self) -> Optional[float]:
        """
        Get timestamp of last successful planning operation.
        
        Returns:
            Timestamp (seconds since epoch) or None if no successful planning yet
            
        Requirements: 6.5
        """
        return self._last_planning_success

    def get_planning_statistics(self) -> Dict[str, int]:
        """
        Get planning statistics.
        
        Returns:
            Dictionary with planning count and success count
        """
        return {
            "total_requests": self._planning_count,
            "successful_requests": self._success_count,
            "failed_requests": self._planning_count - self._success_count
        }

    def reset_statistics(self) -> None:
        """Reset planning statistics."""
        self._planning_count = 0
        self._success_count = 0
        self._last_planning_success = None
        logger.info("Planning statistics reset")

    def log_performance_summary(self) -> None:
        """
        Log a summary of planning performance metrics.
        
        Useful for periodic monitoring and debugging.
        
        Requirements: 8.5
        """
        success_rate = (
            (self._success_count / self._planning_count * 100) 
            if self._planning_count > 0 else 0
        )
        
        logger.info(
            f"Planning performance summary: "
            f"total={self._planning_count}, "
            f"success={self._success_count}, "
            f"failed={self._planning_count - self._success_count}, "
            f"success_rate={success_rate:.1f}%",
            extra={
                "total_requests": self._planning_count,
                "successful_requests": self._success_count,
                "failed_requests": self._planning_count - self._success_count,
                "success_rate": success_rate,
                "last_success_timestamp": self._last_planning_success
            }
        )

