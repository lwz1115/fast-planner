#!/bin/bash

echo "=========================================="
echo "系统深度检查报告"
echo "生成时间: $(date)"
echo "=========================================="
echo ""

# 系统基本信息
echo "【1. 系统基本信息】"
echo "----------------------------------------"
echo "主机名: $(hostname)"
echo "操作系统: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
echo "内核版本: $(uname -r)"
echo "架构: $(uname -m)"
echo "运行时间: $(uptime -p)"
echo ""

# CPU信息
echo "【2. CPU信息】"
echo "----------------------------------------"
echo "CPU型号: $(lscpu | grep 'Model name' | cut -d':' -f2 | xargs)"
echo "CPU核心数: $(nproc)"
echo "CPU架构: $(lscpu | grep 'Architecture' | cut -d':' -f2 | xargs)"
echo "CPU使用率:"
top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print "  空闲: " $1 "%"}'
echo ""

# 内存信息
echo "【3. 内存信息】"
echo "----------------------------------------"
free -h | awk 'NR==1{print "  " $0} NR==2{print "  " $0}'
echo ""

# 磁盘信息
echo "【4. 磁盘使用情况】"
echo "----------------------------------------"
df -h | grep -E '^/dev/|Filesystem' | awk '{printf "  %-20s %-10s %-10s %-10s %-10s\n", $1, $2, $3, $4, $5}'
echo ""

# Docker信息
echo "【5. Docker信息】"
echo "----------------------------------------"
if command -v docker &> /dev/null; then
    echo "Docker版本: $(docker --version)"
    echo ""
    echo "Docker镜像列表:"
    docker images --format "  {{.Repository}}:{{.Tag}} - {{.Size}}" | head -10
    echo ""
    echo "运行中的容器:"
    docker ps --format "  {{.Names}} ({{.Image}}) - {{.Status}}"
    if [ -z "$(docker ps -q)" ]; then
        echo "  无运行中的容器"
    fi
    echo ""
    echo "所有容器:"
    docker ps -a --format "  {{.Names}} ({{.Image}}) - {{.Status}}"
    echo ""
    echo "Docker磁盘使用:"
    docker system df
else
    echo "  Docker未安装"
fi
echo ""

# 网络信息
echo "【6. 网络信息】"
echo "----------------------------------------"
echo "网络接口:"
ip -br addr | awk '{printf "  %-15s %-10s %s\n", $1, $2, $3}'
echo ""
echo "网络连接测试:"
if ping -c 1 8.8.8.8 &> /dev/null; then
    echo "  ✓ 外网连接正常"
else
    echo "  ✗ 外网连接失败"
fi
echo ""

# GPU信息（如果是Jetson设备）
echo "【7. GPU/加速器信息】"
echo "----------------------------------------"
if command -v tegrastats &> /dev/null; then
    echo "Jetson设备信息:"
    if [ -f /etc/nv_tegra_release ]; then
        cat /etc/nv_tegra_release | head -1
    fi
    echo ""
    echo "GPU状态 (采样1秒):"
    timeout 1 tegrastats | head -1
elif command -v nvidia-smi &> /dev/null; then
    echo "NVIDIA GPU信息:"
    nvidia-smi --query-gpu=name,driver_version,memory.total,memory.used --format=csv,noheader | \
        awk -F', ' '{printf "  GPU: %s\n  驱动: %s\n  显存: %s / %s\n", $1, $2, $4, $3}'
else
    echo "  未检测到GPU或加速器"
fi
echo ""

# 进程信息
echo "【8. 系统进程 (CPU占用前5)】"
echo "----------------------------------------"
ps aux --sort=-%cpu | head -6 | awk 'NR==1{print "  " $0} NR>1{printf "  %-10s %5s%% %5s%% %s\n", $1, $3, $4, $11}'
echo ""

