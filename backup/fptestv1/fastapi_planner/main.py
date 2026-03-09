"""
FastAPI application for Fast-Planner Interface.

This module implements the REST API endpoints for trajectory planning,
odometry queries, and health monitoring. It bridges HTTP requests with
the ROS-based Fast-Planner system.

Requirements: 1.1, 1.2, 5.1, 5.3, 6.1
"""

import logging
import time
import sys
import uuid
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from config import get_config, Config
from ros_bridge import ROSBridge
from planning_client import PlanningClient
from models import (
    PlanRequest,
    PlanResponse,
    OdometryResponse,
    HealthResponse,
    ErrorInfo
)
from exceptions import (
    ValidationException,
    ServiceUnavailableException,
    PositionOutOfBoundsException,
    ROSConnectionException
)
from error_handlers import register_exception_handlers
from logging_config import configure_logging, PerformanceLogger


# Request ID tracking for correlation
import contextvars
request_id_var = contextvars.ContextVar('request_id', default=None)

# Logger will be configured during startup
logger = logging.getLogger(__name__)
perf_logger: Optional[PerformanceLogger] = None


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for request/response logging and performance monitoring.
    
    Logs:
    - Request details (method, path, client)
    - Response status and timing
    - Planning performance metrics
    
    Requirements: 8.5
    """
    
    async def dispatch(self, request: Request, call_next):
        # Generate unique request ID for correlation
        request_id = str(uuid.uuid4())[:8]
        request_id_var.set(request_id)
        
        # Log incoming request
        logger.info(
            f"[{request_id}] Incoming request: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else "unknown",
                "query_params": dict(request.query_params)
            }
        )
        
        # Track request timing
        start_time = time.time()
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            process_time_ms = (time.time() - start_time) * 1000.0
            
            # Log response
            logger.info(
                f"[{request_id}] Response: {response.status_code} "
                f"(took {process_time_ms:.2f}ms)",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "process_time_ms": process_time_ms,
                    "path": request.url.path
                }
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time-MS"] = f"{process_time_ms:.2f}"
            
            return response
            
        except Exception as e:
            # Log error with stack trace
            process_time_ms = (time.time() - start_time) * 1000.0
            logger.error(
                f"[{request_id}] Request failed after {process_time_ms:.2f}ms: {e}",
                exc_info=True,
                extra={
                    "request_id": request_id,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "process_time_ms": process_time_ms,
                    "path": request.url.path
                }
            )
            raise


# Global instances
config: Optional[Config] = None
ros_bridge: Optional[ROSBridge] = None
planning_client: Optional[PlanningClient] = None
startup_time: float = 0.0


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown.
    
    Handles:
    - Configuration loading
    - Logging configuration
    - ROS connection initialization
    - Graceful shutdown and resource cleanup
    
    Requirements: 4.4, 4.5, 8.5
    """
    global config, ros_bridge, planning_client, startup_time, perf_logger
    
    # Startup
    startup_time = time.time()
    
    try:
        # Load configuration first (before logging is configured)
        config = get_config()
        
        # Configure structured logging
        configure_logging(config.service.log_level)
        logger.info("Starting FastAPI-Fast-Planner Interface")
        
        # Initialize performance logger
        perf_logger = PerformanceLogger(logger)
        logger.info("Performance logging initialized")
        
        # Initialize ROS Bridge
        logger.info("Initializing ROS Bridge...")
        ros_bridge = ROSBridge(config.ros)
        
        # Connect to ROS
        logger.info(f"Connecting to ROS Master at {config.ros.master_uri}...")
        if not ros_bridge.connect():
            logger.error("Failed to connect to ROS Master")
            logger.error("Please ensure ROS Master is running and accessible")
            sys.exit(1)
        
        logger.info("ROS Bridge connected successfully")
        
        # Initialize Planning Client
        logger.info("Initializing Planning Client...")
        planning_client = PlanningClient(ros_bridge, config.planning)
        logger.info("Planning Client initialized")
        
        logger.info("FastAPI-Fast-Planner Interface started successfully")
        logger.info(f"Service listening on {config.service.host}:{config.service.port}")
        
        # Log startup summary
        logger.info(
            "Service configuration summary",
            extra={
                "ros_master_uri": config.ros.master_uri,
                "planning_timeout": config.planning.planning_timeout,
                "trajectory_sample_rate": config.planning.trajectory_sample_rate,
                "map_size": f"{config.map.size_x}x{config.map.size_y}x{config.map.size_z}",
                "service_port": config.service.port
            }
        )
        
        yield
        
    except Exception as e:
        logger.error(f"Startup failed: {e}", exc_info=True)
        sys.exit(1)
    
    # Shutdown
    logger.info("Shutting down FastAPI-Fast-Planner Interface")
    
    if ros_bridge:
        ros_bridge.shutdown()
    
    logger.info("Shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="FastAPI-Fast-Planner Interface",
    description="REST API interface for Fast-Planner trajectory planning system",
    version="1.0.0",
    lifespan=lifespan
)

