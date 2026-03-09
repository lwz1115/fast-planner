#!/bin/bash
xhost +local:docker

docker run -it --rm \
    --name fast_planner_py38 \
    --env="DISPLAY" --env="QT_X11_NO_MITSHM=1" \
    --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
    --volume="/media/zzxl/数据/my_projects/fastplanner:/root/catkin_ws:rw" \
    -p 1919:1919 \
    -p 8000:8000 \
    --privileged \
    fast-planner:py38
