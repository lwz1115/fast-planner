"""
Error handlers for FastAPI-Fast-Planner Interface.

This module implements exception handlers that convert Python exceptions
into properly formatted HTTP error responses with appropriate status codes
and error information.

Requirements: 3.1, 3.2, 3.3, 3.4, 3.5
"""

import logging
from typing import Union

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from exceptions import (
    PlanningException,
    ValidationException,
    PlanningFailureException,
    ServiceUnavailableException,
    TimeoutException
)
from models import ErrorInfo


logger = logging.getLogger(__name__)


def create_error_response(
    status_code: int,
    error_code: str,
    message: str,
    details: Union[str, None] = None
) -> JSONResponse:
    """
    Create a standardized error response.
    
    Args:
        status_code: HTTP status code
        error_code: Machine-readable error code
        message: Human-readable error message
        details: Additional error context
        
    Returns:
        JSONResponse with error information
        
    Requirements: 3.5
    """
    error_info = ErrorInfo(
        code=error_code,
        message=message,
        details=details
    )
    
    return JSONResponse(
        status_code=status_code,
        content=error_info.dict()
    )


async def validation_exception_handler(
    request: Request,
    exc: Union[RequestValidationError, ValidationError, ValidationException]
) -> JSONResponse:
    """
    Handle validation errors (400).
    
    Handles:
    - Pydantic validation errors from request body
    - Custom ValidationException instances
    - Invalid request parameters
    
    Args:
        request: The FastAPI request
        exc: The validation exception
        
    Returns:
        JSONResponse with 400 status and error details
        
    Requirements: 3.5
    """
    logger.warning(f"Validation error on {request.url.path}: {exc}")
    
    # Handle custom ValidationException
    if isinstance(exc, ValidationException):
        logger.error(
            f"Validation error: {exc.code} - {exc.message}",
            extra={
                "error_code": exc.code,
                "path": request.url.path,
                "details": exc.details
            }
        )
        return create_error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=exc.code,
            message=exc.message,
            details=exc.details
        )
    
    # Handle Pydantic validation errors
    if isinstance(exc, (RequestValidationError, ValidationError)):
        # Extract error details from Pydantic
        errors = exc.errors() if hasattr(exc, 'errors') else []
        error_messages = []
        
        for error in errors:
            loc = " -> ".join(str(x) for x in error.get("loc", []))
            msg = error.get("msg", "Validation error")
            error_messages.append(f"{loc}: {msg}")
        
        details = "; ".join(error_messages) if error_messages else str(exc)
        
        logger.error(
            f"Request validation error: {details}",
            extra={
                "error_code": "validation_error",
                "path": request.url.path,
                "errors": errors
            }
        )
        
        return create_error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="validation_error",
            message="Invalid request parameters",
            details=details
        )
    
    # Fallback for unexpected validation error types
    logger.error(f"Unexpected validation error type: {type(exc)}")
    return create_error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        error_code="validation_error",
        message="Invalid request parameters",
        details=str(exc)
    )


async def planning_failure_exception_handler(
    request: Request,
    exc: PlanningFailureException
) -> JSONResponse:
    """
    Handle planning failure errors (422).
    
    Handles:
    - No path found
    - Start/goal in collision
    - Trajectory optimization failures
    
    Args:
        request: The FastAPI request
        exc: The planning failure exception
        
    Returns:
        JSONResponse with 422 status and error details
        
    Requirements: 3.1, 3.2, 3.3, 8.5
    """
    logger.warning(
        f"Planning failure: {exc.code} - {exc.message}",
        exc_info=True if exc.code == "internal_error" else False,
        extra={
            "error_code": exc.code,
            "path": request.url.path,
            "details": exc.details,
            "status_code": 422
        }
    )
    
    return create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_code=exc.code,
        message=exc.message,
        details=exc.details
    )


