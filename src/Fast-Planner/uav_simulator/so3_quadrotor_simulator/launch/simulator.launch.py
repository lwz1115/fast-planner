#!/usr/bin/env python3
"""
ROS2 Launch文件 - 完整仿真环境
启动地图生成器、四旋翼仿真器、控制器、传感器和可视化
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
import tempfile
import yaml

def generate_launch_description():
    # 声明参数
    init_x_arg = DeclareLaunchArgument('init_x', default_value='0.0')
    init_y_arg = DeclareLaunchArgument('init_y', default_value='0.0')
    init_z_arg = DeclareLaunchArgument('init_z', default_value='1.0')
    map_size_x_arg = DeclareLaunchArgument('map_size_x', default_value='40.0')
    map_size_y_arg = DeclareLaunchArgument('map_size_y', default_value='20.0')
    map_size_z_arg = DeclareLaunchArgument('map_size_z', default_value='5.0')
    c_num_arg = DeclareLaunchArgument('c_num', default_value='100')
    p_num_arg = DeclareLaunchArgument('p_num', default_value='100')
    odom_topic_arg = DeclareLaunchArgument('odom_topic', default_value='/visual_slam/odom')
    
    def create_nodes(context):
        # 获取参数值
        init_x = context.launch_configurations['init_x']
        init_y = context.launch_configurations['init_y']
        init_z = context.launch_configurations['init_z']
        map_size_x = context.launch_configurations['map_size_x']
        map_size_y = context.launch_configurations['map_size_y']
        map_size_z = context.launch_configurations['map_size_z']
        c_num = context.launch_configurations['c_num']
        p_num = context.launch_configurations['p_num']
        odom_topic = context.launch_configurations['odom_topic']
        
        # 获取包路径
        so3_control_pkg = get_package_share_directory('so3_control')
        local_sensing_pkg = get_package_share_directory('local_sensing_node')
        
        # 创建临时参数文件目录
        tmp_dir = tempfile.mkdtemp()
        
        # 1. 为so3_control创建正确的参数文件
        so3_params = {
            'so3_control': {
                'ros__parameters': {
                    'mass': 0.98,
                    'use_angle_corrections': False,
                    'use_external_yaw': False,
                    'gains': {
                        'rot': {'z': 1.0},
                        'ang': {'z': 0.1}
                    }
                }
            }
        }
        
        so3_param_file = os.path.join(tmp_dir, 'so3_params.yaml')
        with open(so3_param_file, 'w') as f:
            yaml.dump(so3_params, f)
        
        # 2. 为pcl_render_node创建参数文件
        pcl_params = {
            'pcl_render_node': {
                'ros__parameters': {
                    'sensing_horizon': 5.0,
                    'sensing_rate': 30.0,
                    'estimation_rate': 30.0,
                    'map': {
                        'x_size': float(map_size_x),
                        'y_size': float(map_size_y),
                        'z_size': float(map_size_z)
                    },
                    'cam_width': 640,
                    'cam_height': 480,
                    'cam_fx': 387.229248046875,
                    'cam_fy': 387.229248046875,
                    'cam_cx': 321.04638671875,
                    'cam_cy': 243.44969177246094,
                }
            }
        }
        
        pcl_param_file = os.path.join(tmp_dir, 'pcl_params.yaml')
        with open(pcl_param_file, 'w') as f:
            yaml.dump(pcl_params, f)
        
        # 返回节点列表
        return [
            # 地图生成器节点
            Node(
                package='map_generator',
                executable='random_forest',
                name='random_forest',
                output='screen',
                parameters=[{
                    'init_state_x': float(init_x),
                    'init_state_y': float(init_y),
                    'map/x_size': float(map_size_x),
                    'map/y_size': float(map_size_y),
                    'map/z_size': float(map_size_z),
                    'map/resolution': 0.1,
                    'ObstacleShape/seed': -1,
                    'map/obs_num': int(p_num),
                    'ObstacleShape/lower_rad': 0.5,
                    'ObstacleShape/upper_rad': 0.7,
                    'ObstacleShape/lower_hei': 0.0,
                    'ObstacleShape/upper_hei': 3.0,
                    'map/circle_num': int(c_num),
                    'ObstacleShape/radius_l': 0.7,
                    'ObstacleShape/radius_h': 0.5,
                    'ObstacleShape/z_l': 0.7,
                    'ObstacleShape/z_h': 0.8,
                    'ObstacleShape/theta': 0.5,
                    'sensing/radius': 5.0,
                    'sensing/rate': 10.0,
                    'use_sim_time': False,
                }],
                remappings=[
                    ('odometry', odom_topic),
                ]
            ),
            
            # 四旋翼仿真器节点
            Node(
                package='so3_quadrotor_simulator',
                executable='quadrotor_simulator_so3',
                name='quadrotor_simulator_so3',
                output='screen',
                parameters=[{
                    'rate.odom': 200.0,
                    'simulator.init_state_x': float(init_x),
                    'simulator.init_state_y': float(init_y),
                    'simulator.init_state_z': float(init_z),
                    'use_sim_time': False,
                }],
                remappings=[
                    ('odom', '/visual_slam/odom'),
                    ('cmd', '/so3_cmd'),
                    ('force_disturbance', '/force_disturbance'),
                    ('moment_disturbance', '/moment_disturbance'),
                ]
            ),
            
            # SO3控制器节点 - 使用参数文件和单独的参数
            Node(
                package='so3_control',
                executable='so3_control_node',
                name='so3_control',
                output='screen',
                parameters=[
                    os.path.join(so3_control_pkg, 'config', 'gains_hummingbird.yaml'),
                    os.path.join(so3_control_pkg, 'config', 'corrections_hummingbird.yaml'),
                    so3_param_file,  # 使用临时参数文件
                ],
                remappings=[
                    ('odom', odom_topic),
                    ('position_cmd', '/planning/pos_cmd'),
                    ('motors', '/motors'),
                    ('corrections', '/corrections'),
                    ('so3_cmd', '/so3_cmd'),
                ]
            ),
            
            # 扰动生成器节点
            Node(
                package='so3_disturbance_generator',
                executable='so3_disturbance_generator',
                name='so3_disturbance_generator',
                output='screen',
                parameters=[{'use_sim_time': False}],
                remappings=[
                    ('odom', '/visual_slam/odom'),
                    ('noisy_odom', odom_topic),
                    ('correction', '/visual_slam/correction'),
                    ('force_disturbance', '/force_disturbance'),
                    ('moment_disturbance', '/moment_disturbance'),
                ]
            ),
            
            # 里程计可视化节点
            Node(
                package='odom_visualization',
                executable='odom_visualization',
                name='odom_visualization',
                output='screen',
                parameters=[{
                    'mesh_resource': 'package://odom_visualization/meshes/hummingbird.mesh',  # 使用原始MESH文件
                    'color.a': 0.8,
                    'color.r': 1.0,
                    'color.g': 0.0,
                    'color.b': 0.0,
                    'covariance_scale': 100.0,
                    'tf45': False,
                    'use_sim_time': False,
                }],
                remappings=[
                    ('odom', '/visual_slam/odom'),
                ]
            ),
            
            # 传感器仿真节点
            Node(
                package='local_sensing_node',
                executable='pcl_render_node',
                name='pcl_render_node',
                output='screen',
                parameters=[
                    os.path.join(local_sensing_pkg, 'params', 'camera.yaml'),
                    pcl_param_file,  # 使用临时参数文件
                ],
                remappings=[
                    ('global_map', '/map_generator/global_cloud'),
                    ('odometry', odom_topic),
                    # 输出话题重映射 - 发布给SDFMap和RViz
                    ('depth', '/sdf_map/depth'),
                    ('colordepth', '/sdf_map/colordepth'),
                    ('camera_pose', '/sdf_map/pose'),
                    ('rendered_pcl', '/sdf_map/cloud'),
                ]
            ),
        ]
    
    return LaunchDescription([
        init_x_arg,
        init_y_arg,
        init_z_arg,
        map_size_x_arg,
        map_size_y_arg,
        map_size_z_arg,
        c_num_arg,
        p_num_arg,
        odom_topic_arg,
        OpaqueFunction(function=create_nodes),
    ])


