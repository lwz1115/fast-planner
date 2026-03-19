cmake_minimum_required(VERSION 3.8)
project(plan_manage)

set(CMAKE_BUILD_TYPE "Release")
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -Wall -g")

# 查找依赖
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(visualization_msgs REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(pcl_conversions REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(PCL 1.7 REQUIRED)
find_package(plan_env REQUIRED)
find_package(path_searching REQUIRED)
find_package(bspline REQUIRED)
find_package(bspline_opt REQUIRED)
find_package(traj_utils REQUIRED)
find_package(quadrotor_msgs REQUIRED)
find_package(poly_traj REQUIRED)

# 生成消息
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/Bspline.msg"
  DEPENDENCIES std_msgs geometry_msgs builtin_interfaces
)

# 包含目录
include_directories(
  include
  ${EIGEN3_INCLUDE_DIR}
  ${PCL_INCLUDE_DIRS}
  /root/colcon_ws/install/poly_traj/include
)

# 可执行文件
add_executable(fast_planner_node
  src/fast_planner_node.cpp 
  src/kino_replan_fsm.cpp
  src/topo_replan_fsm.cpp
  src/planner_manager.cpp
)

ament_target_dependencies(fast_planner_node
  rclcpp
  std_msgs
  geometry_msgs
  nav_msgs
  sensor_msgs
  visualization_msgs
  pcl_conversions
  plan_env
  path_searching
  bspline
  bspline_opt
  traj_utils
  quadrotor_msgs
  poly_traj
)

# 链接生成的消息
rosidl_target_interfaces(fast_planner_node ${PROJECT_NAME} "rosidl_typesupport_cpp")

# 显式链接 NLopt 库
target_link_libraries(fast_planner_node
  nlopt
)

add_executable(traj_server 
  src/traj_server.cpp
)

ament_target_dependencies(traj_server
  rclcpp
  std_msgs
  geometry_msgs
  nav_msgs
  sensor_msgs
  visualization_msgs
  pcl_conversions
  plan_env
  path_searching
  bspline
  bspline_opt
  traj_utils
  quadrotor_msgs
  poly_traj
)

# 链接生成的消息
rosidl_target_interfaces(traj_server ${PROJECT_NAME} "rosidl_typesupport_cpp")

# 显式链接 NLopt 库（traj_server 也需要）
target_link_libraries(traj_server
  nlopt
)

# 安装
install(TARGETS
  fast_planner_node
  traj_server
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY include/
  DESTINATION include/${PROJECT_NAME}
)

# 安装launch文件
install(DIRECTORY launch/
  DESTINATION share/${PROJECT_NAME}/launch
  FILES_MATCHING PATTERN "*.py" PATTERN "*.xml"
)

# 安装config文件
install(DIRECTORY config/
  DESTINATION share/${PROJECT_NAME}/config
  FILES_MATCHING PATTERN "*.rviz" PATTERN "*.yaml"
)

ament_export_dependencies(rosidl_default_runtime)

ament_package()

