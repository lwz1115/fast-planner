#!/usr/bin/env python3
"""
ROS2 Launch文件 - RViz可视化
启动RViz用于Fast-Planner可视化
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # 获取config文件路径
    pkg_share = get_package_share_directory('plan_manage')
    rviz_config_file = os.path.join(pkg_share, 'config', 'kino.rviz')
    
    # RViz节点
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rvizvisualisation',
        arguments=['-d', rviz_config_file],
        output='log'
    )
    
    return LaunchDescription([
        rviz_node
    ])

