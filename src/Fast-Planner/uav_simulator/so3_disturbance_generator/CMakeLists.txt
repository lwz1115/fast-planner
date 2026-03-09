cmake_minimum_required(VERSION 3.8)
project(so3_disturbance_generator)

set(CMAKE_CXX_STANDARD 14)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(visualization_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(pose_utils REQUIRED)
find_package(Armadillo REQUIRED)

include_directories(
  include
  ${ARMADILLO_INCLUDE_DIRS}
)

add_executable(so3_disturbance_generator src/so3_disturbance_generator.cpp)

ament_target_dependencies(so3_disturbance_generator
  rclcpp
  std_msgs
  geometry_msgs
  nav_msgs
  sensor_msgs
  visualization_msgs
  tf2
  tf2_ros
  pose_utils
)

target_link_libraries(so3_disturbance_generator
  ${ARMADILLO_LIBRARIES}
  pose_utils::pose_utils
)

install(TARGETS
  so3_disturbance_generator
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY include/
  DESTINATION include
)

ament_package()

