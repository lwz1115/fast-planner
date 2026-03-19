"""
Logging configuration for FastAPI-Fast-Planner Interface.

This module provides structured logging configuration with support for:
- Multiple log levels
- Structured log formatting
- Request correlation via request IDs
- Performance monitoring
- Error tracking with stack traces

Requirements: 8.5
"""

import logging
import sys
from typing import Optional


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter for structured logging.
    
    Adds consistent formatting with request IDs, timestamps, and context.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record with structured information.
        
        Args:
            record: Log record to format
            
        Returns:
            Formatted log string
        """
        # Add request ID if available
        if not hasattr(record, 'request_id'):
            record.request_id = '-'
        
        # Format the base message
        formatted = super().format(record)
        
        # Add extra fields if present
        extra_fields = []
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename', 'funcName',
                          'levelname', 'levelno', 'lineno', 'module', 'msecs',
                          'message', 'pathname', 'process', 'processName',
                          'relativeCreated', 'thread', 'threadName', 'exc_info',
                          'exc_text', 'stack_info', 'request_id']:
                extra_fields.append(f"{key}={value}")
        
        if extra_fields:
            formatted += f" | {', '.join(extra_fields)}"
        
        return formatted


def configure_logging(log_level: str = "INFO") -> None:
    """
    Configure application logging with structured format.
    
    Sets up:
    - Console handler with structured formatting
    - Appropriate log levels for different modules
    - Request correlation support
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Requirements: 8.5
    """
    # Convert log level string to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    
    # Create structured formatter
    formatter = StructuredFormatter(
        fmt='%(asctime)s - [%(request_id)s] - %(name)s - %(levelname)s - '
            '[%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Add console handler
    root_logger.addHandler(console_handler)
    
    # Set specific log levels for noisy libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    
    # Log configuration complete
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level: {log_level}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class PerformanceLogger:
    """
    Helper class for logging performance metrics.
    
    Provides convenient methods for logging timing information,
    success rates, and other performance indicators.
    """
    
    def __init__(self, logger: logging.Logger):
        """
        Initialize performance logger.
        
        Args:
            logger: Logger instance to use
        """
        self.logger = logger
    
    def log_timing(
        self,
        operation: str,
        duration_ms: float,
        success: bool = True,
        **extra_fields
    ) -> None:
        """
        Log timing information for an operation.
        
        Args:
            operation: Name of the operation
            duration_ms: Duration in milliseconds
            success: Whether operation succeeded
            **extra_fields: Additional fields to log
        """
        level = logging.INFO if success else logging.WARNING
        
        self.logger.log(
            level,
            f"{operation} {'completed' if success else 'failed'} in {duration_ms:.2f}ms",
            extra={
                "operation": operation,
                "duration_ms": duration_ms,
                "success": success,
                **extra_fields
            }
        )
    
    def log_rate(
        self,
        metric_name: str,
        count: int,
        total: int,
        **extra_fields
    ) -> None:
        """
        Log rate/percentage metrics.
        
        Args:
            metric_name: Name of the metric
            count: Count of items
            total: Total items
            **extra_fields: Additional fields to log
        """
        rate = (count / total * 100) if total > 0 else 0
        
        self.logger.info(
            f"{metric_name}: {count}/{total} ({rate:.1f}%)",
            extra={
                "metric": metric_name,
                "count": count,
                "total": total,
                "rate": rate,
                **extra_fields
            }
        )
    
    def log_counter(
        self,
        counter_name: str,
        value: int,
        **extra_fields
    ) -> None:
        """
        Log counter metrics.
        
        Args:
            counter_name: Name of the counter
            value: Counter value
            **extra_fields: Additional fields to log
        """
        self.logger.info(
            f"{counter_name}: {value}",
            extra={
                "counter": counter_name,
                "value": value,
                **extra_fields
            }
        )


# Example usage:
# from fastapi_planner.logging_config import configure_logging, get_logger, PerformanceLogger
#
# configure_logging("INFO")
# logger = get_logger(__name__)
# perf_logger = PerformanceLogger(logger)
#
# perf_logger.log_timing("planning", 45.3, success=True, algorithm="kinodynamic")
# perf_logger.log_rate("success_rate", 95, 100)
