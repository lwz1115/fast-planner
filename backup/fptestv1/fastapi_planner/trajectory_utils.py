"""
Trajectory utilities for B-spline conversion and evaluation.

This module provides functions to evaluate B-spline trajectories and convert
them from ROS plan_manage/Bspline messages to waypoint lists with position,
velocity, and acceleration at regular time intervals.

Requirements: 2.1, 2.3, 2.4, 2.5
"""

import logging
from typing import List, Tuple
import numpy as np

try:
    from plan_manage.msg import Bspline
    from geometry_msgs.msg import Point
    ROS_AVAILABLE = True
except ImportError:
    ROS_AVAILABLE = False
    logging.warning("ROS packages not available. Trajectory conversion will not function.")

from models import Waypoint, Trajectory, Position


logger = logging.getLogger(__name__)


class BsplineEvaluator:
    """
    Evaluates non-uniform B-spline trajectories for position, velocity, and acceleration.
    
    Implements the De Boor algorithm for B-spline evaluation and computes derivatives
    by evaluating derivative B-splines.
    """
    
    def __init__(self, control_points: np.ndarray, order: int, knots: np.ndarray):
        """
        Initialize B-spline evaluator.
        
        Args:
            control_points: Nx3 array of control points (N points in 3D space)
            order: B-spline order (degree + 1), typically 3 for quadratic or 4 for cubic
            knots: Knot vector for non-uniform B-spline
        """
        self.control_points = control_points
        self.order = order
        self.knots = knots
        self.p = order  # Degree is order
        self.n = len(control_points) - 1  # Number of control points - 1
        self.m = self.n + self.p + 1  # Number of knots - 1
        
        # Validate inputs
        if len(knots) != self.m + 1:
            raise ValueError(
                f"Invalid knot vector length. Expected {self.m + 1}, got {len(knots)}"
            )
        
        logger.debug(f"BsplineEvaluator initialized: {len(control_points)} control points, "
                    f"order={order}, {len(knots)} knots")
    
    def get_time_span(self) -> Tuple[float, float]:
        """
        Get the valid time span for B-spline evaluation.
        
        Returns:
            Tuple of (start_time, end_time) in the knot vector
        """
        u_min = self.knots[self.p]
        u_max = self.knots[self.m - self.p]
        return u_min, u_max
    
    def evaluate_de_boor(self, u: float) -> np.ndarray:
        """
        Evaluate B-spline at parameter u using De Boor's algorithm.
        
        Args:
            u: Parameter value to evaluate at
            
        Returns:
            3D position as numpy array [x, y, z]
            
        Requirements: 2.1
        """
        # Clamp u to valid range
        u_min, u_max = self.get_time_span()
        u_clamped = np.clip(u, u_min, u_max)
        
        # Find knot span: determine which [u_k, u_{k+1}] contains u
        k = self.p
        while k < self.m - self.p:
            if self.knots[k + 1] >= u_clamped:
                break
            k += 1
        
        # De Boor's algorithm
        # Initialize with p+1 control points
        d = []
        for i in range(self.p + 1):
            idx = k - self.p + i
            if idx < 0 or idx >= len(self.control_points):
                logger.warning(f"Control point index {idx} out of bounds")
                idx = np.clip(idx, 0, len(self.control_points) - 1)
            d.append(self.control_points[idx].copy())
        
        # Recursive evaluation
        for r in range(1, self.p + 1):
            for i in range(self.p, r - 1, -1):
                knot_idx_left = i + k - self.p
                knot_idx_right = i + 1 + k - r
                
                # Avoid division by zero
                denominator = self.knots[knot_idx_right] - self.knots[knot_idx_left]
                if abs(denominator) < 1e-10:
                    alpha = 0.5
                else:
                    alpha = (u_clamped - self.knots[knot_idx_left]) / denominator
                
                d[i] = (1 - alpha) * d[i - 1] + alpha * d[i]
        
        return d[self.p]
    
    def get_derivative_control_points(self) -> np.ndarray:
        """
        Compute control points for the derivative B-spline.
        
        The derivative of a B-spline is also a B-spline with order p-1.
        Control point Q_i = p * (P_{i+1} - P_i) / (u_{i+p+1} - u_{i+1})
        
        Returns:
            (N-1)x3 array of derivative control points
        """
        n_derivative_points = len(self.control_points) - 1
        derivative_points = np.zeros((n_derivative_points, 3))
        
        for i in range(n_derivative_points):
            denominator = self.knots[i + self.p + 1] - self.knots[i + 1]
            if abs(denominator) < 1e-10:
                # Avoid division by zero
                derivative_points[i] = np.zeros(3)
            else:
                derivative_points[i] = (
                    self.p * (self.control_points[i + 1] - self.control_points[i]) / denominator
                )
        
        return derivative_points
    
    def get_derivative(self) -> 'BsplineEvaluator':
        """
        Get B-spline evaluator for the derivative.
        
        Returns:
            BsplineEvaluator for the derivative B-spline
        """
        derivative_control_points = self.get_derivative_control_points()
        
        # Derivative knot vector: remove first and last knot
        derivative_knots = self.knots[1:-1]
        
        return BsplineEvaluator(
            derivative_control_points,
            self.order - 1,
            derivative_knots
        )
    
    def evaluate_with_derivatives(self, u: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Evaluate B-spline position, velocity, and acceleration at parameter u.
        
        Args:
            u: Parameter value to evaluate at
            
        Returns:
            Tuple of (position, velocity, acceleration) as numpy arrays
            
        Requirements: 2.1
        """
        # Evaluate position
        position = self.evaluate_de_boor(u)
        
        # Evaluate velocity (first derivative)
        if self.order > 1:
            velocity_bspline = self.get_derivative()
            velocity = velocity_bspline.evaluate_de_boor(u)
        else:
            velocity = np.zeros(3)
        
        # Evaluate acceleration (second derivative)
        if self.order > 2:
            acceleration_bspline = velocity_bspline.get_derivative()
            acceleration = acceleration_bspline.evaluate_de_boor(u)
        else:
            acceleration = np.zeros(3)
        
        return position, velocity, acceleration


def convert_bspline_to_trajectory(
    bspline_msg: 'Bspline',
    sample_rate: float = 10.0
) -> Trajectory:
    """
    Convert ROS plan_manage/Bspline message to Trajectory with waypoints.
    
    Samples the B-spline trajectory at regular intervals (default 10 Hz) and
    evaluates position, velocity, and acceleration at each sample point.
    
    Args:
        bspline_msg: ROS Bspline message from Fast-Planner
        sample_rate: Sampling frequency in Hz (default 10.0 for 0.1s intervals)
        
    Returns:
        Trajectory object with sampled waypoints
        
    Raises:
        ValueError: If B-spline message is invalid or empty
        
    Requirements: 2.1, 2.3, 2.4, 2.5
    """
    if not ROS_AVAILABLE:
        raise RuntimeError("ROS packages not available. Cannot convert B-spline trajectory.")
    
    # Validate input
    if not bspline_msg.pos_pts:
        raise ValueError("B-spline message has no position control points")
    
    if not bspline_msg.knots:
        raise ValueError("B-spline message has no knot vector")
    
    logger.info(f"Converting B-spline trajectory: {len(bspline_msg.pos_pts)} control points, "
               f"order={bspline_msg.order}, sample_rate={sample_rate} Hz")
    
    # Convert control points from ROS Point messages to numpy array
    control_points = np.array([
        [pt.x, pt.y, pt.z] for pt in bspline_msg.pos_pts
    ])
    
    # Convert knots to numpy array
    knots = np.array(bspline_msg.knots)
    
    # Create B-spline evaluator
    try:
        evaluator = BsplineEvaluator(control_points, bspline_msg.order, knots)
    except Exception as e:
        logger.error(f"Failed to create B-spline evaluator: {e}")
        raise ValueError(f"Invalid B-spline parameters: {e}")
    
    # Get time span
    u_min, u_max = evaluator.get_time_span()
    duration = u_max - u_min
    
    if duration <= 0:
        raise ValueError(f"Invalid trajectory duration: {duration}")
    
    logger.debug(f"Trajectory time span: [{u_min:.3f}, {u_max:.3f}], duration={duration:.3f}s")
    
    # Sample trajectory at specified rate
    sample_interval = 1.0 / sample_rate  # seconds
    num_samples = int(np.ceil(duration / sample_interval)) + 1
    
    waypoints = []
    for i in range(num_samples):
        # Calculate time relative to trajectory start
        t = i * sample_interval
        
        # Don't exceed trajectory duration
        if t > duration:
            t = duration
        
        # Evaluate B-spline at this time
        u = u_min + t
        try:
            pos, vel, acc = evaluator.evaluate_with_derivatives(u)
            
            waypoint = Waypoint(
                timestamp=t,
                position=Position(x=float(pos[0]), y=float(pos[1]), z=float(pos[2])),
                velocity=Position(x=float(vel[0]), y=float(vel[1]), z=float(vel[2])),
                acceleration=Position(x=float(acc[0]), y=float(acc[1]), z=float(acc[2]))
            )
            waypoints.append(waypoint)
            
        except Exception as e:
            logger.error(f"Failed to evaluate B-spline at t={t:.3f}: {e}")
            raise ValueError(f"B-spline evaluation failed at t={t:.3f}: {e}")
        
        # Stop if we've reached the end
        if t >= duration:
            break
    
    # Validate monotonically increasing timestamps (should be guaranteed by construction)
    for i in range(1, len(waypoints)):
        if waypoints[i].timestamp <= waypoints[i-1].timestamp:
            raise ValueError(
                f"Timestamps not monotonically increasing at index {i}: "
                f"{waypoints[i].timestamp} <= {waypoints[i-1].timestamp}"
            )
    
    logger.info(f"Generated trajectory with {len(waypoints)} waypoints, "
               f"duration={duration:.3f}s")
    
    # Create and return Trajectory object
    trajectory = Trajectory(
        waypoints=waypoints,
        total_duration=duration,
        num_waypoints=len(waypoints)
    )
    
    return trajectory


def validate_trajectory(trajectory: Trajectory) -> bool:
    """
    Validate that a trajectory meets all requirements.
    
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
        # Check waypoint count
        if len(trajectory.waypoints) < 1:
            logger.error("Trajectory has no waypoints")
            return False
        
        if len(trajectory.waypoints) != trajectory.num_waypoints:
            logger.error(
                f"Waypoint count mismatch: {len(trajectory.waypoints)} != {trajectory.num_waypoints}"
            )
            return False
        
        # Check duration
        if trajectory.total_duration <= 0:
            logger.error(f"Invalid duration: {trajectory.total_duration}")
            return False
        
        # Check monotonically increasing timestamps
        for i in range(1, len(trajectory.waypoints)):
            if trajectory.waypoints[i].timestamp <= trajectory.waypoints[i-1].timestamp:
                logger.error(
                    f"Timestamps not monotonically increasing at index {i}: "
                    f"{trajectory.waypoints[i].timestamp} <= {trajectory.waypoints[i-1].timestamp}"
                )
                return False
        
        # Check first timestamp is 0 or close to 0
        if abs(trajectory.waypoints[0].timestamp) > 1e-6:
            logger.warning(f"First timestamp is not 0: {trajectory.waypoints[0].timestamp}")
        
        # Check last timestamp matches duration
        last_timestamp = trajectory.waypoints[-1].timestamp
        if abs(last_timestamp - trajectory.total_duration) > 1e-3:
            logger.warning(
                f"Last timestamp {last_timestamp} doesn't match duration {trajectory.total_duration}"
            )
        
        logger.debug("Trajectory validation passed")
        return True
        
    except Exception as e:
        logger.error(f"Trajectory validation error: {e}", exc_info=True)
        return False
