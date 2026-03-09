cmake_minimum_required(VERSION 3.8)
project(poly_traj)

set(CMAKE_BUILD_TYPE "Release")
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -Wall -g")

# 查找依赖
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(Eigen3 REQUIRED)

# 包含目录
include_directories(
  include
  ${EIGEN3_INCLUDE_DIR}
)

# 库
add_library(poly_traj 
  src/polynomial_traj.cpp 
)

ament_target_dependencies(poly_traj
  rclcpp
  std_msgs
)

# 安装
install(TARGETS
  poly_traj
  EXPORT poly_trajTargets
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY include/
  DESTINATION include/${PROJECT_NAME}
)

install(EXPORT poly_trajTargets
  FILE poly_trajTargets.cmake
  NAMESPACE poly_traj::
  DESTINATION lib/cmake/${PROJECT_NAME}
)

ament_export_targets(poly_trajTargets HAS_LIBRARY_TARGET)
ament_export_dependencies(rclcpp std_msgs Eigen3)
ament_export_include_directories(include)

ament_package()  

