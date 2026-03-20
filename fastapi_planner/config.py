"""
Configuration management for FastAPI-Fast-Planner Interface.

This module handles loading configuration from YAML files and environment variables,
with validation to ensure all required parameters are present and valid.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional
import yaml
from pydantic import BaseModel, Field, validator


logger = logging.getLogger(__name__)


class ROSTopicsConfig(BaseModel):
    """ROS topic configuration."""
    odometry: str = Field(default="/visual_slam/odom", description="Odometry topic")
    goal: str = Field(default="/move_base_simple/goal", description="Default goal topic")
    trajectory: str = Field(default="/planning/bspline", description="Trajectory topic")
    planning_goal: str = Field(default="/planning/goal", description="Alternative goal topic")
    point_cloud: str = Field(default="/depth_cloud", description="Point cloud topic for depth images")
    kinodynamic_goal: Optional[str] = Field(default=None, description="Kinodynamic-specific goal topic (uses 'goal' if not set)")
    topological_goal: Optional[str] = Field(default=None, description="Topological-specific goal topic (uses 'goal' if not set)")
    
    def get_goal_topic_for_algorithm(self, algorithm: str) -> str:
        """
        Get the appropriate goal topic for the specified algorithm.
        
        Args:
            algorithm: Planning algorithm ("kinodynamic" or "topological")
            
        Returns:
            Goal topic path for the algorithm
        """
        if algorithm == "kinodynamic" and self.kinodynamic_goal:
            return self.kinodynamic_goal
        elif algorithm == "topological" and self.topological_goal:
            return self.topological_goal
        else:
            return self.goal


class ROSConfig(BaseModel):
    """ROS connection and topic configuration."""
    master_uri: str = Field(default="http://localhost:11311", description="ROS Master URI")
    node_name: str = Field(default="fastapi_planner_bridge", description="ROS node name")
    topics: ROSTopicsConfig = Field(default_factory=ROSTopicsConfig)

    @validator('master_uri')
    def validate_master_uri(cls, v):
        """Validate ROS Master URI format."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError("ROS Master URI must start with http:// or https://")
        return v

    @validator('node_name')
    def validate_node_name(cls, v):
        """Validate ROS node name."""
        if not v or not v.strip():
            raise ValueError("ROS node name cannot be empty")
        return v.strip()


class PlanningConfig(BaseModel):
    """Planning algorithm configuration."""
    default_max_velocity: float = Field(default=3.0, gt=0, description="Default max velocity (m/s)")
    default_max_acceleration: float = Field(default=2.0, gt=0, description="Default max acceleration (m/s^2)")
    planning_timeout: float = Field(default=5.0, gt=0, description="Planning timeout (seconds)")
    trajectory_sample_rate: float = Field(default=10.0, gt=0, description="Trajectory sample rate (Hz)")
    max_velocity_limit: float = Field(default=10.0, gt=0, description="Maximum velocity limit (m/s)")
    max_acceleration_limit: float = Field(default=10.0, gt=0, description="Maximum acceleration limit (m/s^2)")

    @validator('default_max_velocity')
    def validate_default_velocity(cls, v, values):
        """Ensure default velocity is reasonable."""
        if v > 10.0:
            logger.warning(f"Default max velocity {v} m/s is very high")
        return v

    @validator('trajectory_sample_rate')
    def validate_sample_rate(cls, v):
        """Ensure sample rate is reasonable."""
        if v < 1.0:
            raise ValueError("Trajectory sample rate must be at least 1 Hz")
        if v > 100.0:
            logger.warning(f"Trajectory sample rate {v} Hz is very high")
        return v


class MapConfig(BaseModel):
    """Map boundaries configuration."""
    size_x: float = Field(default=40.0, gt=0, description="Map size in X direction (meters)")
    size_y: float = Field(default=20.0, gt=0, description="Map size in Y direction (meters)")
    size_z: float = Field(default=5.0, gt=0, description="Map size in Z direction (meters)")
    origin_x: float = Field(default=0.0, description="Map origin X coordinate")
    origin_y: float = Field(default=0.0, description="Map origin Y coordinate")
    origin_z: float = Field(default=0.0, description="Map origin Z coordinate")

    def is_position_in_bounds(self, x: float, y: float, z: float) -> bool:
        """Check if a position is within map boundaries."""
        return (
            self.origin_x <= x <= self.origin_x + self.size_x and
            self.origin_y <= y <= self.origin_y + self.size_y and
            self.origin_z <= z <= self.origin_z + self.size_z
        )


