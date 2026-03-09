#!/usr/bin/env python3
"""
ROS2 Launch文件 - 从ROS1自动转换
原始文件: rviz.launch
"""

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    # TODO: 根据原始launch文件配置节点
    # 原始XML内容已注释在下方
    
    return LaunchDescription([
        # 在此添加节点配置
    ])

"""
原始XML内容:
<launch>
  <node name="rvizvisualisation" pkg="rviz" type="rviz" output="log" args="-d $(find plan_manage)/config/traj.rviz" />
</launch>

"""