# Register exception handlers
register_exception_handlers(app)

# Add logging middleware
app.add_middleware(LoggingMiddleware)
logger.info("Logging middleware registered")


# Add CORS middleware
@app.on_event("startup")
async def configure_cors():
    """Configure CORS middleware based on configuration."""
    if config and config.service.enable_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=config.service.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        logger.info(f"CORS enabled for origins: {config.service.cors_origins}")


@app.post(
    "/plan",
    response_model=PlanResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorInfo, "description": "Invalid request parameters"},
        422: {"model": ErrorInfo, "description": "Planning failed"},
        503: {"model": ErrorInfo, "description": "Service unavailable"},
        504: {"model": ErrorInfo, "description": "Planning timeout"}
    },
    summary="Plan trajectory from start to goal",
    description="Submit a planning request with start and goal positions. "
                "Returns a trajectory with waypoints or error information."
)
async def plan_trajectory(request: PlanRequest) -> PlanResponse:
    """
    Plan a trajectory from start to goal position.
    
    This endpoint accepts a planning request with start/goal positions and
    planning parameters, invokes Fast-Planner via ROS, and returns the
    computed trajectory as a series of waypoints.
    
    Args:
        request: Planning request with positions and parameters
        
    Returns:
        PlanResponse with trajectory or error information
        
    Raises:
        HTTPException: For various error conditions (400, 422, 503, 504)
        
    Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 8.5
    """
    request_id = request_id_var.get()
    
    # Log request details
    logger.info(
        f"[{request_id}] Planning request received",
        extra={
            "request_id": request_id,
            "start": request.start.dict(),
            "goal": request.goal.dict(),
            "max_velocity": request.max_velocity,
            "max_acceleration": request.max_acceleration,
            "algorithm": request.algorithm,
            "use_current_odom": request.use_current_odom
        }
    )
    
    if not planning_client or not ros_bridge:
        logger.error(f"[{request_id}] Planning service not initialized")
        raise ServiceUnavailableException(
            code="service_not_initialized",
            message="Planning service is not initialized",
            details="Service may still be starting up"
        )
    
    # Validate positions are within map boundaries
    if config:
        if not config.map.is_position_in_bounds(
            request.start.x, request.start.y, request.start.z
        ):
            bounds_info = (
                f"Map bounds: X=[{config.map.origin_x}, {config.map.origin_x + config.map.size_x}], "
                f"Y=[{config.map.origin_y}, {config.map.origin_y + config.map.size_y}], "
                f"Z=[{config.map.origin_z}, {config.map.origin_z + config.map.size_z}]"
            )
            logger.warning(
                f"[{request_id}] Start position out of bounds: {request.start.dict()}",
                extra={
                    "request_id": request_id,
                    "position": request.start.dict(),
                    "bounds": bounds_info
                }
            )
            raise PositionOutOfBoundsException("start", bounds_info)
        
        if not config.map.is_position_in_bounds(
            request.goal.x, request.goal.y, request.goal.z
        ):
            bounds_info = (
                f"Map bounds: X=[{config.map.origin_x}, {config.map.origin_x + config.map.size_x}], "
                f"Y=[{config.map.origin_y}, {config.map.origin_y + config.map.size_y}], "
                f"Z=[{config.map.origin_z}, {config.map.origin_z + config.map.size_z}]"
            )
            logger.warning(
                f"[{request_id}] Goal position out of bounds: {request.goal.dict()}",
                extra={
                    "request_id": request_id,
                    "position": request.goal.dict(),
                    "bounds": bounds_info
                }
            )
            raise PositionOutOfBoundsException("goal", bounds_info)
    
    # Check ROS connection
    if not ros_bridge.is_connected():
        logger.error(f"[{request_id}] ROS connection not available")
        raise ROSConnectionException()
    
    # Execute planning request (exceptions will be handled by exception handlers)
    logger.debug(f"[{request_id}] Invoking planning client")
    response = await planning_client.plan_trajectory(request)
    
    # Log planning performance metrics
    logger.info(
        f"[{request_id}] Planning completed successfully: "
        f"{response.trajectory.num_waypoints if response.trajectory else 0} waypoints, "
        f"planning_time={response.planning_time_ms:.2f}ms, "
        f"total_time={response.total_time_ms:.2f}ms",
        extra={
            "request_id": request_id,
            "success": response.success,
            "num_waypoints": response.trajectory.num_waypoints if response.trajectory else 0,
            "trajectory_duration": response.trajectory.total_duration if response.trajectory else 0,
            "planning_time_ms": response.planning_time_ms,
            "ros_planning_time_ms": response.ros_planning_time_ms,
            "total_time_ms": response.total_time_ms,
            "algorithm": request.algorithm
        }
    )
    
    return response