class HealthCheckConfig(BaseModel):
    """Health check configuration."""
    max_odometry_age: float = Field(default=1.0, gt=0, description="Max odometry age (seconds)")
    planner_check_interval: float = Field(default=5.0, gt=0, description="Planner check interval (seconds)")


class DepthConfig(BaseModel):
    """Depth image processing configuration."""
    min_depth: float = Field(default=0.1, gt=0, description="Minimum depth threshold (meters)")
    max_depth: float = Field(default=10.0, gt=0, description="Maximum depth threshold (meters)")
    voxel_size: float = Field(default=0.05, gt=0, description="Voxel size for downsampling (meters)")
    max_batch_size: int = Field(default=10, gt=0, le=100, description="Maximum batch size for depth images")
    default_encoding: str = Field(default="16UC1", description="Default depth image encoding")

    @validator('max_depth')
    def validate_depth_range(cls, v, values):
        """Ensure max_depth is greater than min_depth."""
        if 'min_depth' in values and v <= values['min_depth']:
            raise ValueError(f"max_depth ({v}) must be greater than min_depth ({values['min_depth']})")
        return v

    @validator('default_encoding')
    def validate_encoding(cls, v):
        """Validate depth image encoding format."""
        valid_encodings = ['16UC1', '32FC1']
        if v not in valid_encodings:
            raise ValueError(f"Encoding must be one of: {', '.join(valid_encodings)}")
        return v

    @validator('voxel_size')
    def validate_voxel_size(cls, v):
        """Ensure voxel size is reasonable."""
        if v > 1.0:
            logger.warning(f"Voxel size {v} meters is very large, may result in excessive downsampling")
        if v < 0.01:
            logger.warning(f"Voxel size {v} meters is very small, may result in minimal downsampling")
        return v


class ServiceConfig(BaseModel):
    """Service configuration."""
    host: str = Field(default="0.0.0.0", description="Service host address")
    port: int = Field(default=8000, gt=0, lt=65536, description="Service port")
    log_level: str = Field(default="info", description="Logging level")
    enable_cors: bool = Field(default=True, description="Enable CORS")
    cors_origins: List[str] = Field(default_factory=lambda: ["*"], description="CORS allowed origins")
    docs_url: str = Field(default="/docs", description="API docs URL")
    redoc_url: str = Field(default="/redoc", description="ReDoc URL")
    health_check: HealthCheckConfig = Field(default_factory=HealthCheckConfig)

    @validator('log_level')
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ['debug', 'info', 'warning', 'error', 'critical']
        v_lower = v.lower()
        if v_lower not in valid_levels:
            raise ValueError(f"Log level must be one of: {', '.join(valid_levels)}")
        return v_lower


class Config(BaseModel):
    """Main configuration class combining all configuration sections."""
    ros: ROSConfig = Field(default_factory=ROSConfig)
    planning: PlanningConfig = Field(default_factory=PlanningConfig)
    map: MapConfig = Field(default_factory=MapConfig)
    depth: DepthConfig = Field(default_factory=DepthConfig)
    service: ServiceConfig = Field(default_factory=ServiceConfig)

    class Config:
        """Pydantic configuration."""
        validate_assignment = True

    def validate_on_startup(self) -> None:
        """
        Perform additional validation checks on startup.
        Raises ValueError if configuration is invalid.
        """
        # Validate planning limits
        if self.planning.default_max_velocity > self.planning.max_velocity_limit:
            raise ValueError(
                f"Default max velocity ({self.planning.default_max_velocity}) "
                f"exceeds limit ({self.planning.max_velocity_limit})"
            )
        
        if self.planning.default_max_acceleration > self.planning.max_acceleration_limit:
            raise ValueError(
                f"Default max acceleration ({self.planning.default_max_acceleration}) "
                f"exceeds limit ({self.planning.max_acceleration_limit})"
            )
        
        # Validate map boundaries
        if self.map.size_x <= 0 or self.map.size_y <= 0 or self.map.size_z <= 0:
            raise ValueError("Map dimensions must be positive")
        
        # Validate depth processing parameters
        if self.depth.min_depth >= self.depth.max_depth:
            raise ValueError(
                f"min_depth ({self.depth.min_depth}) must be less than "
                f"max_depth ({self.depth.max_depth})"
            )
        
        logger.info("Configuration validation passed")


