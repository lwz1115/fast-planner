cmake_minimum_required(VERSION 3.8)
project(bspline)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -Wall")

# 查找依赖
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(visualization_msgs REQUIRED)
find_package(pcl_conversions REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(PCL 1.7 REQUIRED)

# 包含目录
include_directories(
  include 
  ${EIGEN3_INCLUDE_DIR} 
  ${PCL_INCLUDE_DIRS}
)

# 库
add_library(bspline 
  src/non_uniform_bspline.cpp 
)

ament_target_dependencies(bspline
  rclcpp
  std_msgs
  visualization_msgs
  pcl_conversions
)

# 安装
install(TARGETS
  bspline
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY include/
  DESTINATION include/${PROJECT_NAME}
)

ament_package()  

