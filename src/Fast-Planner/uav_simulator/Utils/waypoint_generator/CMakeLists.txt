cmake_minimum_required(VERSION 3.8)
project(waypoint_generator)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -O3")

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(visualization_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(Boost REQUIRED COMPONENTS system)

include_directories(
  include
  ${EIGEN3_INCLUDE_DIRS}
)

add_executable(waypoint_generator 
  src/waypoint_generator.cpp
)

ament_target_dependencies(waypoint_generator
  rclcpp
  tf2
  tf2_ros
  tf2_geometry_msgs
  nav_msgs
  geometry_msgs
  visualization_msgs
  sensor_msgs
  std_msgs
)

target_link_libraries(waypoint_generator
  ${Boost_LIBRARIES}
)

install(TARGETS
  waypoint_generator
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()