def load_config_from_yaml(config_path: str) -> Dict:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to YAML configuration file
        
    Returns:
        Dictionary containing configuration data
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If YAML parsing fails
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(path, 'r') as f:
        config_data = yaml.safe_load(f)
    
    if config_data is None:
        raise ValueError(f"Configuration file is empty: {config_path}")
    
    logger.info(f"Loaded configuration from {config_path}")
    return config_data


def apply_env_overrides(config_data: Dict) -> Dict:
    """
    Apply environment variable overrides to configuration.
    
    Environment variables follow the pattern:
    - ROS_MASTER_URI -> ros.master_uri
    - FASTAPI_HOST -> service.host
    - FASTAPI_PORT -> service.port
    - LOG_LEVEL -> service.log_level
    
    Args:
        config_data: Configuration dictionary
        
    Returns:
        Configuration dictionary with environment overrides applied
    """
    # ROS Master URI override
    if 'ROS_MASTER_URI' in os.environ:
        config_data.setdefault('ros', {})['master_uri'] = os.environ['ROS_MASTER_URI']
        logger.info(f"Overriding ROS Master URI from environment: {os.environ['ROS_MASTER_URI']}")
    
    # ROS IP override (for node configuration)
    if 'ROS_IP' in os.environ:
        logger.info(f"ROS_IP environment variable set: {os.environ['ROS_IP']}")
    
    # Service host override
    if 'FASTAPI_HOST' in os.environ:
        config_data.setdefault('service', {})['host'] = os.environ['FASTAPI_HOST']
        logger.info(f"Overriding service host from environment: {os.environ['FASTAPI_HOST']}")
    
    # Service port override
    if 'FASTAPI_PORT' in os.environ:
        try:
            port = int(os.environ['FASTAPI_PORT'])
            config_data.setdefault('service', {})['port'] = port
            logger.info(f"Overriding service port from environment: {port}")
        except ValueError:
            logger.warning(f"Invalid FASTAPI_PORT value: {os.environ['FASTAPI_PORT']}")
    
    # Log level override
    if 'LOG_LEVEL' in os.environ:
        config_data.setdefault('service', {})['log_level'] = os.environ['LOG_LEVEL']
        logger.info(f"Overriding log level from environment: {os.environ['LOG_LEVEL']}")
    
    return config_data


def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load and validate configuration from file and environment variables.
    
    Args:
        config_path: Path to YAML configuration file. If None, uses default path.
        
    Returns:
        Validated Config object
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If configuration is invalid
    """
    # Determine config file path
    if config_path is None:
        # Check environment variable
        config_path = os.environ.get('CONFIG_FILE')
        
        # Use default path if not specified
        if config_path is None:
            # Look for settings.yaml in the fastapi_planner directory
            default_path = Path(__file__).parent / 'settings.yaml'
            if default_path.exists():
                config_path = str(default_path)
            else:
                # Fallback
                config_path = 'fastapi_planner/settings.yaml'
    
    # Load YAML configuration
    try:
        config_data = load_config_from_yaml(config_path)
    except FileNotFoundError:
        logger.warning(f"Config file not found: {config_path}, using defaults")
        config_data = {}
    
    # Apply environment variable overrides
    config_data = apply_env_overrides(config_data)
    
    # Create and validate Config object
    try:
        config = Config(**config_data)
        config.validate_on_startup()
        logger.info("Configuration loaded and validated successfully")
        return config
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        raise


# Global configuration instance (loaded on first import)
_config_instance: Optional[Config] = None


def get_config(config_path: Optional[str] = None, reload: bool = False) -> Config:
    """
    Get the global configuration instance.
    
    Args:
        config_path: Path to configuration file (only used on first load or reload)
        reload: Force reload of configuration
        
    Returns:
        Config instance
    """
    global _config_instance
    
    if _config_instance is None or reload:
        _config_instance = load_config(config_path)
    
    return _config_instance