# ROS环境检查
echo "【9. ROS环境深度检查】"
echo "----------------------------------------"
if [ -d "/opt/ros" ]; then
    echo "已安装的ROS版本:"
    ls /opt/ros/ | sed 's/^/  - /'
    echo ""
    
    # 检查ROS2 Humble
    if [ -d "/opt/ros/humble" ]; then
        echo "ROS2 Humble详细信息:"
        echo "  安装路径: /opt/ros/humble"
        
        # 检查环境变量
        if [ -f "/opt/ros/humble/setup.bash" ]; then
            echo "  ✓ setup.bash 存在"
            source /opt/ros/humble/setup.bash 2>/dev/null
            
            # 检查ROS2命令
            if command -v ros2 &> /dev/null; then
                echo "  ✓ ros2 命令可用"
                echo "  ROS2版本: $(ros2 --version 2>/dev/null | head -1)"
            else
                echo "  ✗ ros2 命令不可用"
            fi
            
            # 检查关键ROS2包
            echo ""
            echo "  关键ROS2包检查:"
            ros2_packages=(
                "ros-humble-ros-core"
                "ros-humble-ros-base"
                "ros-humble-desktop"
                "ros-humble-ros-gz"
                "python3-colcon-common-extensions"
                "python3-rosdep"
            )
            for pkg in "${ros2_packages[@]}"; do
                if dpkg -l | grep -q "^ii.*$pkg"; then
                    version=$(dpkg -l | grep "^ii.*$pkg" | awk '{print $3}')
                    echo "    ✓ $pkg: $version"
                else
                    echo "    ✗ $pkg: 未安装"
                fi
            done
            
            # 检查ROS2节点和话题
            echo ""
            echo "  ROS2运行时检查:"
            if pgrep -f "ros2" > /dev/null; then
                echo "    ✓ 检测到运行中的ROS2进程"
                echo "    运行中的节点:"
                timeout 2 ros2 node list 2>/dev/null | sed 's/^/      /' || echo "      无法列出节点"
            else
                echo "    - 当前无运行中的ROS2进程"
            fi
            
            # 检查rosdep
            echo ""
            echo "  rosdep状态:"
            if command -v rosdep &> /dev/null; then
                echo "    ✓ rosdep已安装"
                if [ -f "/etc/ros/rosdep/sources.list.d/20-default.list" ]; then
                    echo "    ✓ rosdep已初始化"
                else
                    echo "    ✗ rosdep未初始化 (运行: rosdep init)"
                fi
            else
                echo "    ✗ rosdep未安装"
            fi
            
        else
            echo "  ✗ setup.bash 不存在"
        fi
    fi
    
    # 检查ROS1 Noetic
    if [ -d "/opt/ros/noetic" ]; then
        echo ""
        echo "ROS1 Noetic详细信息:"
        echo "  安装路径: /opt/ros/noetic"
        if [ -f "/opt/ros/noetic/setup.bash" ]; then
            echo "  ✓ setup.bash 存在"
        else
            echo "  ✗ setup.bash 不存在"
        fi
    fi
    
else
    echo "  未检测到ROS安装"
fi
echo ""

# Gazebo环境检查
echo "【10. Gazebo仿真环境检查】"
echo "----------------------------------------"

# 检查Gazebo Classic
if command -v gazebo &> /dev/null; then
    echo "Gazebo Classic:"
    echo "  ✓ 已安装"
    echo "  版本: $(gazebo --version 2>/dev/null | head -1)"
    echo "  路径: $(which gazebo)"
    
    # 检查Gazebo相关包
    echo ""
    echo "  Gazebo Classic相关包:"
    gazebo_classic_packages=(
        "gazebo"
        "libgazebo11"
        "libgazebo-dev"
        "ros-humble-gazebo-ros-pkgs"
    )
    for pkg in "${gazebo_classic_packages[@]}"; do
        if dpkg -l | grep -q "^ii.*$pkg"; then
            version=$(dpkg -l | grep "^ii.*$pkg" | awk '{print $3}')
            echo "    ✓ $pkg: $version"
        else
            echo "    ✗ $pkg: 未安装"
        fi
    done
else
    echo "Gazebo Classic:"
    echo "  ✗ 未安装"
fi

echo ""

# 检查新版Gazebo (Ignition/Gazebo)
if command -v gz &> /dev/null; then
    echo "Gazebo (新版 Ignition Gazebo):"
    echo "  ✓ 已安装"
    echo "  gz命令版本: $(gz --version 2>/dev/null | head -1)"
    echo "  路径: $(which gz)"
    
    # 检查gz子命令
    echo ""
    echo "  可用的gz子命令:"
    gz help 2>/dev/null | grep "^  " | sed 's/^/    /'
    
    # 检查Gazebo Fortress相关包
    echo ""
    echo "  Gazebo Fortress相关包:"
    gazebo_packages=(
        "gz-fortress"
        "gz-sim7"
        "gz-transport12"
        "gz-msgs9"
        "ros-humble-ros-gz"
        "ros-humble-ros-gz-sim"
        "ros-humble-ros-gz-bridge"
    )
    for pkg in "${gazebo_packages[@]}"; do
        if dpkg -l | grep -q "^ii.*$pkg"; then
            version=$(dpkg -l | grep "^ii.*$pkg" | awk '{print $3}')
            echo "    ✓ $pkg: $version"
        else
            echo "    ✗ $pkg: 未安装"
        fi
    done
    
    # 检查Gazebo环境变量
    echo ""
    echo "  Gazebo环境变量:"
    if [ -n "$GZ_SIM_RESOURCE_PATH" ]; then
        echo "    GZ_SIM_RESOURCE_PATH: $GZ_SIM_RESOURCE_PATH"
    else
        echo "    GZ_SIM_RESOURCE_PATH: 未设置"
    fi
    if [ -n "$GAZEBO_MODEL_PATH" ]; then
        echo "    GAZEBO_MODEL_PATH: $GAZEBO_MODEL_PATH"
    else
        echo "    GAZEBO_MODEL_PATH: 未设置"
    fi
    if [ -n "$GAZEBO_PLUGIN_PATH" ]; then
        echo "    GAZEBO_PLUGIN_PATH: $GAZEBO_PLUGIN_PATH"
    else
        echo "    GAZEBO_PLUGIN_PATH: 未设置"
    fi
    
    # 检查Gazebo运行状态
    echo ""
    echo "  Gazebo运行状态:"
    if pgrep -f "gz sim" > /dev/null || pgrep -f "gzserver" > /dev/null; then
        echo "    ✓ 检测到运行中的Gazebo进程"
    else
        echo "    - 当前无运行中的Gazebo进程"
    fi
    