@app.get(
    "/odometry",
    response_model=OdometryResponse,
    status_code=status.HTTP_200_OK,
    responses={
        503: {"model": ErrorInfo, "description": "Odometry unavailable"}
    },
    summary="Get current odometry",
    description="Returns the current quadrotor odometry state including position, "
                "orientation, and velocities."
)
async def get_odometry() -> OdometryResponse:
    """
    Get current quadrotor odometry state.
    
    Returns the most recent odometry data if available and fresh (< 1 second old).
    
    Returns:
        OdometryResponse with current state
        
    Raises:
        HTTPException: 503 if odometry is unavailable or stale
        
    Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 8.5
    """
    request_id = request_id_var.get()
    
    if not ros_bridge:
        logger.error(f"[{request_id}] ROS Bridge not initialized")
        raise ServiceUnavailableException(
            code="service_not_initialized",
            message="ROS Bridge is not initialized",
            details="Service may still be starting up"
        )
    
    odometry = ros_bridge.get_latest_odometry()
    
    if odometry is None:
        logger.warning(f"[{request_id}] Odometry data unavailable")
        from exceptions import OdometryUnavailableException
        raise OdometryUnavailableException()
    
    logger.debug(
        f"[{request_id}] Odometry retrieved: pos=({odometry.position.x:.2f}, "
        f"{odometry.position.y:.2f}, {odometry.position.z:.2f})",
        extra={
            "request_id": request_id,
            "position": odometry.position.dict(),
            "timestamp": odometry.timestamp
        }
    )
    
    return odometry


