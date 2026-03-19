#!/usr/bin/env python3
"""
ROS2 Launch文件 - Kinodynamic规划
启动Fast-Planner的动力学规划仿真
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
    # 声明参数
    map_size_x_arg = DeclareLaunchArgument('map_size_x', default_value='40.0')
    map_size_y_arg = DeclareLaunchArgument('map_size_y', default_value='20.0')
    map_size_z_arg = DeclareLaunchArgument('map_size_z', default_value='5.0')
    odom_topic_arg = DeclareLaunchArgument('odom_topic', default_value='/visual_slam/odom')
    
    # 获取参数值
    map_size_x = LaunchConfiguration('map_size_x')
    map_size_y = LaunchConfiguration('map_size_y')
    map_size_z = LaunchConfiguration('map_size_z')
    odom_topic = LaunchConfiguration('odom_topic')
    
    # Fast-Planner节点
    fast_planner_node = Node(
        package='plan_manage',
        executable='fast_planner_node',
        name='fast_planner_node',
        output='screen',
        parameters=[{
            'planner_node/planner': 1,  # 1: Kinodynamic, 2: Topological
            'fsm/flight_type': 1,
            'fsm/thresh_replan': 1.0,
            'fsm/thresh_no_replan': 1.0,
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
            'sdf_map/obstacles_inflation': 0.3,
            'sdf_map/local_map_margin': 10,
            'sdf_map/ground_height': -0.01,
            
            'sdf_map/cx': 321.04638671875,
            'sdf_map/cy': 243.44969177246094,
            'sdf_map/fx': 387.229248046875,
            'sdf_map/fy': 387.229248046875,
            'sdf_map/use_depth_filter': True,
            'sdf_map/depth_filter_tolerance': 0.15,
            'sdf_map/depth_filter_maxdist': 5.0,
            'sdf_map/depth_filter_mindist': 0.2,
            'sdf_map/depth_filter_margin': 2,
            'sdf_map/k_depth_scaling_factor': 1000.0,
            'sdf_map/skip_pixel': 2,
            
            'sdf_map/p_hit': 0.65,
            'sdf_map/p_miss': 0.35,
            'sdf_map/p_min': 0.12,
            'sdf_map/p_max': 0.90,
            'sdf_map/p_occ': 0.80,
            'sdf_map/min_ray_length': 0.1,
            'sdf_map/max_ray_length': 4.5,
            
            'sdf_map/visualization_truncate_height': 2.49,
            'sdf_map/virtual_ceil_height': 2.5,
            'sdf_map/show_occ_time': False,
            'sdf_map/pose_type': 1,
            'sdf_map/frame_id': 'world',
            
            'manager/max_vel': 3.0,
            'manager/max_acc': 2.0,
            'manager/max_jerk': 4.0,
            'manager/dynamic_environment': 0,
            'manager/clearance_threshold': 0.2,
            'manager/local_segment_length': 6.0,
            'manager/control_points_distance': 0.4,
            'manager/use_geometric_path': False,
            'manager/use_kinodynamic_path': True,
            'manager/use_topo_path': False,
            'manager/use_optimization': True,
            
            'search/max_tau': 0.6,
            'search/init_max_tau': 0.8,
            'search/max_vel': 3.0,
            'search/max_acc': 2.0,
            'search/w_time': 10.0,
            'search/horizon': 7.0,
            'search/lambda_heu': 5.0,
            'search/resolution_astar': 0.1,
            'search/time_resolution': 0.8,
            'search/margin': 0.3,
            'search/allocate_num': 100000,
            'search/check_num': 5,
            'search/optimistic': False,
            
            'optimization/lambda1': 1.0,
            'optimization/lambda2': 0.5,
            'optimization/lambda3': 0.0001,
            'optimization/lambda4': 0.01,
            'optimization/lambda5': 0.0,
            'optimization/lambda6': 0.0,
            'optimization/lambda7': 0.0,
            'optimization/lambda8': 0.0,
            'optimization/dist0': 0.5,
            'optimization/max_vel': 3.0,
            'optimization/max_acc': 2.0,
            'optimization/visib_min': 0.2,
            'optimization/dlmin': 0.2,
            'optimization/wnl': 0.1,
            'optimization/algorithm1': 15,
            'optimization/algorithm2': 11,
            'optimization/order': 3,
            'optimization/max_iteration_num1': 2,
            'optimization/max_iteration_num2': 300,
            'optimization/max_iteration_num3': 200,
            'optimization/max_iteration_num4': 200,
            'optimization/max_iteration_time1': 0.0001,
            'optimization/max_iteration_time2': 0.005,
            'optimization/max_iteration_time3': 0.003,
            'optimization/max_iteration_time4': 0.003,
        }],
        remappings=[
            ('odometry', odom_topic),
        ]
    )
    
    # 轨迹服务器节点
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
    
    # 航点生成器节点
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
    
    # 包含仿真器launch文件
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


