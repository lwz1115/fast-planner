"""
ROS2 Bridge component for FastAPI-Fast-Planner Interface.

This module handles all ROS2 communication including:
- ROS2 node initialization and lifecycle management
- Odometry subscription with message caching
- Goal publishing to Fast-Planner
- Trajectory subscription from Fast-Planner
- Connection validation and status checking

Converted from ROS1 (rospy) to ROS2 (rclpy)
"""

import logging
import threading
import time
from typing import Optional, Callable, Dict, TYPE_CHECKING, Any

# 使用 TYPE_CHECKING 避免运行时导入错误
if TYPE_CHECKING:
    from nav_msgs.msg import Odometry
    from geometry_msgs.msg import PoseStamped
    from sensor_msgs.msg import PointCloud2
    from plan_manage.msg import Bspline

try:
    import rclpy
    from rclpy.node import Node
    from rclpy.executors import MultiThreadedExecutor
    from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
    from nav_msgs.msg import Odometry
    from geometry_msgs.msg import PoseStamped, Point, Quaternion as ROSQuaternion
    from sensor_msgs.msg import PointCloud2, PointField
    from std_msgs.msg import Header
    import struct
    import numpy as np

    # 尝试导入自定义消息
    try:
        from plan_manage.msg import Bspline
        BSPLINE_AVAILABLE = True
    except ImportError:
        BSPLINE_AVAILABLE = False
        logging.warning("plan_manage.msg.Bspline not available")

    ROS_AVAILABLE = True
except ImportError as e:
    ROS_AVAILABLE = False
    BSPLINE_AVAILABLE = False
    logging.warning(f"ROS2 packages not available: {e}")

    # 定义占位符类型
    Node = Any
    MultiThreadedExecutor = Any
    Odometry = Any
    PoseStamped = Any
    PointCloud2 = Any
    Bspline = Any

from config import ROSConfig
from models import Position, Quaternion, OdometryResponse


logger = logging.getLogger(__name__)


class ROSBridgeNode(Node):
    """
    ROS2 Node for ROSBridge.

    Separated from ROSBridge class to follow ROS2 best practices.
    """

    def __init__(self, config: ROSConfig):
        super().__init__(config.node_name)
        self.config = config

        # QoS 配置
        self.qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        # 数据缓存
        self._latest_odometry: Optional[Odometry] = None
        self._odometry_timestamp: Optional[float] = None
        self._odometry_lock = threading.Lock()

        self._latest_trajectory: Optional['Bspline'] = None
        self._trajectory_timestamp: Optional[float] = None
        self._trajectory_lock = threading.Lock()

        # 回调函数
        self._trajectory_callback: Optional[Callable] = None

        # 创建发布者
        self._setup_publishers()

        # 创建订阅者
        self._setup_subscribers()

        self.get_logger().info(f"ROSBridgeNode initialized: {config.node_name}")

    def _setup_publishers(self) -> None:
        """设置 ROS2 发布者"""
        try:
            # 默认目标发布者
            self._goal_publisher = self.create_publisher(
                PoseStamped,
                self.config.topics.goal,
                self.qos_profile
            )
            self.get_logger().info(f"Goal publisher created: {self.config.topics.goal}")

            # 算法特定的发布者
            self._goal_publishers: Dict[str, any] = {}

            if self.config.topics.kinodynamic_goal:
                self._goal_publishers['kinodynamic'] = self.create_publisher(
                    PoseStamped,
                    self.config.topics.kinodynamic_goal,
                    self.qos_profile
                )
                self.get_logger().info(f"Kinodynamic goal publisher: {self.config.topics.kinodynamic_goal}")

            if self.config.topics.topological_goal:
                self._goal_publishers['topological'] = self.create_publisher(
                    PoseStamped,
                    self.config.topics.topological_goal,
                    self.qos_profile
                )
                self.get_logger().info(f"Topological goal publisher: {self.config.topics.topological_goal}")

            # 点云发布者
            self._point_cloud_publisher = self.create_publisher(
                PointCloud2,
                self.config.topics.point_cloud,
                self.qos_profile
            )
            self.get_logger().info(f"Point cloud publisher: {self.config.topics.point_cloud}")

        except Exception as e:
            self.get_logger().error(f"Failed to create publishers: {e}")
            raise

    def _setup_subscribers(self) -> None:
        """设置 ROS2 订阅者"""
        try:
            # 里程计订阅者
            self._odometry_subscriber = self.create_subscription(
                Odometry,
                self.config.topics.odometry,
                self._odometry_callback,
                self.qos_profile
            )
            self.get_logger().info(f"Odometry subscriber: {self.config.topics.odometry}")

            # 轨迹订阅者（如果 Bspline 消息可用）
            if BSPLINE_AVAILABLE:
                self._trajectory_subscriber = self.create_subscription(
                    Bspline,
                    self.config.topics.trajectory,
                    self._trajectory_callback_wrapper,
                    self.qos_profile
                )
                self.get_logger().info(f"Trajectory subscriber: {self.config.topics.trajectory}")
            else:
                self.get_logger().warning("Bspline message not available, trajectory subscription disabled")

        except Exception as e:
            self.get_logger().error(f"Failed to create subscribers: {e}")
            raise

    def _odometry_callback(self, msg: Odometry) -> None:
        """里程计回调函数"""
        with self._odometry_lock:
            self._latest_odometry = msg
            self._odometry_timestamp = time.time()
            self.get_logger().debug(
                f"Odometry: pos=({msg.pose.pose.position.x:.2f}, "
                f"{msg.pose.pose.position.y:.2f}, {msg.pose.pose.position.z:.2f})"
            )

    def _trajectory_callback_wrapper(self, msg: 'Bspline') -> None:
        """轨迹回调包装函数"""
        with self._trajectory_lock:
            self._latest_trajectory = msg
            self._trajectory_timestamp = time.time()
            self.get_logger().debug("Received trajectory")

        # 调用外部回调
        if self._trajectory_callback:
            try:
                self._trajectory_callback(msg)
            except Exception as e:
                self.get_logger().error(f"Trajectory callback error: {e}")

    def get_latest_odometry(self, max_age: float = 1.0) -> Optional[Odometry]:
        """获取最新里程计数据"""
        with self._odometry_lock:
            if self._latest_odometry is None:
                return None

            age = time.time() - self._odometry_timestamp
            if age > max_age:
                self.get_logger().warning(f"Odometry data too old: {age:.2f}s")
                return None

            return self._latest_odometry

    def publish_goal(self, goal: PoseStamped, algorithm: str = "kinodynamic") -> bool:
        """发布目标位置"""
        try:
            # 选择发布者
            if algorithm in self._goal_publishers:
                publisher = self._goal_publishers[algorithm]
                self.get_logger().info(f"Publishing goal to {algorithm} topic")
            else:
                publisher = self._goal_publisher
                self.get_logger().info("Publishing goal to default topic")

            # 发布消息
            publisher.publish(goal)

            # 等待消息发送
            time.sleep(0.1)
            return True

        except Exception as e:
            self.get_logger().error(f"Failed to publish goal: {e}")
            return False

    def publish_point_cloud(self, cloud: PointCloud2) -> bool:
        """发布点云"""
        try:
            self._point_cloud_publisher.publish(cloud)
            return True
        except Exception as e:
            self.get_logger().error(f"Failed to publish point cloud: {e}")
            return False

    def set_trajectory_callback(self, callback: Callable) -> None:
        """设置轨迹回调函数"""
        self._trajectory_callback = callback

    def check_planner_status(self) -> bool:
        """检查Fast-Planner是否可用（通过检查goal topic是否有订阅者）"""
        try:
            count = self._goal_publisher.get_subscription_count()
            return count > 0
        except Exception:
            return False

    def get_odometry_age_ms(self) -> Optional[float]:
        """获取里程计数据的年龄（毫秒）"""
        with self._odometry_lock:
            if self._odometry_timestamp is None:
                return None
            return (time.time() - self._odometry_timestamp) * 1000.0


