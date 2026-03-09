#!/bin/bash

# 目标镜像名称
TARGET_IMAGE="fast-planner:latest"

# 容器名称
CONTAINER_NAME="fast_planner_ros2"

# 工作目录
WORKSPACE_PATH="/home/nvidia/ROS2/fastplanner"

echo "使用的镜像: $TARGET_IMAGE"

# 允许Docker访问X11显示
xhost +local:docker

# 检查容器是否存在
if docker ps -a --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo "容器 ${CONTAINER_NAME} 已存在"
    
    # 检查容器是否正在运行
    if docker ps --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        echo "容器正在运行，进入容器..."
        docker exec -it ${CONTAINER_NAME} bash
    else
        echo "容器已停止，启动并进入容器..."
        docker start ${CONTAINER_NAME}
        sleep 1  # 给容器一点启动时间
        docker exec -it ${CONTAINER_NAME} bash
    fi
else
    echo "创建新容器 ${CONTAINER_NAME}..."
    
    # 检查镜像是否存在
    if ! docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "^${TARGET_IMAGE}$"; then
        echo "错误: 镜像 ${TARGET_IMAGE} 不存在!"
        echo "请先构建镜像或手动安装ROS2后提交镜像"
        exit 1
    fi
    
    docker run -it \
        --name ${CONTAINER_NAME} \
        --network host \
        --privileged \
        -v ${WORKSPACE_PATH}:/root/colcon_ws:rw \
        -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
        -e DISPLAY=$DISPLAY \
        -e ROS_DOMAIN_ID=0 \
        -v /dev:/dev:rw \
        --restart unless-stopped \
        ${TARGET_IMAGE} \
        bash
    
    # 如果容器退出，询问是否删除
    if [ $? -ne 0 ]; then
        read -p "容器创建失败，是否删除容器? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker rm ${CONTAINER_NAME}
        fi
    fi
fi
