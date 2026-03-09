# FastAPI-Fast-Planner 接口

为 Fast-Planner ROS 轨迹规划系统提供 HTTP 访问的 REST API 服务。

## 目录

- [概述](#概述)
- [项目结构](#项目结构)
- [安装](#安装)
- [配置](#配置)
- [Docker 部署](#docker-部署)
- [使用方法](#使用方法)
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

- `POST /plan` - 请求从起点到目标的轨迹规划
- `GET /odometry` - 获取当前四旋翼里程计状态
- `GET /health` - 检查服务健康状态
- `GET /metrics` - 获取性能指标和统计信息
- `GET /` - 服务信息
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

## 开发

这是基本项目结构。实现任务定义在：
`.kiro/specs/fastapi-fast-planner-interface/tasks.md`

## 需求文档

查看 `.kiro/specs/fastapi-fast-planner-interface/` 中的 `requirements.md` 和 `design.md` 获取详细规范。