@app.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Get service health status",
    description="Returns the health status of the service including ROS connection, "
                "Fast-Planner availability, and uptime information."
)
async def get_health() -> HealthResponse:
    """
    Get service health status.
    
    Returns health information including:
    - Overall status (healthy/degraded/unhealthy)
    - ROS connection status
    - Fast-Planner availability
    - Service uptime
    - Last successful planning timestamp
    - Odometry age
    
    Returns:
        HealthResponse with status information
        
    Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 8.5
    """
    request_id = request_id_var.get()
    
    # Calculate uptime
    uptime_seconds = time.time() - startup_time if startup_time > 0 else 0.0
    
    # Check ROS connection
    ros_connected = ros_bridge.is_connected() if ros_bridge else False
    
    # Check Fast-Planner availability
    fast_planner_available = False
    if ros_bridge and ros_connected:
        fast_planner_available = ros_bridge.check_planner_status()
    
    # Determine overall status
    if ros_connected and fast_planner_available:
        overall_status = "healthy"
    elif ros_connected and not fast_planner_available:
        overall_status = "degraded"
    else:
        overall_status = "unhealthy"
    
    # Get last planning success timestamp
    last_planning_success = None
    if planning_client:
        last_planning_success = planning_client.get_last_planning_success()
    
    # Get odometry age
    odometry_age_ms = None
    if ros_bridge:
        odometry_age_ms = ros_bridge.get_odometry_age_ms()
    
    # Log health check with details
    logger.debug(
        f"[{request_id}] Health check: status={overall_status}, "
        f"ros_connected={ros_connected}, planner_available={fast_planner_available}, "
        f"uptime={uptime_seconds:.1f}s",
        extra={
            "request_id": request_id,
            "status": overall_status,
            "ros_connected": ros_connected,
            "fast_planner_available": fast_planner_available,
            "uptime_seconds": uptime_seconds,
            "odometry_age_ms": odometry_age_ms
        }
    )
    
    return HealthResponse(
        status=overall_status,
        ros_connected=ros_connected,
        fast_planner_available=fast_planner_available,
        uptime_seconds=uptime_seconds,
        last_planning_success=last_planning_success,
        odometry_age_ms=odometry_age_ms
    )


@app.get(
    "/",
    summary="Root endpoint",
    description="Returns basic service information"
)
async def root():
    """Root endpoint with service information."""
    return {
        "service": "FastAPI-Fast-Planner Interface",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics"
    }


@app.get(
    "/metrics",
    summary="Get performance metrics",
    description="Returns planning performance statistics and metrics"
)
async def get_metrics():
    """
    Get performance metrics and statistics.
    
    Returns planning statistics including success rate, request counts,
    and timing information.
    
    Requirements: 8.5
    """
    request_id = request_id_var.get()
    
    if not planning_client:
        logger.warning(f"[{request_id}] Planning client not initialized")
        return {
            "error": "Planning client not initialized",
            "statistics": None
        }
    
    # Get statistics
    stats = planning_client.get_planning_statistics()
    
    # Calculate additional metrics
    uptime_seconds = time.time() - startup_time if startup_time > 0 else 0.0
    success_rate = (
        (stats["successful_requests"] / stats["total_requests"] * 100)
        if stats["total_requests"] > 0 else 0
    )
    
    metrics = {
        "uptime_seconds": uptime_seconds,
        "total_requests": stats["total_requests"],
        "successful_requests": stats["successful_requests"],
        "failed_requests": stats["failed_requests"],
        "success_rate_percent": round(success_rate, 2),
        "last_planning_success": planning_client.get_last_planning_success(),
        "ros_connected": ros_bridge.is_connected() if ros_bridge else False
    }
    
    logger.debug(
        f"[{request_id}] Metrics retrieved",
        extra={
            "request_id": request_id,
            **metrics
        }
    )
    
    return metrics


# Exception handlers are registered via register_exception_handlers() above


if __name__ == "__main__":
    import uvicorn
    
    # Load config to get host and port
    try:
        cfg = get_config()
        uvicorn.run(
            "main:app",
            host=cfg.service.host,
            port=cfg.service.port,
            log_level=cfg.service.log_level,
            reload=False
        )
    except Exception as e:
        print(f"Failed to start service: {e}")
        sys.exit(1)
