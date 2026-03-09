cmake_minimum_required(VERSION 3.8)
project(so3_control)

set(CMAKE_CXX_STANDARD 14)

# 查找依赖
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(quadrotor_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(Eigen3 REQUIRED)

# 包含目录
include_directories(
  include
  ${EIGEN3_INCLUDE_DIR}
)

# 库
add_library(SO3Control 
  src/SO3Control.cpp
)

ament_target_dependencies(SO3Control
  rclcpp
  nav_msgs
  geometry_msgs
  quadrotor_msgs
)

# 可执行文件
add_executable(so3_control_node 
  src/so3_control_nodelet.cpp
)

ament_target_dependencies(so3_control_node
  rclcpp
  nav_msgs
  geometry_msgs
  sensor_msgs
  std_msgs
  quadrotor_msgs
  tf2
  tf2_ros
)

target_link_libraries(so3_control_node 
  SO3Control
)

# 安装
install(TARGETS
  SO3Control
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
)

install(TARGETS
  so3_control_node
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY include/
  DESTINATION include/${PROJECT_NAME}
)

install(DIRECTORY config/
  DESTINATION share/${PROJECT_NAME}/config
)

ament_package()

