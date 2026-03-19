cmake_minimum_required(VERSION 3.8)
project(bspline_opt)

set(CMAKE_BUILD_TYPE "Release")
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -Wall")

set(NLOPT_INCLUDE_DIR "/usr/local/include")  
set(NLOPT_LIBRARY "/usr/local/lib/libnlopt.so")

# 查找依赖
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(visualization_msgs REQUIRED)
find_package(pcl_conversions REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(PCL 1.7 REQUIRED)
find_package(plan_env REQUIRED)
find_package(bspline REQUIRED)

# 包含目录
include_directories(
  include 
  ${EIGEN3_INCLUDE_DIR} 
  ${PCL_INCLUDE_DIRS}
  ${NLOPT_INCLUDE_DIR}  
)

# 库
add_library(bspline_opt 
  src/bspline_optimizer.cpp 
)

ament_target_dependencies(bspline_opt
  rclcpp
  std_msgs
  visualization_msgs
  pcl_conversions
  plan_env
  bspline
)

target_link_libraries(bspline_opt
  ${NLOPT_LIBRARY}   
)

# 安装
install(TARGETS
  bspline_opt
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY include/
  DESTINATION include/
)

# 导出依赖
ament_export_include_directories(include)
ament_export_libraries(bspline_opt)
ament_export_dependencies(
  rclcpp
  std_msgs
  visualization_msgs
  pcl_conversions
  plan_env
  bspline
)

ament_package()

