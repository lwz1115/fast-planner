"""
ROS Bridge component for FastAPI-Fast-Planner Interface.

This module handles all ROS communication including:
- ROS node initialization and lifecycle management
- Odometry subscription with message caching
- Goal publishing to Fast-Planner
- Trajectory subscription from Fast-Planner
- Connection validation and status checking

Requirements: 4.4, 5.1-5.5
"""

import logging
import threading
import time
from typing import Optional, Callable, Dict
from datetime import datetime

try:
    import rospy
    from nav_msgs.msg import Odometry
    from geometry_msgs.msg import PoseStamped, Point, Quaternion as ROSQuaternion
    from plan_manage.msg import Bspline
    from sensor_msgs.msg import PointCloud2, PointField
    from std_msgs.msg import Header
    import struct
    import numpy as np
    ROS_AVAILABLE = True
except ImportError:
    ROS_AVAILABLE = False
    logging.warning("ROS packages not available. ROSBridge will not function.")

from config import ROSConfig
from models import Position, Quaternion, OdometryResponse


logger = logging.getLogger(__name__)


class ROSBridge:
    """
    Bridge between FastAPI service and ROS Fast-Planner system.
    
    Manages ROS node lifecycle, subscribes to odometry and trajectory topics,
    publishes goal positions, and provides connection status checking.
    """

    def __init__(self, config: ROSConfig):
        """
        Initialize ROS Bridge with configuration.
        
        Args:
            config: ROS configuration including master URI and topic names
        """
        if not ROS_AVAILABLE:
            raise RuntimeError("ROS packages are not available. Cannot initialize ROSBridge.")
        
        self.config = config
        self._node_initialized = False
        self._ros_connected = False
        
        # Odometry caching (max age 1 second per requirement 5.5)
        self._latest_odometry: Optional[Odometry] = None
        self._odometry_timestamp: Optional[float] = None
        self._odometry_lock = threading.Lock()
        self._max_odometry_age = 1.0  # seconds
        
        # Trajectory caching
        self._latest_trajectory: Optional[Bspline] = None
        self._trajectory_timestamp: Optional[float] = None
        self._trajectory_lock = threading.Lock()
        self._trajectory_callback: Optional[Callable] = None
        
        # ROS publishers and subscribers
        self._goal_publisher: Optional[rospy.Publisher] = None
        self._goal_publishers: Dict[str, rospy.Publisher] = {}  # Algorithm-specific publishers
        self._point_cloud_publisher: Optional[rospy.Publisher] = None
        self._odometry_subscriber: Optional[rospy.Subscriber] = None
        self._trajectory_subscriber: Optional[rospy.Subscriber] = None
        
        logger.info(f"ROSBridge initialized with config: {config.dict()}")

    def connect(self) -> bool:
        """
        Initialize ROS node and establish connections.
        
        Initializes the ROS node, sets up publishers and subscribers,
        and validates the connection to ROS master.
        
        Returns:
            True if connection successful, False otherwise
            
        Requirements: 4.4
        """
        try:
            # Set ROS Master URI from config
            import os
            os.environ['ROS_MASTER_URI'] = self.config.master_uri
            logger.info(f"Setting ROS_MASTER_URI to {self.config.master_uri}")
            
            # Initialize ROS node if not already initialized
            if not self._node_initialized:
                try:
                    rospy.init_node(
                        self.config.node_name,
                        anonymous=True,
                        disable_signals=True,
                        log_level=rospy.INFO
                    )
                    self._node_initialized = True
                    logger.info(f"ROS node '{self.config.node_name}' initialized")
                except rospy.exceptions.ROSException as e:
                    if "rospy.init_node() has already been called" in str(e):
                        logger.warning("ROS node already initialized")
                        self._node_initialized = True
                    else:
                        raise
            
            # Validate connection to ROS master
            if not self._check_ros_master():
                logger.error("Cannot connect to ROS master")
                return False
            
            # Set up publishers
            self._setup_publishers()
            
            # Set up subscribers
            self._setup_subscribers()
            
            self._ros_connected = True
            logger.info("ROS Bridge connected successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect ROS Bridge: {e}", exc_info=True)
            self._ros_connected = False
            return False

    def _check_ros_master(self) -> bool:
        """
        Check if ROS master is reachable.
        
        Returns:
            True if ROS master is reachable, False otherwise
        """
        try:
            rospy.get_master().getPid()
            return True
        except Exception as e:
            logger.error(f"ROS master not reachable: {e}")
            return False

    def _setup_publishers(self) -> None:
        """
        Set up ROS publishers for goal positions and point clouds.
        
        Creates publishers for both default and algorithm-specific goal topics,
        as well as point cloud topic for depth image processing.
        
        Requirements: 4.4, 7.3, 10.5, 13.4
        """
        try:
            # Dictionary to store publishers for different algorithms
            self._goal_publishers = {}
            
            # Publisher for default goal topic
            self._goal_publisher = rospy.Publisher(
                self.config.topics.goal,
                PoseStamped,
                queue_size=10
            )
            logger.info(f"Default goal publisher created on topic: {self.config.topics.goal}")
            
            # Create algorithm-specific publishers if configured
            if self.config.topics.kinodynamic_goal:
                self._goal_publishers['kinodynamic'] = rospy.Publisher(
                    self.config.topics.kinodynamic_goal,
                    PoseStamped,
                    queue_size=10
                )
                logger.info(f"Kinodynamic goal publisher created on topic: {self.config.topics.kinodynamic_goal}")
            
            if self.config.topics.topological_goal:
                self._goal_publishers['topological'] = rospy.Publisher(
                    self.config.topics.topological_goal,
                    PoseStamped,
                    queue_size=10
                )
                logger.info(f"Topological goal publisher created on topic: {self.config.topics.topological_goal}")
            
            # Publisher for point cloud from depth images
            self._point_cloud_publisher = rospy.Publisher(
                self.config.topics.point_cloud,
                PointCloud2,
                queue_size=10
            )
            logger.info(f"Point cloud publisher created on topic: {self.config.topics.point_cloud}")
            
        except Exception as e:
            logger.error(f"Failed to create publishers: {e}", exc_info=True)
            raise

    def _setup_subscribers(self) -> None:
        """
        Set up ROS subscribers for odometry and trajectory.
        
        Requirements: 4.4, 5.1
        """
        try:
            # Subscriber for odometry
            self._odometry_subscriber = rospy.Subscriber(
                self.config.topics.odometry,
                Odometry,
                self._odometry_callback,
                queue_size=10
            )
            logger.info(f"Odometry subscriber created on topic: {self.config.topics.odometry}")
            
            # Subscriber for trajectory (B-spline from Fast-Planner)
            self._trajectory_subscriber = rospy.Subscriber(
                self.config.topics.trajectory,
                Bspline,
                self._trajectory_callback_wrapper,
                queue_size=10
            )
            logger.info(f"Trajectory subscriber created on topic: {self.config.topics.trajectory}")
            
        except Exception as e:
            logger.error(f"Failed to create subscribers: {e}", exc_info=True)
            raise

    def _odometry_callback(self, msg: Odometry) -> None:
        """
        Callback for odometry messages.
        
        Caches the latest odometry message with timestamp for age checking.
        
        Args:
            msg: Odometry message from ROS
            
        Requirements: 5.1, 5.5
        """
        with self._odometry_lock:
            self._latest_odometry = msg
            self._odometry_timestamp = time.time()
            logger.debug(f"Received odometry: pos=({msg.pose.pose.position.x:.2f}, "
                        f"{msg.pose.pose.position.y:.2f}, {msg.pose.pose.position.z:.2f})")

    def _trajectory_callback_wrapper(self, msg: Bspline) -> None:
        """
        Callback for trajectory messages.
        
        Caches the latest trajectory and calls registered callback if present.
        
        Args:
            msg: B-spline trajectory message from Fast-Planner
            
        Requirements: 4.4
        """
        with self._trajectory_lock:
            self._latest_trajectory = msg
            self._trajectory_timestamp = time.time()
            logger.info(f"Received trajectory with {len(msg.pos_pts)} position points")
            
            # Call registered callback if present
            if self._trajectory_callback:
                try:
                    self._trajectory_callback(msg)
                except Exception as e:
                    logger.error(f"Error in trajectory callback: {e}", exc_info=True)

    def publish_goal(self, start: Position, goal: Position, algorithm: str = "kinodynamic") -> bool:
        """
        Publish goal position to Fast-Planner using algorithm-specific topic routing.
        
        Routes the goal to the appropriate ROS topic based on the selected algorithm.
        If no algorithm-specific topic is configured, uses the default goal topic.
        
        Args:
            start: Start position (currently not used by Fast-Planner)
            goal: Goal position to reach
            algorithm: Planning algorithm ("kinodynamic" or "topological")
            
        Returns:
            True if goal published successfully, False otherwise
            
        Requirements: 4.4, 7.3
        """
        if not self._ros_connected or self._goal_publisher is None:
            logger.error("Cannot publish goal: ROS not connected")
            return False
        
        try:
            # Validate algorithm
            if algorithm not in ["kinodynamic", "topological"]:
                logger.error(f"Invalid algorithm: {algorithm}")
                return False
            
            # Select the appropriate publisher based on algorithm
            if algorithm in self._goal_publishers:
                publisher = self._goal_publishers[algorithm]
                topic = self.config.topics.get_goal_topic_for_algorithm(algorithm)
            else:
                publisher = self._goal_publisher
                topic = self.config.topics.goal
            
            # Create PoseStamped message for goal
            goal_msg = PoseStamped()
            goal_msg.header.stamp = rospy.Time.now()
            goal_msg.header.frame_id = "world"
            
            # Set goal position
            goal_msg.pose.position = Point(x=goal.x, y=goal.y, z=goal.z)
            
            # Set neutral orientation (Fast-Planner typically ignores orientation)
            goal_msg.pose.orientation = ROSQuaternion(x=0.0, y=0.0, z=0.0, w=1.0)
            
            # Publish goal to algorithm-specific topic
            publisher.publish(goal_msg)
            logger.info(f"Published goal to {topic} (algorithm={algorithm}): "
                       f"({goal.x:.2f}, {goal.y:.2f}, {goal.z:.2f})")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish goal: {e}", exc_info=True)
            return False

    def get_latest_odometry(self) -> Optional[OdometryResponse]:
        """
        Get the most recent odometry data if available and fresh.
        
        Returns odometry only if it's less than max_odometry_age seconds old.
        
        Returns:
            OdometryResponse if fresh odometry available, None otherwise
            
        Requirements: 5.2, 5.3, 5.4, 5.5
        """
        with self._odometry_lock:
            if self._latest_odometry is None or self._odometry_timestamp is None:
                logger.debug("No odometry data available")
                return None
            
            # Check if odometry is too old
            age = time.time() - self._odometry_timestamp
            if age > self._max_odometry_age:
                logger.warning(f"Odometry data is stale (age: {age:.2f}s)")
                return None
            
            # Convert ROS Odometry message to OdometryResponse
            try:
                odom = self._latest_odometry
                response = OdometryResponse(
                    timestamp=odom.header.stamp.to_sec(),
                    position=Position(
                        x=odom.pose.pose.position.x,
                        y=odom.pose.pose.position.y,
                        z=odom.pose.pose.position.z
                    ),
                    orientation=Quaternion(
                        x=odom.pose.pose.orientation.x,
                        y=odom.pose.pose.orientation.y,
                        z=odom.pose.pose.orientation.z,
                        w=odom.pose.pose.orientation.w
                    ),
                    linear_velocity=Position(
                        x=odom.twist.twist.linear.x,
                        y=odom.twist.twist.linear.y,
                        z=odom.twist.twist.linear.z
                    ),
                    angular_velocity=Position(
                        x=odom.twist.twist.angular.x,
                        y=odom.twist.twist.angular.y,
                        z=odom.twist.twist.angular.z
                    )
                )
                return response
            except Exception as e:
                logger.error(f"Failed to convert odometry message: {e}", exc_info=True)
                return None

    def get_odometry_age_ms(self) -> Optional[float]:
        """
        Get the age of the most recent odometry message in milliseconds.
        
        Returns:
            Age in milliseconds if odometry available, None otherwise
            
        Requirements: 6.5
        """
        with self._odometry_lock:
            if self._odometry_timestamp is None:
                return None
            age_seconds = time.time() - self._odometry_timestamp
            return age_seconds * 1000.0

    def wait_for_trajectory(self, timeout: float = 5.0) -> Optional[Bspline]:
        """
        Wait for a new trajectory message from Fast-Planner.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            B-spline trajectory message if received, None if timeout
            
        Requirements: 4.4
        """
        start_time = time.time()
        initial_timestamp = self._trajectory_timestamp
        
        while time.time() - start_time < timeout:
            with self._trajectory_lock:
                # Check if we received a new trajectory
                if (self._trajectory_timestamp is not None and 
                    self._trajectory_timestamp != initial_timestamp):
                    logger.info("New trajectory received")
                    return self._latest_trajectory
            
            # Sleep briefly to avoid busy waiting
            time.sleep(0.01)
        
        logger.warning(f"Trajectory wait timeout after {timeout}s")
        return None

    def register_trajectory_callback(self, callback: Callable[[Bspline], None]) -> None:
        """
        Register a callback to be called when trajectory is received.
        
        Args:
            callback: Function to call with trajectory message
        """
        self._trajectory_callback = callback
        logger.info("Trajectory callback registered")

    def check_planner_status(self) -> bool:
        """
        Check if Fast-Planner node is available and responding.
        
        Checks if the trajectory topic has active publishers, which indicates
        Fast-Planner is running.
        
        Returns:
            True if Fast-Planner appears to be running, False otherwise
            
        Requirements: 6.2, 6.3
        """
        if not self._ros_connected:
            return False
        
        try:
            # Check if trajectory topic has publishers
            topic_info = rospy.get_published_topics()
            trajectory_topic = self.config.topics.trajectory
            
            for topic, msg_type in topic_info:
                if topic == trajectory_topic:
                    logger.debug(f"Fast-Planner topic {trajectory_topic} is being published")
                    return True
            
            logger.warning(f"Fast-Planner topic {trajectory_topic} not found in published topics")
            return False
            
        except Exception as e:
            logger.error(f"Failed to check planner status: {e}", exc_info=True)
            return False

    def is_connected(self) -> bool:
        """
        Check if ROS connection is active.
        
        Returns:
            True if connected to ROS, False otherwise
            
        Requirements: 4.4, 6.4
        """
        if not self._ros_connected:
            return False
        
        try:
            # Check if ROS master is still reachable
            return self._check_ros_master()
        except Exception:
            return False

    def publish_point_cloud(
        self, 
        points: np.ndarray, 
        frame_id: str = "map", 
        timestamp: Optional[float] = None
    ) -> bool:
        """
        Publish point cloud to ROS topic for Fast-Planner consumption.
        
        Converts numpy array of 3D points to sensor_msgs/PointCloud2 message
        and publishes to the configured point cloud topic.
        
        Args:
            points: Numpy array of shape (N, 3) containing XYZ coordinates
            frame_id: Frame ID for the point cloud (default: "map")
            timestamp: Timestamp for the point cloud (default: current time)
            
        Returns:
            True if point cloud published successfully, False otherwise
            
        Requirements: 10.5, 12.5, 13.4
        """
        if not self._ros_connected or self._point_cloud_publisher is None:
            logger.error("Cannot publish point cloud: ROS not connected")
            return False
        
        try:
            # Validate input
            if not isinstance(points, np.ndarray):
                logger.error("Points must be a numpy array")
                return False
            
            if points.ndim != 2 or points.shape[1] != 3:
                logger.error(f"Points must have shape (N, 3), got {points.shape}")
                return False
            
            if points.shape[0] == 0:
                logger.warning("Empty point cloud, skipping publish")
                return True
            
            # Create PointCloud2 message
            msg = self._create_pointcloud2_message(points, frame_id, timestamp)
            
            # Publish the message
            self._point_cloud_publisher.publish(msg)
            
            logger.info(f"Published point cloud with {points.shape[0]} points to {self.config.topics.point_cloud}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish point cloud: {e}", exc_info=True)
            return False

    def _create_pointcloud2_message(
        self,
        points: np.ndarray,
        frame_id: str,
        timestamp: Optional[float] = None
    ) -> PointCloud2:
        """
        Create a PointCloud2 message from numpy array of points.
        
        Args:
            points: Numpy array of shape (N, 3) containing XYZ coordinates
            frame_id: Frame ID for the point cloud
            timestamp: Timestamp for the point cloud (default: current time)
            
        Returns:
            PointCloud2 message
        """
        # Create header
        header = Header()
        header.frame_id = frame_id
        
        if timestamp is not None:
            # Convert float timestamp to ROS Time
            header.stamp = rospy.Time.from_sec(timestamp)
        else:
            header.stamp = rospy.Time.now()
        
        # Define point cloud fields (X, Y, Z as float32)
        fields = [
            PointField(
                name='x',
                offset=0,
                datatype=PointField.FLOAT32,
                count=1
            ),
            PointField(
                name='y',
                offset=4,
                datatype=PointField.FLOAT32,
                count=1
            ),
            PointField(
                name='z',
                offset=8,
                datatype=PointField.FLOAT32,
                count=1
            )
        ]
        
        # Convert points to binary data
        # Each point is 3 float32 values (12 bytes total)
        points_float32 = points.astype(np.float32)
        cloud_data = points_float32.tobytes()
        
        # Create PointCloud2 message
        msg = PointCloud2()
        msg.header = header
        msg.height = 1  # Unorganized point cloud
        msg.width = points.shape[0]
        msg.fields = fields
        msg.is_bigendian = False
        msg.point_step = 12  # 3 floats * 4 bytes
        msg.row_step = msg.point_step * msg.width
        msg.data = cloud_data
        msg.is_dense = True  # No invalid points (already filtered)
        
        return msg

    def shutdown(self) -> None:
        """
        Gracefully shutdown ROS bridge and cleanup resources.
        
        Unregisters subscribers and publishers, and marks connection as closed.
        
        Requirements: 4.5
        """
        logger.info("Shutting down ROS Bridge")
        
        try:
            # Unregister subscribers
            if self._odometry_subscriber:
                self._odometry_subscriber.unregister()
                logger.info("Odometry subscriber unregistered")
            
            if self._trajectory_subscriber:
                self._trajectory_subscriber.unregister()
                logger.info("Trajectory subscriber unregistered")
            
            # Unregister publishers
            if self._goal_publisher:
                self._goal_publisher.unregister()
                logger.info("Goal publisher unregistered")
            
            # Unregister algorithm-specific publishers
            for algorithm, publisher in self._goal_publishers.items():
                publisher.unregister()
                logger.info(f"{algorithm} goal publisher unregistered")
            
            # Unregister point cloud publisher
            if self._point_cloud_publisher:
                self._point_cloud_publisher.unregister()
                logger.info("Point cloud publisher unregistered")
            
            self._ros_connected = False
            logger.info("ROS Bridge shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during ROS Bridge shutdown: {e}", exc_info=True)

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()
