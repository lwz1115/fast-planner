# FastAPI-Fast-Planner 接口

为 Fast-Planner ROS 轨迹规划系统提供 HTTP 访问的 REST API 服务。

## 目录

- [概述](#概述)
- [项目结构](#项目结构)
- [安装](#安装)
- [配置](#配置)
- [Docker 部署](#docker-部署)
- [使用方法](#使用方法)
- [深度图像处理](#深度图像处理)
- [ROS 话题要求](#ros-话题要求)
- [Fast-Planner 设置](#fast-planner-设置)
- [API 文档](#api-文档)
- [错误处理](#错误处理)
- [日志和监控](#日志和监控)
- [故障排除](#故障排除)
- [开发](#开发)
- [需求文档](#需求文档)

## 概述

## 项目结构

```
fastapi_planner/
├── __init__.py           # 包初始化
├── requirements.txt      # Python 依赖
├── config.yaml          # 服务配置
├── .env.example         # 环境变量模板
└── README_CN.md         # 本文件
```

## 安装

### 前置要求

- ROS Noetic（或 Melodic）
- Python 3.8+
- 已安装并配置的 Fast-Planner ROS 包

### 设置步骤

1. 安装 Python 依赖：
```bash
pip3 install -r requirements.txt
```

2. 配置环境变量：
```bash
cp .env.example .env
# 编辑 .env 文件设置您的配置
```

3. 更新配置：
```bash
# 编辑 config.yaml 以匹配您的 ROS 设置
nano config.yaml
```

## 配置

服务使用 YAML 配置文件和环境变量的组合。环境变量优先于 YAML 设置。

### config.yaml

主配置文件（`config.yaml`）包含按部分组织的所有服务参数：

#### ROS 配置（`ros`）

控制 ROS 连接和话题路由：

```yaml
ros:
  master_uri: "http://localhost:11311"  # ROS Master URI
  node_name: "fastapi_planner_bridge"   # 此服务的 ROS 节点名称
  topics:
    odometry: "/state_ukf/odom"         # 里程计话题 (nav_msgs/Odometry)
    goal: "/move_base_simple/goal"      # 默认目标话题 (geometry_msgs/PoseStamped)
    trajectory: "/planning/bspline"     # 轨迹结果话题 (plan_manage/Bspline)
    planning_goal: "/planning/goal"     # 备用目标话题
    kinodynamic_goal: null              # 可选：动力学特定目标话题
    topological_goal: null              # 可选：拓扑特定目标话题
```

**参数说明：**
- `master_uri`: ROS Master 地址（可被 `ROS_MASTER_URI` 环境变量覆盖）
- `node_name`: 此服务创建的 ROS 节点名称
- `topics.odometry`: 订阅四旋翼里程计数据的话题
- `topics.goal`: 发布目标位置的默认话题
- `topics.trajectory`: 订阅规划的 B 样条轨迹的话题
- `topics.kinodynamic_goal`: 可选的算法特定目标话题（未设置时使用 `goal`）
- `topics.topological_goal`: 可选的算法特定目标话题（未设置时使用 `goal`）

#### 规划配置（`planning`）

控制规划行为和限制：

```yaml
planning:
  default_max_velocity: 3.0           # 默认最大速度 (m/s)
  default_max_acceleration: 2.0       # 默认最大加速度 (m/s²)
  planning_timeout: 5.0               # 规划超时 (秒)
  trajectory_sample_rate: 10.0        # 航点采样率 (Hz)
  max_velocity_limit: 10.0            # 允许的最大速度 (m/s)
  max_acceleration_limit: 10.0        # 允许的最大加速度 (m/s²)
```

**参数说明：**
- `default_max_velocity`: 请求中未指定时使用的默认速度限制
- `default_max_acceleration`: 请求中未指定时使用的默认加速度限制
- `planning_timeout`: 等待 Fast-Planner 计算轨迹的最长时间
- `trajectory_sample_rate`: B 样条轨迹的采样频率（每秒航点数）
- `max_velocity_limit`: 速度验证的硬限制（超过此值的请求将被拒绝）
- `max_acceleration_limit`: 加速度验证的硬限制

#### 地图配置（`map`）

定义位置验证的地图边界：

```yaml
map:
  size_x: 40.0    # X 方向地图尺寸（米）
  size_y: 20.0    # Y 方向地图尺寸（米）
  size_z: 5.0     # Z 方向地图尺寸（米）
  origin_x: 0.0   # 地图原点 X 坐标
  origin_y: 0.0   # 地图原点 Y 坐标
  origin_z: 0.0   # 地图原点 Z 坐标
```

**参数说明：**
- `size_x`, `size_y`, `size_z`: 地图尺寸（米）
- `origin_x`, `origin_y`, `origin_z`: 地图原点坐标（用于坐标转换）

位置验证检查：`origin ≤ position ≤ origin + size`

#### 服务配置（`service`）

控制 FastAPI 服务行为：

```yaml
service:
  host: "0.0.0.0"              # 绑定地址
  port: 8000                   # 服务端口
  log_level: "info"            # 日志级别 (debug/info/warning/error/critical)
  enable_cors: true            # 启用 CORS 中间件
  cors_origins: ["*"]          # 允许的 CORS 来源
  docs_url: "/docs"            # Swagger UI 文档 URL
  redoc_url: "/redoc"          # ReDoc 文档 URL
  health_check:
    max_odometry_age: 1.0      # 里程计被视为过时前的最大年龄（秒）
    planner_check_interval: 5.0 # 检查 Fast-Planner 可用性的间隔（秒）
```

**参数说明：**
- `host`: 绑定的网络接口（0.0.0.0 = 所有接口）
- `port`: HTTP 服务的 TCP 端口（可被 `FASTAPI_PORT` 环境变量覆盖）
- `log_level`: 日志详细程度（可被 `LOG_LEVEL` 环境变量覆盖）
- `enable_cors`: 为 Web 客户端启用跨域资源共享
- `cors_origins`: 允许的来源列表（使用 `["*"]` 允许所有来源）
- `docs_url`: Swagger UI 文档的路径（设置为 `null` 禁用）
- `redoc_url`: ReDoc 文档的路径（设置为 `null` 禁用）
- `health_check.max_odometry_age`: 超过此时间的里程计被视为过时
- `health_check.planner_check_interval`: 验证 Fast-Planner 运行的频率

### 环境变量

环境变量会覆盖相应的 YAML 设置。参见 `.env.example` 获取模板。

#### 必需的环境变量

无 - 所有设置在 `config.yaml` 中都有默认值。

#### 可选的环境变量

**ROS 配置：**
- `ROS_MASTER_URI`: ROS Master 地址（覆盖 `ros.master_uri`）
  - 示例：`http://192.168.1.100:11311`
- `ROS_IP`: ROS 通信的 IP 地址（由 ROS 使用，服务不直接使用）
  - 示例：`192.168.1.50`
- `ROS_HOSTNAME`: ROS 通信的主机名
  - 示例：`robot-laptop`

**服务配置：**
- `FASTAPI_HOST`: 服务绑定地址（覆盖 `service.host`）
  - 示例：`0.0.0.0`（所有接口）或 `127.0.0.1`（仅本地）
- `FASTAPI_PORT`: 服务端口（覆盖 `service.port`）
  - 示例：`8000`
- `LOG_LEVEL`: 日志级别（覆盖 `service.log_level`）
  - 值：`debug`, `info`, `warning`, `error`, `critical`

**配置文件：**
- `CONFIG_FILE`: YAML 配置文件的路径
  - 默认：`./config.yaml`（相对于 fastapi_planner 目录）
  - 示例：`/etc/fastapi_planner/config.yaml`

### 配置优先级

设置按以下顺序应用（后者覆盖前者）：

1. 代码中的默认值
2. YAML 配置文件（`config.yaml`）
3. 环境变量

### 配置验证

服务在启动时验证所有配置：

- ROS Master URI 格式（必须以 `http://` 或 `https://` 开头）
- 端口号（必须在 1-65535 之间）
- 超时、速度、加速度的正值
- 地图尺寸（必须为正）
- 日志级别（必须是有效的级别名称）

如果验证失败，服务将退出并显示指示问题的错误消息。

## Docker 部署

服务设计为在带有 ROS 的 Docker 容器中运行。

### 使用 Docker Compose（推荐）

最简单的部署方式是使用 Docker Compose：

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f fastapi-planner

# 停止服务
docker-compose down
```

`docker-compose.yml` 文件包括：
- 使用 ROS 环境自动启动服务
- 开发的卷挂载
- 健康检查
- ROS 通信的网络主机模式
- 环境变量配置

### 直接使用 Docker

手动构建和运行：

```bash
# 构建镜像
docker build -f Dockerfile.dev -t fastapi-planner .

# 运行容器
docker run -it --network host \
  -e ROS_MASTER_URI=http://localhost:11311 \
  -e FASTAPI_PORT=8000 \
  -v $(pwd)/fastapi_planner:/root/catkin_ws/fastapi_planner \
  fastapi-planner

# 在容器内启动服务
source /opt/ros/noetic/setup.bash
source devel/setup.bash
python3 -m fastapi_planner.main
```

## 使用方法

### 运行服务

启动 FastAPI 服务：

```bash
# 首先确保 ROS 正在运行
roscore

# 在另一个终端中启动服务
python3 -m fastapi_planner.main
```

或直接使用 uvicorn：

```bash
uvicorn fastapi_planner.main:app --host 0.0.0.0 --port 8000
```

### API 端点

服务提供以下端点：

#### 规划端点
- `POST /plan` - 请求从起点到目标的轨迹规划
- `GET /odometry` - 获取当前四旋翼里程计状态

#### 地图更新端点
- `POST /map/depth` - 处理单张深度图像以更新占用地图
- `POST /map/depth/batch` - 批量处理多张深度图像

#### 监控端点
- `GET /health` - 检查服务健康状态
- `GET /metrics` - 获取性能指标和统计信息
- `GET /` - 服务信息

#### 文档端点
- `GET /docs` - 交互式 API 文档（Swagger UI）
- `GET /redoc` - 备用 API 文档（ReDoc）

详细的 API 文档包含请求/响应模式和示例，请参见：
- **交互式文档**：http://localhost:8000/docs（Swagger UI）
- **备用文档**：http://localhost:8000/redoc（ReDoc）
- **API 参考**：查看 `API参考.md` 获取详细的端点文档

### 快速开始示例

#### 规划轨迹

```bash
curl -X POST "http://localhost:8000/plan" \
  -H "Content-Type: application/json" \
  -d '{
    "start": {"x": 0.0, "y": 0.0, "z": 1.0},
    "goal": {"x": 10.0, "y": 5.0, "z": 1.5},
    "max_velocity": 3.0,
    "max_acceleration": 2.0,
    "algorithm": "kinodynamic"
  }'
```

**响应（成功）：**
```json
{
  "success": true,
  "trajectory": {
    "waypoints": [
      {
        "timestamp": 0.0,
        "position": {"x": 0.0, "y": 0.0, "z": 1.0},
        "velocity": {"x": 0.0, "y": 0.0, "z": 0.0},
        "acceleration": {"x": 0.5, "y": 0.2, "z": 0.0}
      }
    ],
    "total_duration": 5.2,
    "num_waypoints": 52
  },
  "error": null,
  "planning_time_ms": 45.3,
  "ros_planning_time_ms": 38.1,
  "total_time_ms": 52.7
}
```

#### 获取当前里程计

```bash
curl "http://localhost:8000/odometry"
```

**响应：**
```json
{
  "timestamp": 1699876543.123,
  "position": {"x": 1.2, "y": 0.5, "z": 1.0},
  "orientation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0},
  "linear_velocity": {"x": 0.5, "y": 0.0, "z": 0.0},
  "angular_velocity": {"x": 0.0, "y": 0.0, "z": 0.1}
}
```

#### 检查服务健康

```bash
curl "http://localhost:8000/health"
```

**响应：**
```json
{
  "status": "healthy",
  "ros_connected": true,
  "fast_planner_available": true,
  "uptime_seconds": 3600.5,
  "last_planning_success": 1699876543.123,
  "odometry_age_ms": 50.2
}
```

#### 获取性能指标

```bash
curl "http://localhost:8000/metrics"
```

**响应：**
```json
{
  "uptime_seconds": 3600.5,
  "total_requests": 150,
  "successful_requests": 142,
  "failed_requests": 8,
  "success_rate_percent": 94.67,
  "last_planning_success": 1699876543.123,
  "ros_connected": true
}
```

#### 处理深度图像

```bash
curl -X POST "http://localhost:8000/map/depth" \
  -H "Content-Type: application/json" \
  -d '{
    "depth_image": "iVBORw0KGgoAAAANSUhEUgAAAAUA...",
    "camera_intrinsics": {
      "fx": 525.0,
      "fy": 525.0,
      "cx": 319.5,
      "cy": 239.5,
      "width": 640,
      "height": 480
    },
    "camera_pose": {
      "position": {"x": 1.0, "y": 0.5, "z": 1.0},
      "orientation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0}
    },
    "depth_scale": 0.001,
    "timestamp": 1699876543.123,
    "frame_id": "camera_depth_optical_frame",
    "encoding": "16UC1"
  }'
```

**响应（成功）：**
```json
{
  "success": true,
  "points_generated": 15234,
  "processing_time_ms": 125.3,
  "timestamp": 1699876543.123,
  "message": "深度图像已处理并成功发布点云"
}
```

#### 批量处理深度图像

```bash
curl -X POST "http://localhost:8000/map/depth/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "depth_images": [
      {
        "depth_image": "iVBORw0KGgoAAAANSUhEUgAAAAUA...",
        "camera_intrinsics": {
          "fx": 525.0,
          "fy": 525.0,
          "cx": 319.5,
          "cy": 239.5,
          "width": 640,
          "height": 480
        },
        "camera_pose": {
          "position": {"x": 1.0, "y": 0.5, "z": 1.0},
          "orientation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0}
        },
        "depth_scale": 0.001,
        "timestamp": 1699876543.123
      }
    ]
  }'
```

**响应：**
```json
{
  "success": true,
  "total_images": 1,
  "successful": 1,
  "failed": 0,
  "results": [
    {
      "index": 0,
      "success": true,
      "points_generated": 15234,
      "processing_time_ms": 125.3
    }
  ],
  "total_processing_time_ms": 125.3
}
```

## 深度图像处理

服务提供深度图像处理端点，用于更新 Fast-Planner 使用的占用地图。深度图像被转换为 3D 点云并发布到 ROS 进行地图更新。

### 深度处理概述

深度处理流程：

1. **接收深度图像** - Base64 编码的深度图像及相机参数
2. **解码和验证** - 解码图像数据并验证尺寸/格式
3. **生成点云** - 使用相机内参将深度像素转换为 3D 点
4. **转换到世界坐标系** - 应用相机位姿变换
5. **发布到 ROS** - 将点云发送到 Fast-Planner 的地图更新话题
6. **返回结果** - 提供处理统计信息和成功状态

### 相机参数

相机内参定义了深度到 3D 转换的投影模型：

#### 必需参数

```json
{
  "fx": 525.0,      // X 方向焦距（像素）
  "fy": 525.0,      // Y 方向焦距（像素）
  "cx": 319.5,      // 主点 X 坐标（像素）
  "cy": 239.5,      // 主点 Y 坐标（像素）
  "width": 640,     // 图像宽度（像素）
  "height": 480     // 图像高度（像素）
}
```

#### 参数说明

- **fx, fy**: 焦距（像素）（来自相机标定）
  - 典型值：VGA 分辨率为 500-600
  - 如果像素非正方形，可以不同
  
- **cx, cy**: 主点（光学中心）（像素）
  - 通常接近图像中心：(width/2, height/2)
  - 可能由于镜头畸变校正而偏移
  
- **width, height**: 图像尺寸（像素）
  - 必须与实际深度图像大小匹配
  - 常见分辨率：640x480、1280x720、1920x1080

#### 相机位姿

相机位姿定义了在世界坐标系中的位置和方向：

```json
{
  "position": {
    "x": 1.0,    // 相机位置（米）
    "y": 0.5,
    "z": 1.0
  },
  "orientation": {
    "x": 0.0,    // 四元数方向
    "y": 0.0,
    "z": 0.0,
    "w": 1.0
  }
}
```

#### 获取相机参数

**从 ROS camera_info 话题：**
```bash
# 查看相机信息
rostopic echo /camera/depth/camera_info

# 提取参数
# K 矩阵：[fx, 0, cx, 0, fy, cy, 0, 0, 1]
# fx = K[0], fy = K[4], cx = K[2], cy = K[5]
```

**从相机标定文件：**
```yaml
# camera.yaml
camera_matrix:
  rows: 3
  cols: 3
  data: [525.0, 0.0, 319.5, 0.0, 525.0, 239.5, 0.0, 0.0, 1.0]
```

### 支持的深度图像格式

服务支持多种深度图像编码：

#### 编码类型

| 编码 | 位深度 | 数据类型 | 典型用途 |
|------|--------|----------|----------|
| `16UC1` | 16位 | 无符号整数 | 最常见（RealSense、Kinect）|
| `32FC1` | 32位 | 浮点数 | 高精度深度 |
| `mono16` | 16位 | 无符号整数 | 替代格式 |

#### 深度缩放

`depth_scale` 参数将像素值转换为米：

```python
depth_in_meters = pixel_value * depth_scale
```

**常见深度缩放：**
- **0.001**（1mm）：RealSense D435、D455
- **0.0001**（0.1mm）：高精度传感器
- **1.0**：预缩放的浮点图像（32FC1）

#### 图像编码

深度图像在发送前必须进行 Base64 编码：

**Python 示例：**
```python
import base64
import cv2

# 读取深度图像
depth_image = cv2.imread('depth.png', cv2.IMREAD_UNCHANGED)

# 编码为字节
_, buffer = cv2.imencode('.png', depth_image)

# Base64 编码
depth_base64 = base64.b64encode(buffer).decode('utf-8')
```

### 单张深度图像处理

处理单张深度图像以更新地图。

#### 端点

```
POST /map/depth
```

#### 请求模式

```json
{
  "depth_image": "string (base64)",
  "camera_intrinsics": {
    "fx": "number",
    "fy": "number", 
    "cx": "number",
    "cy": "number",
    "width": "integer",
    "height": "integer"
  },
  "camera_pose": {
    "position": {"x": "number", "y": "number", "z": "number"},
    "orientation": {"x": "number", "y": "number", "z": "number", "w": "number"}
  },
  "depth_scale": "number (默认: 0.001)",
  "timestamp": "number (可选)",
  "frame_id": "string (默认: 'camera_depth_optical_frame')",
  "encoding": "string (默认: '16UC1')"
}
```

#### 响应模式

```json
{
  "success": "boolean",
  "points_generated": "integer",
  "processing_time_ms": "number",
  "timestamp": "number",
  "message": "string"
}
```

### 批量深度图像处理

在单个请求中处理多张深度图像以提高效率。

#### 端点

```
POST /map/depth/batch
```

#### 请求模式

```json
{
  "depth_images": [
    {
      "depth_image": "string (base64)",
      "camera_intrinsics": {...},
      "camera_pose": {...},
      "depth_scale": "number",
      "timestamp": "number (可选)",
      "frame_id": "string (可选)",
      "encoding": "string (可选)"
    }
  ]
}
```

#### 响应模式

```json
{
  "success": "boolean",
  "total_images": "integer",
  "successful": "integer",
  "failed": "integer",
  "results": [
    {
      "index": "integer",
      "success": "boolean",
      "points_generated": "integer",
      "processing_time_ms": "number",
      "error": "string (如果失败)"
    }
  ],
  "total_processing_time_ms": "number"
}
```

### Python 客户端示例

#### 示例 1：从 RealSense 发送单张深度图像

```python
import requests
import base64
import cv2
import numpy as np
import pyrealsense2 as rs

# 配置 RealSense
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
pipeline.start(config)

# 获取相机内参
profile = pipeline.get_active_profile()
depth_profile = rs.video_stream_profile(profile.get_stream(rs.stream.depth))
intrinsics = depth_profile.get_intrinsics()

try:
    # 捕获帧
    frames = pipeline.wait_for_frames()
    depth_frame = frames.get_depth_frame()
    
    # 转换为 numpy 数组
    depth_image = np.asanyarray(depth_frame.get_data())
    
    # 编码为 base64
    _, buffer = cv2.imencode('.png', depth_image)
    depth_base64 = base64.b64encode(buffer).decode('utf-8')
    
    # 准备请求
    request_data = {
        "depth_image": depth_base64,
        "camera_intrinsics": {
            "fx": intrinsics.fx,
            "fy": intrinsics.fy,
            "cx": intrinsics.ppx,
            "cy": intrinsics.ppy,
            "width": intrinsics.width,
            "height": intrinsics.height
        },
        "camera_pose": {
            "position": {"x": 1.0, "y": 0.5, "z": 1.0},
            "orientation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0}
        },
        "depth_scale": 0.001,  # RealSense 深度缩放
        "encoding": "16UC1"
    }
    
    # 发送请求
    response = requests.post(
        "http://localhost:8000/map/depth",
        json=request_data
    )
    
    print(f"成功: {response.json()['success']}")
    print(f"生成点数: {response.json()['points_generated']}")
    print(f"处理时间: {response.json()['processing_time_ms']:.2f}ms")
    
finally:
    pipeline.stop()
```

#### 示例 2：从文件发送深度图像

```python
import requests
import base64
import cv2

def send_depth_image(image_path, camera_params, camera_pose):
    """发送深度图像文件到 API。"""
    
    # 读取深度图像
    depth_image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    
    # 编码为 base64
    _, buffer = cv2.imencode('.png', depth_image)
    depth_base64 = base64.b64encode(buffer).decode('utf-8')
    
    # 准备请求
    request_data = {
        "depth_image": depth_base64,
        "camera_intrinsics": camera_params,
        "camera_pose": camera_pose,
        "depth_scale": 0.001,
        "encoding": "16UC1"
    }
    
    # 发送请求
    response = requests.post(
        "http://localhost:8000/map/depth",
        json=request_data
    )
    
    return response.json()

# 使用示例
camera_params = {
    "fx": 525.0,
    "fy": 525.0,
    "cx": 319.5,
    "cy": 239.5,
    "width": 640,
    "height": 480
}

camera_pose = {
    "position": {"x": 1.0, "y": 0.5, "z": 1.0},
    "orientation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0}
}

result = send_depth_image("depth_image.png", camera_params, camera_pose)
print(f"结果: {result}")
```

#### 示例 3：批量处理多张图像

```python
import requests
import base64
import cv2
import glob

def process_depth_batch(image_paths, camera_params, camera_poses):
    """批量处理多张深度图像。"""
    
    depth_images = []
    
    for i, (image_path, pose) in enumerate(zip(image_paths, camera_poses)):
        # 读取并编码图像
        depth_image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        _, buffer = cv2.imencode('.png', depth_image)
        depth_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # 添加到批次
        depth_images.append({
            "depth_image": depth_base64,
            "camera_intrinsics": camera_params,
            "camera_pose": pose,
            "depth_scale": 0.001,
            "timestamp": 1699876543.0 + i * 0.1,
            "encoding": "16UC1"
        })
    
    # 发送批量请求
    response = requests.post(
        "http://localhost:8000/map/depth/batch",
        json={"depth_images": depth_images}
    )
    
    return response.json()

# 使用示例
image_paths = glob.glob("depth_images/*.png")
camera_params = {
    "fx": 525.0,
    "fy": 525.0,
    "cx": 319.5,
    "cy": 239.5,
    "width": 640,
    "height": 480
}

# 生成位姿（示例：沿 X 轴移动）
camera_poses = [
    {
        "position": {"x": i * 0.5, "y": 0.5, "z": 1.0},
        "orientation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0}
    }
    for i in range(len(image_paths))
]

result = process_depth_batch(image_paths, camera_params, camera_poses)
print(f"总图像数: {result['total_images']}")
print(f"成功: {result['successful']}")
print(f"失败: {result['failed']}")
print(f"总时间: {result['total_processing_time_ms']:.2f}ms")
```

#### 示例 4：与 ROS 集成

```python
import rospy
import requests
import base64
import cv2
import numpy as np
from sensor_msgs.msg import Image, CameraInfo
from geometry_msgs.msg import PoseStamped
from cv_bridge import CvBridge

class DepthImagePublisher:
    def __init__(self, api_url="http://localhost:8000"):
        self.api_url = api_url
        self.bridge = CvBridge()
        self.camera_info = None
        self.camera_pose = None
        
        # 订阅话题
        rospy.Subscriber("/camera/depth/image_raw", Image, self.depth_callback)
        rospy.Subscriber("/camera/depth/camera_info", CameraInfo, self.info_callback)
        rospy.Subscriber("/camera/pose", PoseStamped, self.pose_callback)
    
    def info_callback(self, msg):
        """存储相机内参。"""
        self.camera_info = {
            "fx": msg.K[0],
            "fy": msg.K[4],
            "cx": msg.K[2],
            "cy": msg.K[5],
            "width": msg.width,
            "height": msg.height
        }
    
    def pose_callback(self, msg):
        """存储相机位姿。"""
        self.camera_pose = {
            "position": {
                "x": msg.pose.position.x,
                "y": msg.pose.position.y,
                "z": msg.pose.position.z
            },
            "orientation": {
                "x": msg.pose.orientation.x,
                "y": msg.pose.orientation.y,
                "z": msg.pose.orientation.z,
                "w": msg.pose.orientation.w
            }
        }
    
    def depth_callback(self, msg):
        """处理深度图像并发送到 API。"""
        if self.camera_info is None or self.camera_pose is None:
            rospy.logwarn("等待相机信息和位姿...")
            return
        
        try:
            # 将 ROS 图像转换为 numpy
            depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
            
            # 编码为 base64
            _, buffer = cv2.imencode('.png', depth_image)
            depth_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # 准备请求
            request_data = {
                "depth_image": depth_base64,
                "camera_intrinsics": self.camera_info,
                "camera_pose": self.camera_pose,
                "depth_scale": 0.001,
                "timestamp": msg.header.stamp.to_sec(),
                "frame_id": msg.header.frame_id,
                "encoding": msg.encoding
            }
            
            # 发送到 API
            response = requests.post(
                f"{self.api_url}/map/depth",
                json=request_data,
                timeout=1.0
            )
            
            if response.json()["success"]:
                rospy.loginfo(f"已处理深度图像: {response.json()['points_generated']} 个点")
            else:
                rospy.logwarn(f"处理深度图像失败: {response.json()['message']}")
                
        except Exception as e:
            rospy.logerr(f"处理深度图像时出错: {e}")

if __name__ == "__main__":
    rospy.init_node("depth_image_publisher")
    publisher = DepthImagePublisher()
    rospy.spin()
```

## ROS 话题要求

服务需要以下 ROS 话题可用：

### 必需话题

#### 里程计话题（订阅）
- **话题**：`/state_ukf/odom`（可通过 `ros.topics.odometry` 配置）
- **消息类型**：`nav_msgs/Odometry`
- **用途**：提供当前四旋翼位置、方向和速度
- **要求**：
  - 必须以 ≥1 Hz 发布以保证可靠运行
  - 超过 1 秒的消息被视为过时
  - 在规划请求中 `use_current_odom: true` 时使用

#### 轨迹话题（订阅）
- **话题**：`/planning/bspline`（可通过 `ros.topics.trajectory` 配置）
- **消息类型**：`plan_manage/Bspline`
- **用途**：从 Fast-Planner 接收规划的 B 样条轨迹
- **要求**：
  - 由 Fast-Planner 在成功规划后发布
  - 包含 B 样条控制点和时间信息
  - 以配置的采样率（默认 10 Hz）转换为航点

#### 目标话题（发布）
- **话题**：`/move_base_simple/goal`（可通过 `ros.topics.goal` 配置）
- **消息类型**：`geometry_msgs/PoseStamped`
- **用途**：向 Fast-Planner 发送目标位置
- **要求**：
  - Fast-Planner 必须订阅此话题
  - 可以是算法特定的（见下面的算法选择）

### 算法特定话题

服务支持动力学和拓扑规划的算法特定目标话题：

#### 动力学算法
- **话题**：可通过 `ros.topics.kinodynamic_goal` 配置
- **默认**：如果未指定，使用 `ros.topics.goal`
- **使用**：在规划请求中设置 `algorithm: "kinodynamic"`

#### 拓扑算法
- **话题**：可通过 `ros.topics.topological_goal` 配置
- **默认**：如果未指定，使用 `ros.topics.goal`
- **使用**：在规划请求中设置 `algorithm: "topological"`

### 话题配置示例

```yaml
ros:
  topics:
    odometry: "/state_ukf/odom"
    goal: "/move_base_simple/goal"
    trajectory: "/planning/bspline"
    kinodynamic_goal: "/planning/kinodynamic/goal"  # 可选
    topological_goal: "/planning/topological/goal"  # 可选
```

### 验证话题

检查所需话题是否可用：

```bash
# 列出所有话题
rostopic list

# 检查里程计话题
rostopic echo /state_ukf/odom -n 1

# 检查轨迹话题
rostopic info /planning/bspline

# 监控目标发布
rostopic echo /move_base_simple/goal
```

## Fast-Planner 设置

### 前置要求

服务需要安装并运行 Fast-Planner。按照以下步骤操作：

### 1. 安装 Fast-Planner

```bash
# 克隆 Fast-Planner 仓库
cd ~/catkin_ws/src
git clone https://github.com/HKUST-Aerial-Robotics/Fast-Planner.git

# 安装依赖
sudo apt-get install ros-noetic-nlopt
sudo apt-get install libarmadillo-dev

# 构建
cd ~/catkin_ws
catkin_make
source devel/setup.bash
```

### 2. 配置 Fast-Planner

编辑 Fast-Planner 配置文件以匹配您的环境：

**地图配置**（`plan_manage/config/`）：
- 设置地图大小以匹配 `config.yaml` 地图尺寸
- 配置障碍物检测参数
- 设置规划算法参数

**启动文件**（`plan_manage/launch/`）：
- 验证话题名称与服务配置匹配
- 配置算法特定参数
- 设置可视化选项

### 3. 启动 Fast-Planner

#### 动力学规划

```bash
roslaunch plan_manage kino_replan.launch
```

这将启动：
- 使用动力学算法的 Fast-Planner 节点
- 地图服务器和障碍物检测
- RViz 可视化（可选）

#### 拓扑规划

```bash
roslaunch plan_manage topo_replan.launch
```

这将启动：
- 使用拓扑算法的 Fast-Planner 节点
- 地图服务器和障碍物检测
- RViz 可视化（可选）

### 4. 验证 Fast-Planner

检查 Fast-Planner 是否运行：

```bash
# 检查 Fast-Planner 节点
rosnode list | grep fast_planner

# 检查订阅的话题
rosnode info /fast_planner_node

# 验证轨迹话题
rostopic info /planning/bspline
```

### 5. 测试规划

使用 ROS 工具发送测试目标：

```bash
# 发布测试目标
rostopic pub /move_base_simple/goal geometry_msgs/PoseStamped \
  "header:
    frame_id: 'world'
  pose:
    position: {x: 10.0, y: 5.0, z: 1.5}
    orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}"

# 监控轨迹输出
rostopic echo /planning/bspline
```

### 与 FastAPI 服务集成

一旦 Fast-Planner 运行：

1. **启动 FastAPI 服务**：
   ```bash
   python3 -m fastapi_planner.main
   ```

2. **验证连接**：
   ```bash
   curl http://localhost:8000/health
   ```
   
   应返回 `"fast_planner_available": true`

3. **发送规划请求**：
   ```bash
   curl -X POST http://localhost:8000/plan \
     -H "Content-Type: application/json" \
     -d '{"start": {"x": 0, "y": 0, "z": 1}, "goal": {"x": 10, "y": 5, "z": 1.5}}'
   ```

### 常见 Fast-Planner 问题

**Fast-Planner 无响应：**
- 检查 Fast-Planner 节点是否运行：`rosnode list`
- 验证话题订阅：`rosnode info /fast_planner_node`
- 检查 Fast-Planner 日志中的错误
- 确保地图和障碍物已加载

**规划总是失败：**
- 验证地图边界与配置匹配
- 检查起点/目标位置是否有碰撞
- 增加 Fast-Planner 配置中的规划超时
- 检查 Fast-Planner 算法参数

**未收到轨迹：**
- 验证轨迹话题名称与配置匹配
- 检查消息类型：`rostopic type /planning/bspline`
- 监控话题发布：`rostopic hz /planning/bspline`
- 检查 Fast-Planner 是否在规划后发布

## API 文档

服务通过多个接口提供全面的 API 文档：

### 1. 交互式文档（Swagger UI）

访问：**http://localhost:8000/docs**

功能：
- 交互式 API 浏览器 - 直接从浏览器测试端点
- 查看完整的请求/响应模式
- 查看示例值和验证规则
- 下载 OpenAPI 规范（JSON/YAML）
- 测试身份验证和错误场景

### 2. 备用文档（ReDoc）

访问：**http://localhost:8000/redoc**

功能：
- 清晰、可读的文档布局
- 带示例的详细模式描述
- 多种语言的代码示例
- 跨所有端点的搜索功能
- 移动查看的响应式设计

### 3. API 参考文档

查看 `API参考.md` 获取完整的端点文档，包括：
- 详细的请求/响应模式
- 所有错误代码和状态代码
- cURL 和 Python 中的代码示例
- 参数验证规则
- 常见使用模式

### 4. OpenAPI 规范

服务自动生成 OpenAPI 3.0 规范：

**JSON 格式：** http://localhost:8000/openapi.json

使用此规范可以：
- 生成任何语言的客户端库
- 导入到 API 测试工具（Postman、Insomnia）
- 生成其他格式的文档
- 以编程方式验证请求/响应

### 自动文档生成

FastAPI 自动从以下内容生成文档：
- 类型提示和 Pydantic 模型
- 端点函数中的文档字符串
- 响应模型定义
- 异常处理器配置

文档始终与代码保持同步 - 无需手动更新！

## 错误处理

服务实现了全面的错误处理和结构化错误响应。查看 `错误处理.md` 获取详细文档：

- 错误类别和 HTTP 状态代码
- 异常类和使用方法
- 错误响应格式
- 日志行为
- 客户端错误处理示例

## 日志和监控

服务提供全面的日志和监控功能。查看 `日志监控.md` 获取详细文档：

- 结构化日志配置
- 使用关联 ID 进行请求/响应跟踪
- 性能指标和监控
- 带堆栈跟踪的错误日志
- 健康监控端点
- 与监控工具集成（Prometheus、ELK、Grafana）

## 故障排除

### 配置问题

**服务启动失败，提示"配置验证失败"：**
- 检查所有数值是否为正
- 验证日志级别是否为：debug、info、warning、error、critical 之一
- 确保 ROS Master URI 以 `http://` 或 `https://` 开头
- 验证端口号在 1 到 65535 之间

**"ROS Master not found" 错误：**
- 验证 ROS Master 是否运行：`roscore`
- 检查 `ROS_MASTER_URI` 环境变量或配置中的 `ros.master_uri`
- 测试 ROS 连接：`rostopic list`
- 如果使用远程 ROS Master，确保网络连接

**"配置文件未找到" 错误：**
- 检查 `CONFIG_FILE` 环境变量指向正确路径
- 验证 `config.yaml` 存在于 `fastapi_planner/` 目录中
- 如果从不同目录运行，使用绝对路径

**环境变量未生效：**
- 验证环境变量已导出：`echo $ROS_MASTER_URI`
- 检查变量名称完全匹配（区分大小写）
- 更改环境变量后重启服务
- 环境变量覆盖 YAML 设置

**浏览器中的 CORS 错误：**
- 在 config.yaml 中设置 `enable_cors: true`
- 将您的域添加到 `cors_origins` 列表
- 开发时使用 `["*"]`（生产环境不推荐）

### ROS 通信问题

**"Fast-Planner node not responding"：**
- 验证 Fast-Planner 是否运行：`rosnode list | grep fast_planner`
- 检查话题名称是否与 Fast-Planner 配置匹配
- 验证话题存在：`rostopic list`
- 检查话题类型：`rostopic info /planning/bspline`

**"Odometry unavailable" 错误：**
- 验证里程计话题是否发布：`rostopic echo /state_ukf/odom`
- 检查配置中的话题名称是否与您的里程计源匹配
- 确保里程计以合理的速率发布（>1 Hz）

**规划请求超时：**
- 增加 config.yaml 中的 `planning_timeout`
- 检查 Fast-Planner 日志中的错误
- 验证地图和障碍物已在 Fast-Planner 中加载
- 直接使用 ROS 工具测试 Fast-Planner

### 性能问题

**规划响应慢：**
- 检查 `planning_timeout` 设置（可能太高）
- 验证 Fast-Planner 未过载
- 监控 ROS Master 机器上的 CPU 使用率
- 如果不需要，考虑降低 `trajectory_sample_rate`

**内存使用率高：**
- 降低 `trajectory_sample_rate` 以生成更少的航点
- 检查 Fast-Planner 中的内存泄漏
- 使用 `docker stats` 监控（如果使用 Docker）

### 深度处理问题

**"深度图像格式无效" 错误：**
- 确保使用支持的格式：16UC1、32FC1、mono16
- 检查图像尺寸是否与相机内参匹配
- 验证 Base64 编码是否正确
- 确保图像数据未损坏

**"相机参数验证失败" 错误：**
- 确保焦距 `fx`、`fy` 为正数
- 确保主点 `cx`、`cy` 在图像范围内
- 确保图像尺寸 `width`、`height` 为正整数
- 确保深度缩放 `depth_scale` 为正数
- 确保四元数已归一化（x²+y²+z²+w²=1）

**"点云话题不可用" 错误：**
```bash
# 检查点云话题是否存在
rostopic list | grep point_cloud

# 检查 Fast-Planner 是否订阅了点云话题
rosnode info /fast_planner_node

# 验证点云发布
rostopic echo /camera/depth/points -n 1
```

**深度处理慢：**
- 减小图像分辨率
- 使用批量处理端点处理多张图像
- 检查网络延迟（如果 API 在远程）
- 监控服务器 CPU 使用率

**生成的点数为零：**
- 检查深度缩放是否正确
- 验证深度图像不全为零
- 确保相机内参正确
- 检查深度值范围是否合理

## 开发

这是基本项目结构。实现任务定义在：
`.kiro/specs/fastapi-fast-planner-interface/tasks.md`

## 需求文档

查看 `.kiro/specs/fastapi-fast-planner-interface/` 中的 `requirements.md` 和 `design.md` 获取详细规范。
