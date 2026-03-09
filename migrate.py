#!/usr/bin/env python3
"""
Fast-Planner ROS1 to ROS2 自动化迁移工具
"""

import os
import re
import shutil
import argparse
from pathlib import Path
from typing import List, Dict, Tuple

class ROS2Migrator:
    def __init__(self, src_path: str, dst_path: str):
        self.src_path = Path(src_path)
        self.dst_path = Path(dst_path)
        self.migration_log = []
        
    def log(self, message: str):
        """记录迁移日志"""
        print(f"[迁移] {message}")
        self.migration_log.append(message)
    
    def migrate_package_xml(self, pkg_xml_path: Path) -> str:
        """迁移 package.xml 从 ROS1 到 ROS2 格式"""
        with open(pkg_xml_path, 'r') as f:
            content = f.read()
        
        # 检测格式版本
        if 'format="2"' in content or 'format="3"' in content:
            format_version = 3  # ROS2 使用 format 3
        else:
            format_version = 3
        
        # 替换格式版本
        content = re.sub(r'<package.*?>', f'<package format="{format_version}">', content)
        
        # 替换依赖标签
        replacements = {
            '<buildtool_depend>catkin</buildtool_depend>': '<buildtool_depend>ament_cmake</buildtool_depend>',
            '<build_depend>roscpp</build_depend>': '<depend>rclcpp</depend>',
            '<build_depend>rospy</build_depend>': '<depend>rclpy</depend>',
            '<build_depend>std_msgs</build_depend>': '<depend>std_msgs</depend>',
            '<build_depend>geometry_msgs</build_depend>': '<depend>geometry_msgs</depend>',
            '<build_depend>nav_msgs</build_depend>': '<depend>nav_msgs</depend>',
            '<build_depend>sensor_msgs</build_depend>': '<depend>sensor_msgs</depend>',
            '<build_depend>visualization_msgs</build_depend>': '<depend>visualization_msgs</depend>',
            '<build_depend>message_generation</build_depend>': '<buildtool_depend>rosidl_default_generators</buildtool_depend>',
            '<exec_depend>message_runtime</exec_depend>': '<exec_depend>rosidl_default_runtime</exec_depend>',
            '<run_depend>': '<exec_depend>',
            '</run_depend>': '</exec_depend>',
            '<build_export_depend>roscpp</build_export_depend>': '',
            '<build_export_depend>rospy</build_export_depend>': '',
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        # 添加 ROS2 特定的导出
        if '<export>' in content and '</export>' in content:
            export_section = re.search(r'<export>(.*?)</export>', content, re.DOTALL)
            if export_section:
                export_content = export_section.group(1).strip()
                if not export_content or export_content == '<!-- Other tools can request additional information be placed here -->':
                    content = content.replace(
                        export_section.group(0),
                        '  <export>\n    <build_type>ament_cmake</build_type>\n  </export>'
                    )
        
        return content
    
    def migrate_cmakelists(self, cmake_path: Path) -> str:
        """迁移 CMakeLists.txt 从 ROS1 到 ROS2 格式"""
        with open(cmake_path, 'r') as f:
            content = f.read()
        
        # 基础替换
        replacements = {
            'find_package(catkin REQUIRED': 'find_package(ament_cmake REQUIRED',
            'catkin_package(': 'ament_package(',
            'add_message_files(': '# add_message_files(',
            'add_service_files(': '# add_service_files(',
            'generate_messages(': '# generate_messages(',
            '${catkin_INCLUDE_DIRS}': '${ament_INCLUDE_DIRS}',
            '${catkin_LIBRARIES}': '${ament_LIBRARIES}',
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        # 处理消息生成
        if 'add_message_files' in content or 'add_service_files' in content:
            # 提取消息文件
            msg_files = re.findall(r'FILES\s+([\w\s.]+)', content)
            if msg_files:
                msg_list = [f.strip() for f in msg_files[0].split() if f.strip()]
                
                # 生成 rosidl_generate_interfaces
                rosidl_section = f"\nrosidl_generate_interfaces(${{PROJECT_NAME}}\n"
                for msg in msg_list:
                    rosidl_section += f'  "msg/{msg}"\n'
                rosidl_section += "  DEPENDENCIES std_msgs geometry_msgs\n)\n"
                
                # 在 ament_package() 之前插入
                content = content.replace('ament_package()', rosidl_section + '\nament_package()')
        
        # 添加 ament_cmake 依赖
        if 'find_package(ament_cmake REQUIRED' in content:
            # 确保在文件开头有正确的 CMake 版本
            if 'cmake_minimum_required' not in content:
                content = 'cmake_minimum_required(VERSION 3.8)\n' + content
        
        return content
    
    def migrate_cpp_node(self, cpp_path: Path) -> str:
        """迁移 C++ 节点代码"""
        with open(cpp_path, 'r') as f:
            content = f.read()
        
        # 头文件替换
        header_replacements = {
            '#include <ros/ros.h>': '#include <rclcpp/rclcpp.hpp>',
            '#include <ros/time.h>': '#include <rclcpp/time.hpp>',
            '#include <ros/duration.h>': '#include <rclcpp/duration.hpp>',
        }
        
        for old, new in header_replacements.items():
            content = content.replace(old, new)
        
        # API 替换
        api_replacements = {
            'ros::init': 'rclcpp::init',
            'ros::NodeHandle': 'rclcpp::Node',
            'ros::Publisher': 'rclcpp::Publisher',
            'ros::Subscriber': 'rclcpp::Subscription',
            'ros::Rate': 'rclcpp::Rate',
            'ros::Time': 'rclcpp::Time',
            'ros::Duration': 'rclcpp::Duration',
            'ros::spin()': 'rclcpp::spin(node)',
            'ros::spinOnce()': 'rclcpp::spin_some(node)',
            'ros::ok()': 'rclcpp::ok()',
            'ROS_INFO': 'RCLCPP_INFO',
            'ROS_WARN': 'RCLCPP_WARN',
            'ROS_ERROR': 'RCLCPP_ERROR',
            'ROS_DEBUG': 'RCLCPP_DEBUG',
        }
        
        for old, new in api_replacements.items():
            content = content.replace(old, new)
        
        return content
    
    def migrate_launch_file(self, launch_path: Path) -> str:
        """迁移 launch 文件从 XML 到 Python 格式"""
        with open(launch_path, 'r') as f:
            xml_content = f.read()
        
        # 提取节点信息
        nodes = re.findall(r'<node\s+pkg="([^"]+)"\s+type="([^"]+)"\s+name="([^"]+)"[^>]*>', xml_content)
        params = re.findall(r'<param\s+name="([^"]+)"\s+value="([^"]+)"', xml_content)
        remaps = re.findall(r'<remap\s+from="([^"]+)"\s+to="([^"]+)"', xml_content)
        
        # 生成 Python launch 文件
        py_content = """from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
"""
        
        for pkg, node_type, name in nodes:
            py_content += f"""        Node(
            package='{pkg}',
            executable='{node_type}',
            name='{name}',
            output='screen',
"""
            
            # 添加参数
            if params:
                py_content += "            parameters=[{\n"
                for param_name, param_value in params:
                    py_content += f"                '{param_name}': {param_value},\n"
                py_content += "            }],\n"
            
            # 添加重映射
            if remaps:
                py_content += "            remappings=[\n"
                for from_topic, to_topic in remaps:
                    py_content += f"                ('{from_topic}', '{to_topic}'),\n"
                py_content += "            ],\n"
            
            py_content += "        ),\n"
        
        py_content += "    ])\n"
        
        return py_content
    
    def migrate_package(self, pkg_path: Path):
        """迁移单个 ROS 包"""
        pkg_name = pkg_path.name
        self.log(f"开始迁移包: {pkg_name}")
        
        # 创建目标目录
        dst_pkg_path = self.dst_path / pkg_name
        dst_pkg_path.mkdir(parents=True, exist_ok=True)
        
        # 迁移 package.xml
        pkg_xml = pkg_path / 'package.xml'
        if pkg_xml.exists():
            self.log(f"  迁移 package.xml")
            new_content = self.migrate_package_xml(pkg_xml)
            with open(dst_pkg_path / 'package.xml', 'w') as f:
                f.write(new_content)
        
        # 迁移 CMakeLists.txt
        cmake = pkg_path / 'CMakeLists.txt'
        if cmake.exists():
            self.log(f"  迁移 CMakeLists.txt")
            new_content = self.migrate_cmakelists(cmake)
            with open(dst_pkg_path / 'CMakeLists.txt', 'w') as f:
                f.write(new_content)
        
        # 复制并迁移源代码
        src_dir = pkg_path / 'src'
        if src_dir.exists():
            self.log(f"  迁移源代码")
            dst_src = dst_pkg_path / 'src'
            dst_src.mkdir(exist_ok=True)
            
            for cpp_file in src_dir.glob('*.cpp'):
                new_content = self.migrate_cpp_node(cpp_file)
                with open(dst_src / cpp_file.name, 'w') as f:
                    f.write(new_content)
        
        # 复制头文件
        include_dir = pkg_path / 'include'
        if include_dir.exists():
            self.log(f"  复制头文件")
            shutil.copytree(include_dir, dst_pkg_path / 'include', dirs_exist_ok=True)
        
        # 复制消息文件
        msg_dir = pkg_path / 'msg'
        if msg_dir.exists():
            self.log(f"  复制消息文件")
            shutil.copytree(msg_dir, dst_pkg_path / 'msg', dirs_exist_ok=True)
        
        # 迁移 launch 文件
        launch_dir = pkg_path / 'launch'
        if launch_dir.exists():
            self.log(f"  迁移 launch 文件")
            dst_launch = dst_pkg_path / 'launch'
            dst_launch.mkdir(exist_ok=True)
            
            for launch_file in launch_dir.glob('*.launch'):
                new_content = self.migrate_launch_file(launch_file)
                new_name = launch_file.stem + '.launch.py'
                with open(dst_launch / new_name, 'w') as f:
                    f.write(new_content)
        
        # 复制配置文件
        config_dir = pkg_path / 'config'
        if config_dir.exists():
            self.log(f"  复制配置文件")
            shutil.copytree(config_dir, dst_pkg_path / 'config', dirs_exist_ok=True)
        
        self.log(f"完成迁移包: {pkg_name}\n")
    
    def find_ros_packages(self) -> List[Path]:
        """查找所有 ROS 包"""
        packages = []
        for pkg_xml in self.src_path.rglob('package.xml'):
            packages.append(pkg_xml.parent)
        return packages
    
    def migrate_all(self):
        """迁移所有包"""
        packages = self.find_ros_packages()
        self.log(f"找到 {len(packages)} 个 ROS 包")
        
        for pkg_path in packages:
            try:
                self.migrate_package(pkg_path)
            except Exception as e:
                self.log(f"错误: 迁移 {pkg_path.name} 失败: {e}")
        
        # 保存日志
        log_file = self.dst_path / 'migration_log.txt'
        with open(log_file, 'w') as f:
            f.write('\n'.join(self.migration_log))
        
        self.log(f"\n迁移完成! 日志保存到: {log_file}")

def main():
    parser = argparse.ArgumentParser(description='Fast-Planner ROS1 到 ROS2 迁移工具')
    parser.add_argument('--src', required=True, help='ROS1 源代码路径')
    parser.add_argument('--dst', required=True, help='ROS2 目标路径')
    parser.add_argument('--package', help='只迁移指定的包')
    
    args = parser.parse_args()
    
    migrator = ROS2Migrator(args.src, args.dst)
    
    if args.package:
        pkg_path = Path(args.src) / args.package
        if pkg_path.exists():
            migrator.migrate_package(pkg_path)
        else:
            print(f"错误: 找不到包 {args.package}")
    else:
        migrator.migrate_all()

if __name__ == '__main__':
    main()

