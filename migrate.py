#!/usr/bin/env python3

import os
import re
import glob

def fix_file(filepath):
    """修复单个文件中的ROS1到ROS2转换问题"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 1. 修复发布器调用：从 .publish( 到 ->publish(
        content = re.sub(r'(\w+)\.publish\(', r'\1->publish(', content)
        
        # 2. 移除TODO转换注释
        content = re.sub(r'/\* TODO: 转换发布 \*/ ', '', content)
        
        # 3. 修复节点引用
        content = re.sub(r'node_->now\(\)', 'node_->now()', content)
        
        # 4. 修复订阅器调用（如果有的话）
        content = re.sub(r'(\w+)\.subscribe\(', r'\1->subscribe(', content)
        
        # 只有内容发生变化时才写回文件
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
        
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    """主函数：查找并修复所有需要的文件"""
    
    # 定义需要搜索的目录
    search_dirs = [
        'src/Fast-Planner/fast_planner/*/src/*.cpp',
        'src/Fast-Planner/uav_simulator/*/src/*.cpp',
        'src/Fast-Planner/uav_simulator/Utils/*/src/*.cpp'
    ]
    
    fixed_files = []
    
    for pattern in search_dirs:
        files = glob.glob(pattern, recursive=True)
        for filepath in files:
            if fix_file(filepath):
                fixed_files.append(filepath)
                print(f"Fixed: {filepath}")
    
    print(f"\n总共修复了 {len(fixed_files)} 个文件:")
    for f in fixed_files:
        print(f"  - {f}")

if __name__ == "__main__":
    main()
