#!/bin/bash
# FastAPI-Planner ROS2 安装和测试脚本

set -e  # 遇到错误立即退出

echo "=========================================="
echo "FastAPI-Planner ROS2 安装和测试"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查是否在正确的目录
if [ ! -f "setup.py" ]; then
    echo -e "${RED}错误: 请在 fastapi_planner 目录下运行此脚本${NC}"
    exit 1
fi

echo -e "${BLUE}步骤 1: 检查 ROS2 环境${NC}"
if [ -z "$ROS_DISTRO" ]; then
    echo -e "${RED}错误: ROS2 环境未加载${NC}"
    echo "请先运行: source /opt/ros/humble/setup.bash"
    echo "或者: source ~/colcon_ws/install/setup.bash"
    exit 1
fi
echo -e "${GREEN}✓ ROS2 环境已加载: $ROS_DISTRO${NC}"
echo ""

echo -e "${BLUE}步骤 2: 检查 Python 依赖${NC}"
echo "检查必需的 Python 包..."

# 检查 rclpy
if python3 -c "import rclpy" 2>/dev/null; then
    echo -e "${GREEN}✓ rclpy 已安装${NC}"
else
    echo -e "${RED}✗ rclpy 未安装${NC}"
    echo "请安装: sudo apt install python3-rclpy"
    exit 1
fi

# 检查 fastapi
if python3 -c "import fastapi" 2>/dev/null; then
    echo -e "${GREEN}✓ fastapi 已安装${NC}"
else
    echo -e "${YELLOW}! fastapi 未安装，正在安装...${NC}"
    pip3 install fastapi uvicorn[standard]
fi

# 检查 pydantic
if python3 -c "import pydantic" 2>/dev/null; then
    echo -e "${GREEN}✓ pydantic 已安装${NC}"
else
    echo -e "${YELLOW}! pydantic 未安装，正在安装...${NC}"
    pip3 install pydantic
fi

echo ""

echo -e "${BLUE}步骤 3: 安装 fastapi_planner 包${NC}"
pip3 install -e .
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ fastapi_planner 包安装成功${NC}"
else
    echo -e "${RED}✗ 安装失败${NC}"
    exit 1
fi
echo ""

echo -e "${BLUE}步骤 4: 验证模块导入${NC}"
python3 << 'EOF'
import sys
try:
    print("测试导入 fastapi_planner 模块...")
    from fastapi_planner.models import PlanRequest, Position
    print("✓ models 模块导入成功")

    from fastapi_planner.config import ROSTopicsConfig
    print("✓ config 模块导入成功")

    from fastapi_planner.ros_bridge import ROSBridge
    print("✓ ros_bridge 模块导入成功 (ROS2 版本)")

    print("\n所有模块导入成功！")
    sys.exit(0)
except Exception as e:
    print(f"✗ 模块导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}模块导入测试失败${NC}"
    exit 1
fi
echo ""

echo -e "${BLUE}步骤 5: 运行单元测试${NC}"
echo "运行算法选择测试..."
python3 run_algorithm_tests.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 单元测试通过${NC}"
else
    echo -e "${YELLOW}! 部分测试失败（可能正常，如果 ROS2 节点未运行）${NC}"
fi
echo ""

echo "=========================================="
echo -e "${GREEN}安装完成！${NC}"
echo "=========================================="
echo ""

echo -e "${YELLOW}下一步操作:${NC}"
echo ""
echo "1. 启动 ROS2 Fast-Planner 节点:"
echo -e "   ${GREEN}cd ~/colcon_ws${NC}"
echo -e "   ${GREEN}source install/setup.bash${NC}"
echo -e "   ${GREEN}ros2 launch plan_manage kino_replan.launch.py${NC}"
echo ""
echo "2. 在另一个终端启动 FastAPI 服务:"
echo -e "   ${GREEN}cd ~/colcon_ws/fastapi_planner${NC}"
echo -e "   ${GREEN}source ~/colcon_ws/install/setup.bash${NC}"
echo -e "   ${GREEN}python3 -m fastapi_planner.main${NC}"
echo ""
echo "3. 访问 API 文档:"
echo -e "   ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo "4. 测试规划 API:"
echo -e "   ${GREEN}curl -X POST http://localhost:8000/api/v1/plan \\${NC}"
echo -e "   ${GREEN}  -H 'Content-Type: application/json' \\${NC}"
echo -e "   ${GREEN}  -d '{\"start\": {\"x\": 0, \"y\": 0, \"z\": 1}, \"goal\": {\"x\": 5, \"y\": 0, \"z\": 1}}'${NC}"
echo ""