else
    echo "Gazebo (新版):"
    echo "  ✗ 未安装"
fi
echo ""

# 检查3D图形支持
echo "【11. 3D图形和渲染支持】"
echo "----------------------------------------"
if command -v glxinfo &> /dev/null; then
    echo "OpenGL信息:"
    glxinfo 2>/dev/null | grep -E "OpenGL version|OpenGL renderer" | sed 's/^/  /'
else
    echo "glxinfo未安装 (安装: sudo apt install mesa-utils)"
fi

if [ -n "$DISPLAY" ]; then
    echo "  ✓ DISPLAY环境变量已设置: $DISPLAY"
else
    echo "  ✗ DISPLAY环境变量未设置 (GUI应用可能无法运行)"
fi
echo ""

# Python环境
echo "【12. Python环境和依赖】"
echo "----------------------------------------"
if command -v python3 &> /dev/null; then
    echo "Python版本: $(python3 --version)"
    echo "Python路径: $(which python3)"
    echo "pip版本: $(pip3 --version 2>/dev/null | cut -d' ' -f1-2)"
    echo ""
    echo "已安装的关键包:"
    for pkg in numpy scipy opencv-python pyyaml fastapi uvicorn pydantic; do
        if python3 -c "import ${pkg//-/_}" 2>/dev/null; then
            version=$(python3 -c "import ${pkg//-/_}; print(${pkg//-/_}.__version__)" 2>/dev/null || echo "未知")
            echo "  ✓ $pkg: $version"
        else
            echo "  ✗ $pkg: 未安装"
        fi
    done
    
    echo ""
    echo "ROS相关Python包:"
    for pkg in rclpy rospy; do
        if python3 -c "import $pkg" 2>/dev/null; then
            echo "  ✓ $pkg: 已安装"
        else
            echo "  ✗ $pkg: 未安装"
        fi
    done
else
    echo "  Python3未安装"
fi
echo ""

# 编译工具链检查
echo "【13. 编译工具链检查】"
echo "----------------------------------------"
tools=(
    "gcc:GCC编译器"
    "g++:G++编译器"
    "cmake:CMake构建工具"
    "make:Make构建工具"
    "colcon:Colcon构建工具"
    "catkin_make:Catkin构建工具"
)

for tool_info in "${tools[@]}"; do
    tool="${tool_info%%:*}"
    desc="${tool_info##*:}"
    if command -v $tool &> /dev/null; then
        version=$($tool --version 2>/dev/null | head -1)
        echo "  ✓ $desc: $version"
    else
        echo "  ✗ $desc: 未安装"
    fi
done
echo ""

# 关键开发库检查
echo "【14. 关键开发库检查】"
echo "----------------------------------------"
dev_libs=(
    "libeigen3-dev:Eigen3线性代数库"
    "libpcl-dev:点云库PCL"
    "libopencv-dev:OpenCV计算机视觉库"
    "libarmadillo-dev:Armadillo线性代数库"
    "libgsl-dev:GSL科学计算库"
)

for lib_info in "${dev_libs[@]}"; do
    lib="${lib_info%%:*}"
    desc="${lib_info##*:}"
    if dpkg -l | grep -q "^ii.*$lib"; then
        version=$(dpkg -l | grep "^ii.*$lib" | awk '{print $3}')
        echo "  ✓ $desc ($lib): $version"
    else
        echo "  ✗ $desc ($lib): 未安装"
    fi
done
echo ""

# 当前目录信息
echo "【15. 当前工作目录】"
echo "----------------------------------------"
echo "路径: $(pwd)"
echo "磁盘使用: $(du -sh . 2>/dev/null | cut -f1)"
echo "文件数量: $(find . -type f 2>/dev/null | wc -l)"
echo ""

echo "=========================================="
echo "检查完成"
echo "=========================================="

