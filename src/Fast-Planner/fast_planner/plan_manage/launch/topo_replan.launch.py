#!/usr/bin/env python3
"""
ROS2 Launch文件 - Topological规划
启动Fast-Planner的拓扑路径规划仿真
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    map_size_x_arg = DeclareLaunchArgument('map_size_x', default_value='40.0')
    map_size_y_arg = DeclareLaunchArgument('map_size_y', default_value='20.0')
    map_size_z_arg = DeclareLaunchArgument('map_size_z', default_value='5.0')
    odom_topic_arg = DeclareLaunchArgument('odom_topic', default_value='/visual_slam/odom')

    map_size_x = LaunchConfiguration('map_size_x')
    map_size_y = LaunchConfiguration('map_size_y')
    map_size_z = LaunchConfiguration('map_size_z')
    odom_topic = LaunchConfiguration('odom_topic')

    fast_planner_node = Node(
        package='plan_manage',
        executable='fast_planner_node',
        name='fast_planner_node',
        output='screen',
        parameters=[{
            'planner_node/planner': 2,  # 2: Topological

            'fsm/flight_type': 1,
            'fsm/thresh_replan': 0.5,
            'fsm/thresh_no_replan': 2.0,
            'fsm/waypoint_num': 0,
            'fsm/planning_horizon': 7.5,
            'fsm/planning_horizen_time': 3.0,
            'fsm/emergency_time': 1.0,
            'fsm/realworld_experiment': False,
            'fsm/fail_safe': True,

            'sdf_map/resolution': 0.1,
            'sdf_map/map_size_x': map_size_x,
            'sdf_map/map_size_y': map_size_y,
            'sdf_map/map_size_z': map_size_z,
            'sdf_map/local_update_range_x': 5.5,
            'sdf_map/local_update_range_y': 5.5,
            'sdf_map/local_update_range_z': 4.5,
            'sdf_map/obstacles_inflation': 0.099,
            'sdf_map/local_bound_inflate': 0.5,
            'sdf_map/local_map_margin': 50,
            'sdf_map/ground_height': -1.0,

            'sdf_map/cx': 321.04638671875,
            'sdf_map/cy': 243.44969177246094,
            'sdf_map/fx': 387.229248046875,
            'sdf_map/fy': 387.229248046875,
            'sdf_map/use_depth_filter': True,
            'sdf_map/depth_filter_tolerance': 0.15,
            'sdf_map/depth_filter_maxdist': 4.5,
            'sdf_map/depth_filter_mindist': 0.2,
            'sdf_map/depth_filter_margin': 2,
            'sdf_map/k_depth_scaling_factor': 1000.0,
            'sdf_map/skip_pixel': 3,

            'sdf_map/p_hit': 0.65,
            'sdf_map/p_miss': 0.35,
            'sdf_map/p_min': 0.12,
            'sdf_map/p_max': 0.90,
            'sdf_map/p_occ': 0.80,
            'sdf_map/min_ray_length': 0.5,
            'sdf_map/max_ray_length': 4.5,

            'sdf_map/esdf_slice_height': 0.3,
            'sdf_map/visualization_truncate_height': 2.5,
            'sdf_map/virtual_ceil_height': 3.0,
            'sdf_map/show_occ_time': False,
            'sdf_map/show_esdf_time': False,
            'sdf_map/pose_type': 1,
            'sdf_map/frame_id': 'world',

            'manager/max_vel': 3.0,
            'manager/max_acc': 2.5,
            'manager/max_jerk': 4.0,
            'manager/dynamic_environment': 0,
            'manager/local_segment_length': 7.0,
            'manager/clearance_threshold': 0.2,
            'manager/control_points_distance': 0.3,
            'manager/use_geometric_path': False,
            'manager/use_kinodynamic_path': False,
            'manager/use_topo_path': True,
            'manager/use_optimization': True,

            # 拓扑PRM参数
            'topo_prm/sample_inflate_x': 1.0,
            'topo_prm/sample_inflate_y': 3.5,
            'topo_prm/sample_inflate_z': 1.0,
            'topo_prm/clearance': 0.3,
            'topo_prm/max_sample_time': 0.005,
            'topo_prm/max_sample_num': 2000,
            'topo_prm/max_raw_path': 300,
            'topo_prm/max_raw_path2': 25,
            'topo_prm/short_cut_num': 1,
            'topo_prm/reserve_num': 6,
            'topo_prm/ratio_to_short': 5.5,
            'topo_prm/parallel_shortcut': True,

            'optimization/lambda1': 10.0,
            'optimization/lambda2': 5.0,
            'optimization/lambda3': 0.0,
            'optimization/lambda4': 0.001,
            'optimization/lambda5': 1.5,
            'optimization/lambda6': 10.0,
            'optimization/lambda7': 20.0,
            'optimization/dist0': 0.4,
            'optimization/max_vel': 3.0,
            'optimization/max_acc': 2.5,
            'optimization/algorithm1': 15,
            'optimization/algorithm2': 11,
            'optimization/max_iteration_num1': 2,
            'optimization/max_iteration_num2': 300,
            'optimization/max_iteration_time1': 0.0001,
            'optimization/max_iteration_time2': 0.005,
            'optimization/order': 3,
        }],
        remappings=[
            ('odometry', odom_topic),
        ]
    )

    traj_server_node = Node(
        package='plan_manage',
        executable='traj_server',
        name='traj_server',
        output='screen',
        parameters=[{
            'traj_server/time_forward': 1.5,
        }],
        remappings=[
            ('position_cmd', '/planning/pos_cmd'),
            ('odom_world', odom_topic),
        ]
    )

    waypoint_generator_node = Node(
        package='waypoint_generator',
        executable='waypoint_generator',
        name='waypoint_generator',
        output='screen',
        parameters=[{
            'waypoint_type': 'manual-lonely-waypoint',
        }],
        remappings=[
            ('odom', odom_topic),
            ('goal', '/move_base_simple/goal'),
            ('traj_start_trigger', '/traj_start_trigger'),
        ]
    )

    simulator_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('so3_quadrotor_simulator'),
                'launch',
                'simulator.launch.py'
            ])
        ]),
        launch_arguments={
            'map_size_x': map_size_x,
            'map_size_y': map_size_y,
            'map_size_z': map_size_z,
            'odom_topic': odom_topic,
        }.items()
    )

    return LaunchDescription([
        map_size_x_arg,
        map_size_y_arg,
        map_size_z_arg,
        odom_topic_arg,
        fast_planner_node,
        traj_server_node,
        waypoint_generator_node,
        simulator_launch,
    ])
