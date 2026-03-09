cmake_minimum_required(VERSION 3.8)
project(odom_visualization)

set(CMAKE_CXX_STANDARD 14)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(visualization_msgs REQUIRED)
find_package(quadrotor_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(pose_utils REQUIRED)
find_package(Armadillo REQUIRED)

include_directories(
  include
  ${pose_utils_INCLUDE_DIRS}
  ${ARMADILLO_INCLUDE_DIRS}
)

# 如果上面的变量不存在，手动添加
if(NOT pose_utils_INCLUDE_DIRS)
  include_directories(${CMAKE_INSTALL_PREFIX}/include)
endif()

add_executable(odom_visualization src/odom_visualization.cpp)

ament_target_dependencies(odom_visualization
  rclcpp
  std_msgs
  geometry_msgs
  nav_msgs
  sensor_msgs
  visualization_msgs
  quadrotor_msgs
  tf2
  tf2_ros
  pose_utils
)

target_link_libraries(odom_visualization
  ${ARMADILLO_LIBRARIES}
  pose_utils::pose_utils
)

install(TARGETS
  odom_visualization
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()

