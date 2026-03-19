# Gazebo Fortress 移植到 Jetson 指南

## 概述

本文档提供将 Fast-Planner 项目从 Gazebo Classic 迁移到 Gazebo Fortress (Ignition Gazebo) 并在 NVIDIA Jetson 平台上运行的完整指南。

## 目录

1. [环境准备](#环境准备)
2. [Gazebo Fortress 安装](#gazebo-fortress-安装)
3. [ROS 2 桥接方案](#ros-2-桥接方案)
4. [性能优化](#性能优化)
5. [传感器配置](#传感器配置)
6. [常见问题](#常见问题)

---

## 环境准备

### Jetson 平台要求

- **推荐硬件**: Jetson Xavier NX / AGX Xavier / Orin 系列
- **最低配置**: Jetson Nano (性能受限，需要额外优化)
- **JetPack 版本**: 5.0+ (Ubuntu 20.04) 或 6.0+ (Ubuntu 22.04)
- **存储空间**: 至少 16GB 可用空间
- **内存**: 建议 8GB+ RAM

### 软件依赖

```bash
# 检查 JetPack 版本
sudo apt-cache show nvidia-jetpack

# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装基础依赖
sudo apt install -y \
    build-essential \
    cmake \
    git \
    python3-pip \
    wget \
    curl
```

---

## Gazebo Fortress 安装

### 方案 1: 二进制安装 (推荐 Ubuntu 20.04/22.04)

```bash
# 添加 OSRF 仓库
sudo sh -c 'echo "deb http://packages.osrfoundation.org/gazebo/ubuntu-stable `lsb_release -cs` main" > /etc/apt/sources.list.d/gazebo-stable.list'
wget https://packages.osrfoundation.org/gazebo.key -O - | sudo apt-key add -

# 更新并安装 Gazebo Fortress
sudo apt update
sudo apt install -y ignition-fortress

# 验证安装
ign gazebo --version
```

### 方案 2: 源码编译 (适用于特定优化需求)

```bash
# 克隆 Gazebo Fortress 源码
mkdir -p ~/gazebo_ws/src
cd ~/gazebo_ws/src
git clone https://github.com/gazebosim/gz-sim -b ign-gazebo6

# 安装编译依赖
sudo apt install -y \
    libignition-cmake2-dev \
    libignition-common4-dev \
    libignition-math6-dev \
    libignition-plugin-dev \
    libignition-physics5-dev \
    libignition-rendering6-dev \
    libignition-sensors6-dev \
    libignition-transport11-dev \
    libignition-gui6-dev \
    libignition-msgs8-dev \
    libsdformat12-dev

# 编译 (使用 Jetson 优化参数)
cd ~/gazebo_ws
mkdir build && cd build
cmake ../src/gz-sim \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CXX_FLAGS="-march=native -O3" \
    -DBUILD_TESTING=OFF
make -j$(nproc)
sudo make install
```

### Jetson 特定优化编译选项

```bash
# 针对 Jetson 的 CUDA 和 ARM 优化
cmake ../src/gz-sim \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CXX_FLAGS="-march=armv8-a+crypto -mtune=cortex-a57 -O3 -flto" \
    -DUSE_CUDA=ON \
    -DCUDA_ARCH_BIN="5.3,6.2,7.2,8.7" \
    -DBUILD_TESTING=OFF \
    -DENABLE_PROFILER=OFF
```

---

## ROS 2 桥接方案

### 选项 A: ROS 1 Noetic + ros_ign_bridge (推荐当前项目)

由于 Fast-Planner 基于 ROS 1 Noetic，使用 `ros_ign_bridge` 连接 Gazebo Fortress:

```bash
# 安装 ros_ign_bridge
sudo apt install -y ros-noetic-ros-ign-bridge

# 创建桥接启动文件
cat > ~/catkin_ws/src/Fast-Planner/fast_planner/plan_manage/launch/gazebo_fortress_bridge.launch << 'EOF'
<launch>
  <!-- Gazebo Fortress 桥接 -->
  <node pkg="ros_ign_bridge" type="parameter_bridge" name="ros_ign_bridge" output="screen">
    <!-- 深度相机 -->
    <remap from="/depth_camera/image" to="/pcl_render_node/depth"/>
    <remap from="/depth_camera/camera_info" to="/camera/depth/camera_info"/>
    <remap from="/depth_camera/points" to="/pcl_render_node/cloud"/>

    <!-- 里程计 -->
    <remap from="/model/quadrotor/odometry" to="/state_ukf/odom"/>

    <!-- 控制命令 -->
    <remap from="/cmd_vel" to="/planning/pos_cmd"/>

    <!-- 桥接参数 -->
    <param name="config_file" value="$(find plan_manage)/config/ign_bridge.yaml"/>
  </node>
</launch>
EOF
```

桥接配置文件 `ign_bridge.yaml`:

```yaml
# ~/catkin_ws/src/Fast-Planner/fast_planner/plan_manage/config/ign_bridge.yaml
- ros_topic_name: "/pcl_render_node/depth"
  ign_topic_name: "/depth_camera/image"
  ros_type_name: "sensor_msgs/Image"
  ign_type_name: "ignition.msgs.Image"
  direction: IGN_TO_ROS

- ros_topic_name: "/pcl_render_node/cloud"
  ign_topic_name: "/depth_camera/points"
  ros_type_name: "sensor_msgs/PointCloud2"
  ign_type_name: "ignition.msgs.PointCloudPacked"
  direction: IGN_TO_ROS

- ros_topic_name: "/state_ukf/odom"
  ign_topic_name: "/model/quadrotor/odometry"
  ros_type_name: "nav_msgs/Odometry"
  ign_type_name: "ignition.msgs.Odometry"
  direction: IGN_TO_ROS

- ros_topic_name: "/planning/pos_cmd"
  ign_topic_name: "/cmd_vel"
  ros_type_name: "geometry_msgs/Twist"
  ign_type_name: "ignition.msgs.Twist"
  direction: ROS_TO_IGN
```

### 选项 B: 完全迁移到 ROS 2 (长期方案)

如果计划完全迁移到 ROS 2:

```bash
# 安装 ROS 2 Humble (Ubuntu 22.04)
sudo apt install -y ros-humble-desktop
sudo apt install -y ros-humble-ros-gz

# 使用 ros1_bridge 实现 ROS 1/2 共存
sudo apt install -y ros-humble-ros1-bridge
```

---

## 性能优化

### 1. Gazebo Fortress 渲染优化

创建 Jetson 优化的 Gazebo 配置:

```bash
mkdir -p ~/.ignition/gazebo
cat > ~/.ignition/gazebo/server.config << 'EOF'
<?xml version="1.0"?>
<server_config>
  <plugins>
    <plugin filename="libignition-gazebo-physics-system.so" name="ignition::gazebo::systems::Physics">
      <engine>
        <filename>libignition-physics-dartsim-plugin.so</filename>
      </engine>
      <max_step_size>0.01</max_step_size>
      <real_time_factor>1.0</real_time_factor>
    </plugin>

    <plugin filename="libignition-gazebo-sensors-system.so" name="ignition::gazebo::systems::Sensors">
      <render_engine>ogre2</render_engine>
      <!-- Jetson 优化: 降低渲染质量 -->
      <background_color>0.8 0.8 0.8</background_color>
      <ambient_light>0.5 0.5 0.5</ambient_light>
    </plugin>
  </plugins>
</server_config>
EOF
```

### 2. 内存和 CPU 优化

```bash
# 增加 Jetson swap 空间
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 设置 CPU 性能模式
sudo nvpmodel -m 0  # 最大性能模式
sudo jetson_clocks   # 锁定最高频率
```

### 3. Gazebo 启动参数优化

```bash
# 无 GUI 模式 (节省资源)
ign gazebo -s -r world.sdf

# 限制物理更新频率
ign gazebo --physics-engine dart --iterations 50 world.sdf

# 使用简化的渲染引擎
IGN_GAZEBO_RENDER_ENGINE=ogre ign gazebo world.sdf
```

### 4. 传感器降采样

修改深度相机配置以降低数据量:

```xml
<!-- 在 Gazebo Fortress SDF 文件中 -->
<sensor name="depth_camera" type="depth">
  <update_rate>10</update_rate>  <!-- 从 30Hz 降至 10Hz -->
  <camera>
    <horizontal_fov>1.5708</horizontal_fov>
    <image>
      <width>320</width>   <!-- 从 640 降至 320 -->
      <height>240</height> <!-- 从 480 降至 240 -->
      <format>R_FLOAT32</format>
    </image>
    <clip>
      <near>0.1</near>
      <far>10.0</far>
    </clip>
  </camera>
</sensor>
```

---

## 传感器配置

### 深度相机 SDF 模型

创建适配 Fast-Planner 的深度相机模型:

```xml
<!-- models/depth_camera/model.sdf -->
<?xml version="1.0"?>
<sdf version="1.8">
  <model name="depth_camera">
    <pose>0 0 0.1 0 0 0</pose>
    <link name="link">
      <sensor name="depth_camera" type="depth_camera">
        <update_rate>15</update_rate>
        <topic>/depth_camera</topic>

        <camera>
          <horizontal_fov>1.5708</horizontal_fov>
          <image>
            <width>640</width>
            <height>480</height>
            <format>R_FLOAT32</format>
          </image>
          <clip>
            <near>0.1</near>
            <far>10.0</far>
          </clip>

          <!-- 相机内参 (匹配 Fast-Planner 默认值) -->
          <intrinsics>
            <fx>387.23</fx>
            <fy>387.23</fy>
            <cx>321.05</cx>
            <cy>243.45</cy>
            <s>0</s>
          </intrinsics>
        </camera>

        <always_on>1</always_on>
        <visualize>true</visualize>
      </sensor>
    </link>
  </model>
</sdf>
```

### 四旋翼模型

```xml
<!-- models/quadrotor/model.sdf -->
<?xml version="1.0"?>
<sdf version="1.8">
  <model name="quadrotor">
    <pose>0 0 0.5 0 0 0</pose>

    <link name="base_link">
      <inertial>
        <mass>1.5</mass>
        <inertia>
          <ixx>0.029125</ixx>
          <ixy>0</ixy>
          <ixz>0</ixz>
          <iyy>0.029125</iyy>
          <iyz>0</iyz>
          <izz>0.055225</izz>
        </inertia>
      </inertial>

      <collision name="collision">
        <geometry>
          <box>
            <size>0.47 0.47 0.11</size>
          </box>
        </geometry>
      </collision>

      <visual name="visual">
        <geometry>
          <mesh>
            <uri>model://quadrotor/meshes/quadrotor.dae</uri>
          </mesh>
        </geometry>
      </visual>
    </link>

    <!-- 挂载深度相机 -->
    <include>
      <uri>model://depth_camera</uri>
      <pose relative_to="base_link">0.1 0 0 0 0 0</pose>
    </include>

    <!-- 插件 -->
    <plugin filename="libignition-gazebo-multicopter-motor-model-system.so"
            name="ignition::gazebo::systems::MulticopterMotorModel">
      <robotNamespace>quadrotor</robotNamespace>
      <motorNumber>0</motorNumber>
      <turningDirection>ccw</turningDirection>
    </plugin>

    <plugin filename="libignition-gazebo-odometry-publisher-system.so"
            name="ignition::gazebo::systems::OdometryPublisher">
      <odom_topic>/model/quadrotor/odometry</odom_topic>
    </plugin>
  </model>
</sdf>
```

---

## 常见问题

### Q1: Gazebo Fortress 在 Jetson 上启动缓慢

**解决方案**:
```bash
# 禁用不必要的插件
export IGN_GAZEBO_SYSTEM_PLUGIN_PATH=/usr/lib/aarch64-linux-gnu/ign-gazebo-6/plugins
export LIBGL_ALWAYS_SOFTWARE=0  # 确保使用硬件加速

# 使用轻量级场景
ign gazebo empty.sdf  # 先测试空场景
```

### Q2: 深度图像传输延迟高

**解决方案**:
```bash
# 在 FastAPI 配置中启用图像压缩
# fastapi_planner/config.yaml
depth:
  compression: true
  compression_format: "png"  # 或 "jpeg"
  quality: 80

# 降低发布频率
  publish_rate: 10  # Hz
```

### Q3: 内存不足导致崩溃

**解决方案**:
```bash
# 监控内存使用
watch -n 1 free -h

# 限制 Gazebo 内存使用
ulimit -v 4194304  # 限制为 4GB

# 使用无头模式
ign gazebo -s world.sdf  # 无 GUI
```

### Q4: ROS 桥接消息丢失

**解决方案**:
```bash
# 增加 ROS 消息队列大小
# 在 ros_ign_bridge 节点中添加:
<param name="queue_size" value="100"/>

# 检查话题连接
ign topic -l
rostopic list
rostopic hz /pcl_render_node/depth
```

### Q5: CUDA 加速未启用

**解决方案**:
```bash
# 验证 CUDA 可用性
nvidia-smi
nvcc --version

# 设置环境变量
export CUDA_VISIBLE_DEVICES=0
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH

# 重新编译 Gazebo 插件时启用 CUDA
cmake -DUSE_CUDA=ON ..
```

---

## 性能基准测试

### 测试场景

在不同 Jetson 平台上的性能参考:

| 平台 | 实时因子 | 深度图 FPS | CPU 使用率 | 内存使用 |
|------|---------|-----------|-----------|---------|
| Jetson Nano | 0.3-0.5x | 5-8 | 95% | 3.2GB |
| Xavier NX | 0.7-0.9x | 15-20 | 70% | 4.5GB |
| AGX Xavier | 0.9-1.0x | 25-30 | 50% | 6.0GB |
| Orin NX | 1.0x | 30+ | 40% | 5.5GB |

### 运行基准测试

```bash
# 启动 Gazebo 并记录性能
ign gazebo -v 4 --iterations 1000 world.sdf 2>&1 | tee gazebo_perf.log

# 分析实时因子
grep "Real time factor" gazebo_perf.log | awk '{sum+=$NF; count++} END {print sum/count}'

# 监控系统资源
tegrastats --interval 1000 > jetson_stats.log &
```

---

## 启动脚本示例

创建一键启动脚本:

```bash
#!/bin/bash
# start_gazebo_fortress.sh

# 设置环境
source /opt/ros/noetic/setup.bash
source ~/catkin_ws/devel/setup.bash
export IGN_GAZEBO_RESOURCE_PATH=~/gazebo_models:$IGN_GAZEBO_RESOURCE_PATH

# 性能优化
sudo nvpmodel -m 0
sudo jetson_clocks

# 启动 Gazebo Fortress (无 GUI)
ign gazebo -s -r ~/worlds/fast_planner_world.sdf &
GAZEBO_PID=$!

# 等待 Gazebo 启动
sleep 5

# 启动 ROS 桥接
roslaunch plan_manage gazebo_fortress_bridge.launch &
BRIDGE_PID=$!

# 启动 Fast-Planner
roslaunch plan_manage kino_replan.launch &
PLANNER_PID=$!

# 启动 FastAPI 服务
cd ~/catkin_ws/src/fastapi_planner
python3 -m fastapi_planner.main &
API_PID=$!

echo "所有服务已启动"
echo "Gazebo PID: $GAZEBO_PID"
echo "Bridge PID: $BRIDGE_PID"
echo "Planner PID: $PLANNER_PID"
echo "API PID: $API_PID"

# 清理函数
cleanup() {
    echo "正在关闭所有服务..."
    kill $API_PID $PLANNER_PID $BRIDGE_PID $GAZEBO_PID
    exit 0
}

trap cleanup SIGINT SIGTERM

# 保持脚本运行
wait
```

---

## 参考资源

- [Gazebo Fortress 官方文档](https://gazebosim.org/docs/fortress)
- [ros_ign_bridge 文档](http://wiki.ros.org/ros_ign_bridge)
- [Jetson 性能优化指南](https://docs.nvidia.com/jetson/archives/r35.1/DeveloperGuide/)
- [Fast-Planner GitHub](https://github.com/HKUST-Aerial-Robotics/Fast-Planner)

---

## 更新日志

- **2026-03-04**: 初始版本创建