class ROSBridge:
    """
    Bridge between FastAPI service and ROS2 Fast-Planner system.

    Manages ROS2 node lifecycle, subscribes to odometry and trajectory topics,
    publishes goal positions, and provides connection status checking.
    """

    def __init__(self, config: ROSConfig):
        """
        Initialize ROS Bridge with configuration.

        Args:
            config: ROS configuration including topics and node name
        """
        if not ROS_AVAILABLE:
            raise RuntimeError("ROS2 packages are not available. Cannot initialize ROSBridge.")

        self.config = config
        self._node: Optional[ROSBridgeNode] = None
        self._executor: Optional[MultiThreadedExecutor] = None
        self._spin_thread: Optional[threading.Thread] = None
        self._ros_connected = False
        self._max_odometry_age = 5.0  # seconds

        logger.info(f"ROSBridge initialized with config: {config.dict()}")

    def connect(self) -> bool:
        """
        Initialize ROS2 node and establish connections.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # 初始化 rclpy（如果还没初始化）
            if not rclpy.ok():
                rclpy.init()
                logger.info("rclpy initialized")

            # 创建节点
            self._node = ROSBridgeNode(self.config)
            logger.info(f"ROS2 node created: {self.config.node_name}")

            # 创建多线程执行器
            self._executor = MultiThreadedExecutor()
            self._executor.add_node(self._node)

            # 在后台线程中运行 spin
            self._spin_thread = threading.Thread(
                target=self._executor.spin,
                daemon=True
            )
            self._spin_thread.start()
            logger.info("ROS2 executor started in background thread")

            self._ros_connected = True
            logger.info("ROS Bridge connected successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to connect ROS Bridge: {e}", exc_info=True)
            self._ros_connected = False
            return False

    def disconnect(self) -> None:
        """
        Disconnect and cleanup ROS2 resources.
        """
        try:
            logger.info("Disconnecting ROS Bridge...")

            if self._executor:
                self._executor.shutdown()
                logger.info("Executor shutdown")

            if self._node:
                self._node.destroy_node()
                logger.info("Node destroyed")

            if rclpy.ok():
                rclpy.shutdown()
                logger.info("rclpy shutdown")

            self._ros_connected = False
            logger.info("ROS Bridge disconnected")

        except Exception as e:
            logger.error(f"Error during disconnect: {e}", exc_info=True)

    def is_connected(self) -> bool:
        """
        Check if ROS Bridge is connected.

        Returns:
            True if connected, False otherwise
        """
        return self._ros_connected and rclpy.ok()

    def get_odometry(self) -> Optional[OdometryResponse]:
        """
        Get latest odometry data.

        Returns:
            OdometryResponse if available and fresh, None otherwise
        """
        if not self._node:
            return None

        odom_msg = self._node.get_latest_odometry(self._max_odometry_age)
        if not odom_msg:
            return None

        # 转换为 OdometryResponse
        return OdometryResponse(
            timestamp=time.time(),
            position=Position(
                x=odom_msg.pose.pose.position.x,
                y=odom_msg.pose.pose.position.y,
                z=odom_msg.pose.pose.position.z
            ),
            orientation=Quaternion(
                x=odom_msg.pose.pose.orientation.x,
                y=odom_msg.pose.pose.orientation.y,
                z=odom_msg.pose.pose.orientation.z,
                w=odom_msg.pose.pose.orientation.w
            ),
            linear_velocity=Position(
                x=odom_msg.twist.twist.linear.x,
                y=odom_msg.twist.twist.linear.y,
                z=odom_msg.twist.twist.linear.z
            ),
            angular_velocity=Position(
                x=odom_msg.twist.twist.angular.x,
                y=odom_msg.twist.twist.angular.y,
                z=odom_msg.twist.twist.angular.z
            )
        )

    def get_latest_odometry(self) -> Optional[OdometryResponse]:
        """get_odometry的别名，兼容main.py的调用"""
        return self.get_odometry()

    def publish_goal(self, goal: Position, algorithm: str = "kinodynamic",
                    frame_id: str = "world", start: Optional[Position] = None) -> bool:
        """
        Publish goal position to Fast-Planner.

        Args:
            goal: Goal position
            algorithm: Planning algorithm ("kinodynamic" or "topological")
            frame_id: Reference frame
            start: Start position (ignored, Fast-Planner uses its own odometry)

        Returns:
            True if published successfully, False otherwise
        """
        if not self._node:
            logger.error("Node not initialized")
            return False

        try:
            # 创建 PoseStamped 消息
            goal_msg = PoseStamped()
            goal_msg.header.stamp = self._node.get_clock().now().to_msg()
            goal_msg.header.frame_id = frame_id

            goal_msg.pose.position.x = goal.x
            goal_msg.pose.position.y = goal.y
            goal_msg.pose.position.z = goal.z

            # 默认朝向（yaw=0）
            goal_msg.pose.orientation.x = 0.0
            goal_msg.pose.orientation.y = 0.0
            goal_msg.pose.orientation.z = 0.0
            goal_msg.pose.orientation.w = 1.0

            # 发布
            return self._node.publish_goal(goal_msg, algorithm)

        except Exception as e:
            logger.error(f"Failed to publish goal: {e}", exc_info=True)
            return False

    def publish_point_cloud(self, points: np.ndarray, frame_id: str = "world") -> bool:
        """
        Publish point cloud from depth image.

        Args:
            points: Nx3 numpy array of points
            frame_id: Reference frame

        Returns:
            True if published successfully, False otherwise
        """
        if not self._node:
            logger.error("Node not initialized")
            return False

        try:
            # 创建 PointCloud2 消息
            cloud_msg = PointCloud2()
            cloud_msg.header.stamp = self._node.get_clock().now().to_msg()
            cloud_msg.header.frame_id = frame_id

            cloud_msg.height = 1
            cloud_msg.width = len(points)
            cloud_msg.is_dense = False
            cloud_msg.is_bigendian = False

            # 定义字段
            cloud_msg.fields = [
                PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
                PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
                PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1),
            ]

            cloud_msg.point_step = 12  # 3 * 4 bytes
            cloud_msg.row_step = cloud_msg.point_step * cloud_msg.width

            # 打包数据
            cloud_data = []
            for point in points:
                cloud_data.append(struct.pack('fff', point[0], point[1], point[2]))

            cloud_msg.data = b''.join(cloud_data)

            # 发布
            return self._node.publish_point_cloud(cloud_msg)

        except Exception as e:
            logger.error(f"Failed to publish point cloud: {e}", exc_info=True)
            return False

    def set_trajectory_callback(self, callback: Callable) -> None:
        """
        Set callback function for trajectory updates.

        Args:
            callback: Function to call when trajectory is received
        """
        if self._node:
            self._node.set_trajectory_callback(callback)

    def check_planner_status(self) -> bool:
        """检查Fast-Planner规划器是否可用"""
        if not self._node:
            return False
        return self._node.check_planner_status()

    def get_odometry_age_ms(self) -> Optional[float]:
        """获取里程计数据年龄（毫秒）"""
        if not self._node:
            return None
        return self._node.get_odometry_age_ms()

