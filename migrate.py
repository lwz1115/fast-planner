#!/usr/bin/env python3
"""
检查ROS2转换是否完成
验证所有必要的修改是否已应用
"""

import os
import re
from pathlib import Path
from collections import defaultdict

class ConversionChecker:
    def __init__(self, workspace_root):
        self.workspace_root = Path(workspace_root)
        self.src_dir = self.workspace_root / "src" / "Fast-Planner"
        self.issues = defaultdict(list)
        self.warnings = defaultdict(list)
        self.stats = defaultdict(int)
    
    def check_all(self):
        """执行所有检查"""
        print("=" * 60)
        print("ROS2 转换检查")
        print("=" * 60)
        
        print("\n→ 检查 package.xml...")
        self.check_package_xml_files()
        
        print("\n→ 检查 CMakeLists.txt...")
        self.check_cmake_files()
        
        print("\n→ 检查 C++ 文件...")
        self.check_cpp_files()
        
        print("\n→ 检查头文件...")
        self.check_header_files()
        
        self.print_report()
    
    def check_package_xml_files(self):
        """检查package.xml文件"""
        for pkg_xml in self.src_dir.rglob("package.xml"):
            if self.should_skip(pkg_xml):
                continue
            
            self.stats['package_xml'] += 1
            content = pkg_xml.read_text()
            rel_path = str(pkg_xml.relative_to(self.workspace_root))
            
            # 检查format
            if 'format="3"' not in content and 'format="2"' not in content:
                self.issues['package_xml'].append(f"{rel_path}: 缺少format属性")
            
            # 检查buildtool_depend
            if '<buildtool_depend>catkin</buildtool_depend>' in content:
                self.issues['package_xml'].append(f"{rel_path}: 仍在使用catkin")
            
            if '<buildtool_depend>ament_cmake</buildtool_depend>' not in content:
                self.issues['package_xml'].append(f"{rel_path}: 缺少ament_cmake")
            
            # 检查ROS1包
            ros1_packages = ['roscpp', 'rospy', 'message_generation', 'message_runtime']
            for pkg in ros1_packages:
                if f'<depend>{pkg}</depend>' in content or \
                   f'<build_depend>{pkg}</build_depend>' in content:
                    self.issues['package_xml'].append(f"{rel_path}: 仍在使用ROS1包 {pkg}")
            
            # 检查export
            if '<export>' not in content:
                self.warnings['package_xml'].append(f"{rel_path}: 缺少export标签")
            elif '<build_type>ament_cmake</build_type>' not in content:
                self.warnings['package_xml'].append(f"{rel_path}: export中缺少build_type")
            
            # 检查常见依赖
            if 'rclcpp' not in content and 'ament_cmake' in content:
                self.warnings['package_xml'].append(f"{rel_path}: 可能缺少rclcpp依赖")
    
    def check_cmake_files(self):
        """检查CMakeLists.txt文件"""
        for cmake_file in self.src_dir.rglob("CMakeLists.txt"):
            if self.should_skip(cmake_file):
                continue
            
            self.stats['cmake'] += 1
            content = cmake_file.read_text()
            rel_path = str(cmake_file.relative_to(self.workspace_root))
            
            # 检查catkin
            if 'find_package(catkin' in content:
                self.issues['cmake'].append(f"{rel_path}: 仍在使用catkin")
            
            if 'catkin_package(' in content:
                self.issues['cmake'].append(f"{rel_path}: 仍有catkin_package()")
            
            # 检查ament_cmake
            if 'find_package(ament_cmake' not in content:
                self.issues['cmake'].append(f"{rel_path}: 缺少find_package(ament_cmake)")
            
            if 'ament_package()' not in content:
                self.issues['cmake'].append(f"{rel_path}: 缺少ament_package()")
            
            # 检查安装规则
            if 'add_library(' in content or 'add_executable(' in content:
                if 'install(' not in content:
                    self.warnings['cmake'].append(f"{rel_path}: 可能缺少install规则")
            
            # 检查catkin变量
            if '${catkin_INCLUDE_DIRS}' in content or '${catkin_LIBRARIES}' in content:
                self.issues['cmake'].append(f"{rel_path}: 仍在使用catkin变量")
    
    def check_cpp_files(self):
        """检查C++源文件"""
        for cpp_file in self.src_dir.rglob("*.cpp"):
            if self.should_skip(cpp_file):
                continue
            
            self.stats['cpp'] += 1
            try:
                content = cpp_file.read_text(encoding='utf-8', errors='ignore')
                rel_path = str(cpp_file.relative_to(self.workspace_root))
                
                # 检查ROS1头文件
                if '#include <ros/ros.h>' in content:
                    self.issues['cpp'].append(f"{rel_path}: 仍在使用 ros/ros.h")
                
                # 检查ROS1类型
                if re.search(r'\bros::NodeHandle\b', content):
                    self.issues['cpp'].append(f"{rel_path}: 仍在使用 ros::NodeHandle")
                
                if re.search(r'\bros::Time\b', content):
                    self.issues['cpp'].append(f"{rel_path}: 仍在使用 ros::Time")
                
                if re.search(r'\bros::Duration\b', content):
                    self.issues['cpp'].append(f"{rel_path}: 仍在使用 ros::Duration")
                
                # 检查ROS1日志
                if re.search(r'\bROS_INFO\(', content):
                    if 'RCLCPP_INFO' not in content:
                        self.issues['cpp'].append(f"{rel_path}: 仍在使用 ROS_INFO")
                
                # 检查消息类型
                msg_packages = ['geometry_msgs', 'nav_msgs', 'sensor_msgs', 'std_msgs']
                for pkg in msg_packages:
                    # 检查是否缺少::msg::
                    pattern = f'{pkg}::(\\w+)(?!::msg)'
                    if re.search(pattern, content):
                        # 但要排除已经正确的情况
                        if f'{pkg}::msg::' not in content:
                            self.warnings['cpp'].append(
                                f"{rel_path}: {pkg} 可能缺少 ::msg:: 命名空间"
                            )
                
                # 检查.toSec()
                if '.toSec()' in content:
                    self.warnings['cpp'].append(f"{rel_path}: 仍在使用 .toSec() (应为 .seconds())")
                
            except Exception as e:
                self.warnings['cpp'].append(f"{rel_path}: 读取失败 - {e}")
    
    def check_header_files(self):
        """检查头文件"""
        for header in self.src_dir.rglob("*.h"):
            if self.should_skip(header):
                continue
            
            self.stats['headers'] += 1
            try:
                content = header.read_text(encoding='utf-8', errors='ignore')
                rel_path = str(header.relative_to(self.workspace_root))
                
                # 检查ROS1头文件
                if '#include <ros/ros.h>' in content:
                    self.issues['headers'].append(f"{rel_path}: 仍在使用 ros/ros.h")
                
                # 检查cv_bridge
                if '#include <cv_bridge/cv_bridge.hpp>' in content:
                    self.issues['headers'].append(
                        f"{rel_path}: cv_bridge应使用.h而不是.hpp"
                    )
                
                # 检查消息头文件
                # geometry_msgs/PoseStamped.h -> geometry_msgs/msg/pose_stamped.hpp
                pattern = r'#include\s*<(geometry_msgs|nav_msgs|sensor_msgs|std_msgs)/(\w+)\.h>'
                matches = re.findall(pattern, content)
                for pkg, msg_type in matches:
                    if '/msg/' not in content:
                        self.warnings['headers'].append(
                            f"{rel_path}: {pkg}/{msg_type}.h 应转换为 {pkg}/msg/xxx.hpp"
                        )
                
            except Exception as e:
                self.warnings['headers'].append(f"{rel_path}: 读取失败 - {e}")
    
    def print_report(self):
        """打印检查报告"""
        print("\n" + "=" * 60)
        print("检查报告")
        print("=" * 60)
        
        # 统计信息
        print("\n文件统计:")
        print(f"  package.xml:    {self.stats['package_xml']} 个")
        print(f"  CMakeLists.txt: {self.stats['cmake']} 个")
        print(f"  C++ 源文件:     {self.stats['cpp']} 个")
        print(f"  头文件:         {self.stats['headers']} 个")
        
        # 问题
        total_issues = sum(len(v) for v in self.issues.values())
        total_warnings = sum(len(v) for v in self.warnings.values())
        
        print(f"\n发现 {total_issues} 个问题, {total_warnings} 个警告")
        
        if total_issues > 0:
            print("\n" + "=" * 60)
            print("❌ 问题 (必须修复)")
            print("=" * 60)
            for category, issue_list in self.issues.items():
                if issue_list:
                    print(f"\n{category.upper()}:")
                    for issue in issue_list[:10]:  # 只显示前10个
                        print(f"  • {issue}")
                    if len(issue_list) > 10:
                        print(f"  ... 还有 {len(issue_list) - 10} 个问题")
        
        if total_warnings > 0:
            print("\n" + "=" * 60)
            print("⚠️  警告 (建议修复)")
            print("=" * 60)
            for category, warning_list in self.warnings.items():
                if warning_list:
                    print(f"\n{category.upper()}:")
                    for warning in warning_list[:10]:  # 只显示前10个
                        print(f"  • {warning}")
                    if len(warning_list) > 10:
                        print(f"  ... 还有 {len(warning_list) - 10} 个警告")
        
        # 总结
        print("\n" + "=" * 60)
        if total_issues == 0:
            print("✅ 转换检查通过!")
            if total_warnings > 0:
                print(f"   但有 {total_warnings} 个警告需要注意")
        else:
            print(f"❌ 发现 {total_issues} 个问题需要修复")
        print("=" * 60)
    
    def should_skip(self, path):
        """判断是否跳过"""
        skip_dirs = ['build', 'devel', 'install', 'log', '.git', '__pycache__']
        return any(skip_dir in path.parts for skip_dir in skip_dirs)

def main():
    import sys
    workspace = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    checker = ConversionChecker(workspace)
    checker.check_all()

if __name__ == "__main__":
    main()

