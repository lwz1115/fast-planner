"""
Custom exceptions for FastAPI-Fast-Planner Interface.

This module defines custom exception classes for different error scenarios
that can occur during planning operations. These exceptions are mapped to
appropriate HTTP status codes by the exception handlers.

Requirements: 3.1, 3.2, 3.3, 3.4, 3.5
"""

from typing import Optional


class PlanningException(Exception):
    """Base exception for planning-related errors."""
    
    def __init__(
        self,
        code: str,
        message: str,
        details: Optional[str] = None,
        status_code: int = 500
    ):
        """
        Initialize planning exception.
        
        Args:
            code: Machine-readable error code
            message: Human-readable error message
            details: Additional error context
            status_code: HTTP status code for this error
        """
        self.code = code
        self.message = message
        self.details = details
        self.status_code = status_code
        super().__init__(message)


class ValidationException(PlanningException):
    """
    Exception for request validation errors (400).
    
    Raised when request parameters are invalid, out of bounds,
    or fail validation checks.
    
    Requirements: 3.5
    """
    
    def __init__(self, code: str, message: str, details: Optional[str] = None):
        """Initialize validation exception with 400 status code."""
        super().__init__(
            code=code,
            message=message,
            details=details,
            status_code=400
        )


class PlanningFailureException(PlanningException):
    """
    Exception for planning failures (422).
    
    Raised when Fast-Planner cannot find a valid path, encounters
    collisions, or fails trajectory optimization.
    
    Requirements: 3.1, 3.2, 3.3
    """
    
    def __init__(self, code: str, message: str, details: Optional[str] = None):
        """Initialize planning failure exception with 422 status code."""
        super().__init__(
            code=code,
            message=message,
            details=details,
            status_code=422
        )


class ServiceUnavailableException(PlanningException):
    """
    Exception for service unavailable errors (503).
    
    Raised when ROS connection is lost, odometry is unavailable,
    or Fast-Planner node is not responding.
    
    Requirements: 3.5
    """
    
    def __init__(self, code: str, message: str, details: Optional[str] = None):
        """Initialize service unavailable exception with 503 status code."""
        super().__init__(
            code=code,
            message=message,
            details=details,
            status_code=503
        )


class TimeoutException(PlanningException):
    """
    Exception for timeout errors (504).
    
    Raised when planning operations exceed the configured timeout period.
    
    Requirements: 3.4
    """
    
    def __init__(self, code: str, message: str, details: Optional[str] = None):
        """Initialize timeout exception with 504 status code."""
        super().__init__(
            code=code,
            message=message,
            details=details,
            status_code=504
        )


# Specific error code exceptions for common scenarios

class NoPathFoundException(PlanningFailureException):
    """Exception when Fast-Planner cannot find a path to the goal."""
    
    def __init__(self, details: Optional[str] = None):
        """Initialize no path found exception."""
        super().__init__(
            code="no_path_found",
            message="Fast-Planner could not find a collision-free path to the goal",
            details=details or "Goal position may be unreachable or surrounded by obstacles"
        )


class GoalInCollisionException(PlanningFailureException):
    """Exception when goal position is in collision with obstacles."""
    
    def __init__(self, details: Optional[str] = None):
        """Initialize goal in collision exception."""
        super().__init__(
            code="goal_in_collision",
            message="Goal position is in collision with obstacles",
            details=details or "Choose a goal position that is not occupied by obstacles"
        )


class StartInCollisionException(PlanningFailureException):
    """Exception when start position is in collision with obstacles."""
    
    def __init__(self, details: Optional[str] = None):
        """Initialize start in collision exception."""
        super().__init__(
            code="start_in_collision",
            message="Start position is in collision with obstacles",
            details=details or "Choose a start position that is not occupied by obstacles"
        )


class PlanningTimeoutException(TimeoutException):
    """Exception when planning exceeds timeout period."""
    
    def __init__(self, timeout_seconds: float, details: Optional[str] = None):
        """Initialize planning timeout exception."""
        super().__init__(
            code="planning_timeout",
            message=f"Planning timed out after {timeout_seconds} seconds",
            details=details or (
                "Fast-Planner did not return a trajectory within the timeout period. "
                "The goal may be unreachable or the planner is overloaded."
            )
        )


class OdometryUnavailableException(ServiceUnavailableException):
    """Exception when odometry data is not available."""
    
    def __init__(self, details: Optional[str] = None):
        """Initialize odometry unavailable exception."""
        super().__init__(
            code="odometry_unavailable",
            message="No recent odometry data available",
            details=details or "Odometry data is either not being published or is too old (>1 second)"
        )


class ROSConnectionException(ServiceUnavailableException):
    """Exception when ROS connection is lost or unavailable."""
    
    def __init__(self, details: Optional[str] = None):
        """Initialize ROS connection exception."""
        super().__init__(
            code="ros_disconnected",
            message="ROS connection is not available",
            details=details or "Cannot communicate with Fast-Planner"
        )


class PositionOutOfBoundsException(ValidationException):
    """Exception when position is outside map boundaries."""
    
    def __init__(self, position_type: str, bounds_info: str):
        """
        Initialize position out of bounds exception.
        
        Args:
            position_type: "start" or "goal"
            bounds_info: String describing the map boundaries
        """
        super().__init__(
            code=f"{position_type}_out_of_bounds",
            message=f"{position_type.capitalize()} position is outside map boundaries",
            details=bounds_info
        )


class InvalidAlgorithmException(ValidationException):
    """Exception when an unsupported algorithm is specified."""
    
    def __init__(self, algorithm: str, valid_algorithms: list):
        """
        Initialize invalid algorithm exception.
        
        Args:
            algorithm: The invalid algorithm name
            valid_algorithms: List of valid algorithm names
        """
        super().__init__(
            code="invalid_algorithm",
            message=f"Unsupported algorithm: {algorithm}",
            details=f"Valid algorithms are: {', '.join(valid_algorithms)}"
        )