async def service_unavailable_exception_handler(
    request: Request,
    exc: ServiceUnavailableException
) -> JSONResponse:
    """
    Handle service unavailable errors (503).
    
    Handles:
    - ROS connection lost
    - Odometry unavailable
    - Fast-Planner node not responding
    
    Args:
        request: The FastAPI request
        exc: The service unavailable exception
        
    Returns:
        JSONResponse with 503 status and error details
        
    Requirements: 3.5
    """
    logger.error(
        f"Service unavailable: {exc.code} - {exc.message}",
        extra={
            "error_code": exc.code,
            "path": request.url.path,
            "details": exc.details
        }
    )
    
    return create_error_response(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        error_code=exc.code,
        message=exc.message,
        details=exc.details
    )


async def timeout_exception_handler(
    request: Request,
    exc: TimeoutException
) -> JSONResponse:
    """
    Handle timeout errors (504).
    
    Handles:
    - Planning timeout
    - ROS communication timeout
    
    Args:
        request: The FastAPI request
        exc: The timeout exception
        
    Returns:
        JSONResponse with 504 status and error details
        
    Requirements: 3.4
    """
    logger.warning(
        f"Timeout error: {exc.code} - {exc.message}",
        extra={
            "error_code": exc.code,
            "path": request.url.path,
            "details": exc.details
        }
    )
    
    return create_error_response(
        status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        error_code=exc.code,
        message=exc.message,
        details=exc.details
    )


async def planning_exception_handler(
    request: Request,
    exc: PlanningException
) -> JSONResponse:
    """
    Handle generic planning exceptions.
    
    This is a catch-all handler for PlanningException instances that
    don't match more specific exception types.
    
    Args:
        request: The FastAPI request
        exc: The planning exception
        
    Returns:
        JSONResponse with appropriate status code and error details
        
    Requirements: 3.5
    """
    logger.error(
        f"Planning exception: {exc.code} - {exc.message}",
        extra={
            "error_code": exc.code,
            "path": request.url.path,
            "details": exc.details,
            "status_code": exc.status_code
        }
    )
    
    return create_error_response(
        status_code=exc.status_code,
        error_code=exc.code,
        message=exc.message,
        details=exc.details
    )


async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """
    Handle ValueError exceptions.
    
    ValueErrors typically indicate invalid parameters or data that
    passed initial validation but failed business logic checks.
    
    Args:
        request: The FastAPI request
        exc: The ValueError exception
        
    Returns:
        JSONResponse with 400 status and error details
        
    Requirements: 3.5
    """
    logger.warning(
        f"ValueError on {request.url.path}: {exc}",
        extra={
            "error_code": "value_error",
            "path": request.url.path
        }
    )
    
    return create_error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        error_code="value_error",
        message="Invalid value in request",
        details=str(exc)
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected exceptions.
    
    This is the catch-all handler for any exceptions that don't match
    more specific handlers. It logs the full stack trace and returns
    a generic 500 error to the client.
    
    Args:
        request: The FastAPI request
        exc: The exception
        
    Returns:
        JSONResponse with 500 status and error details
        
    Requirements: 3.5
    """
    logger.error(
        f"Unexpected error on {request.url.path}: {exc}",
        exc_info=True,
        extra={
            "error_code": "internal_error",
            "path": request.url.path,
            "exception_type": type(exc).__name__
        }
    )
    
    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code="internal_error",
        message="An unexpected error occurred",
        details=f"{type(exc).__name__}: {str(exc)}"
    )


def register_exception_handlers(app) -> None:
    """
    Register all exception handlers with the FastAPI application.
    
    This function should be called during application initialization to
    register all custom exception handlers.
    
    Args:
        app: The FastAPI application instance
        
    Requirements: 3.1, 3.2, 3.3, 3.4, 3.5
    """
    # Register custom exception handlers
    app.add_exception_handler(ValidationException, validation_exception_handler)
    app.add_exception_handler(PlanningFailureException, planning_failure_exception_handler)
    app.add_exception_handler(ServiceUnavailableException, service_unavailable_exception_handler)
    app.add_exception_handler(TimeoutException, timeout_exception_handler)
    app.add_exception_handler(PlanningException, planning_exception_handler)
    
    # Register standard exception handlers
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(ValueError, value_error_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Exception handlers registered")
