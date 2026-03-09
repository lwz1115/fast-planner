#!/bin/bash

echo "=========================================="
echo "自动安装缺失组件"
echo "=========================================="
echo ""

# 检查是否在容器内
if [ -f /.dockerenv ]; then
    echo "✓ 检测到Docker容器环境"
    IN_CONTAINER=true
else
    echo "✗ 不在Docker容器内，某些操作可能需要sudo权限"
    IN_CONTAINER=false
fi
echo ""

# 更新包列表
echo "【1. 更新软件包列表】"
echo "----------------------------------------"
apt-get update
echo "✓ 完成"
echo ""

# 安装Gazebo Fortress
echo "【2. 安装Gazebo Fortress】"
echo "----------------------------------------"
if ! command -v gz &> /dev/null; then
    echo "正在安装Gazebo Fortress..."
    
    # 添加Gazebo官方源（如果还没有）
    if [ ! -f "/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg" ]; then
        echo "添加Gazebo官方源..."
        wget https://packages.osrfoundation.org/gazebo.gpg -O /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null
        apt-get update
    fi
    
    apt-get install -y gz-fortress
    if [ $? -eq 0 ]; then
        echo "✓ Gazebo Fortress安装成功"
    else
        echo "✗ Gazebo Fortress安装失败"
    fi
else
    echo "✓ Gazebo已安装: $(gz sim --version 2>/dev/null | head -1)"
fi
echo ""

# 安装ROS2相关包
echo "【3. 安装ROS2扩展包】"
echo "----------------------------------------"
ros2_packages=(
    "ros-humble-ros-base"
    "ros-humble-desktop"
)

for pkg in "${ros2_packages[@]}"; do
    if ! dpkg -l | grep -q "^ii.*$pkg"; then
        echo "正在安装 $pkg..."
        apt-get install -y $pkg
        if [ $? -eq 0 ]; then
            echo "✓ $pkg 安装成功"
        else
            echo "✗ $pkg 安装失败"
        fi
    else
        echo "✓ $pkg 已安装，跳过"
    fi
done
echo ""

# 初始化rosdep
echo "【4. 初始化rosdep】"
echo "----------------------------------------"
if [ ! -f "/etc/ros/rosdep/sources.list.d/20-default.list" ]; then
    echo "正在初始化rosdep..."
    rosdep init
    if [ $? -eq 0 ]; then
        echo "✓ rosdep初始化成功"
    else
        echo "✗ rosdep初始化失败（可能是网络问题，可以稍后手动运行: rosdep init）"
    fi
else
    echo "✓ rosdep已初始化，跳过"
fi

echo "正在更新rosdep..."
rosdep update 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ rosdep更新成功"
else
    echo "✗ rosdep更新失败（可能是网络问题）"
fi
echo ""

# 安装Python依赖
echo "【5. 安装Python依赖包】"
echo "----------------------------------------"
python_packages=(
    "opencv-python"
    "pyyaml"
)

for pkg in "${python_packages[@]}"; do
    if ! python3 -c "import ${pkg//-/_}" 2>/dev/null; then
        echo "正在安装 $pkg..."
        pip3 install --no-cache-dir $pkg
        if [ $? -eq 0 ]; then
            echo "✓ $pkg 安装成功"
        else
            echo "✗ $pkg 安装失败"
        fi
    else
        echo "✓ $pkg 已安装，跳过"
    fi
done
echo ""

# 安装3D图形工具
echo "【6. 安装3D图形支持工具】"
echo "----------------------------------------"
if ! command -v glxinfo &> /dev/null; then
    echo "正在安装mesa-utils..."
    apt-get install -y mesa-utils
    if [ $? -eq 0 ]; then
        echo "✓ mesa-utils安装成功"
    else
        echo "✗ mesa-utils安装失败"
    fi
else
    echo "✓ mesa-utils已安装，跳过"
fi
echo ""

# 配置环境变量
echo "【7. 配置环境变量】"
echo "----------------------------------------"
BASHRC="$HOME/.bashrc"

# 检查并添加ROS2环境
if ! grep -q "source /opt/ros/humble/setup.bash" "$BASHRC"; then
    echo "添加ROS2环境到 .bashrc..."
    echo "" >> "$BASHRC"
    echo "# ROS2 Humble环境" >> "$BASHRC"
    echo "source /opt/ros/humble/setup.bash" >> "$BASHRC"
    echo "✓ 已添加ROS2环境"
else
    echo "✓ ROS2环境已配置"
fi

# 检查并添加工作空间环境
if ! grep -q "source /root/colcon_ws/install/setup.bash" "$BASHRC"; then
    echo "添加工作空间环境到 .bashrc..."
    echo "source /root/colcon_ws/install/setup.bash 2>/dev/null || true" >> "$BASHRC"
    echo "✓ 已添加工作空间环境"
else
    echo "✓ 工作空间环境已配置"
fi

# 检查并添加Gazebo环境变量
if ! grep -q "GAZEBO_MODEL_PATH" "$BASHRC"; then
    echo "添加Gazebo环境变量到 .bashrc..."
    echo "" >> "$BASHRC"
    echo "# Gazebo环境变量" >> "$BASHRC"
    echo "export GAZEBO_MODEL_PATH=/root/colcon_ws/src:\$GAZEBO_MODEL_PATH" >> "$BASHRC"
    echo "export GAZEBO_PLUGIN_PATH=/root/colcon_ws/install/lib:\$GAZEBO_PLUGIN_PATH" >> "$BASHRC"
    echo "export LD_LIBRARY_PATH=/root/colcon_ws/install/lib:\$LD_LIBRARY_PATH" >> "$BASHRC"
    echo "✓ 已添加Gazebo环境变量"
else
    echo "✓ Gazebo环境变量已配置"
fi

# 添加ROS_DOMAIN_ID
if ! grep -q "ROS_DOMAIN_ID" "$BASHRC"; then
    echo "export ROS_DOMAIN_ID=0" >> "$BASHRC"
    echo "✓ 已添加ROS_DOMAIN_ID"
else
    echo "✓ ROS_DOMAIN_ID已配置"
fi

# 添加DISPLAY环境变量（用于GUI应用）
if ! grep -q "export DISPLAY=" "$BASHRC"; then
    echo "export DISPLAY=\${DISPLAY:-:0}" >> "$BASHRC"
    echo "✓ 已添加DISPLAY环境变量"
else
    echo "✓ DISPLAY环境变量已配置"
fi
echo ""

# 清理
echo "【8. 清理安装缓存】"
echo "----------------------------------------"
apt-get clean
rm -rf /var/lib/apt/lists/*
echo "✓ 清理完成"
echo ""

echo "=========================================="
echo "安装完成！"
echo "=========================================="
echo ""
echo "已安装组件："
echo "  ✓ Gazebo Fortress (新版Gazebo)"
echo "  ✓ ROS2 Humble (ros-base + desktop)"
echo "  ✓ rosdep (已初始化和更新)"
echo "  ✓ Python依赖 (opencv-python, pyyaml)"
echo "  ✓ 3D图形工具 (mesa-utils)"
echo ""
echo "建议操作："
echo "1. 重新加载环境: source ~/.bashrc"
echo "2. 验证安装: ros2 --version && gz sim --version"
echo "3. 运行系统检查: ./check_system.sh"
echo ""
echo "退出容器后，在主机上保存镜像："
echo "  docker commit fast_planner_ros2 fast-planner:latest"
echo ""

