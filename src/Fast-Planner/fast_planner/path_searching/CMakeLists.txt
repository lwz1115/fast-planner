cmake_minimum_required(VERSION 3.8)
project(path_searching)

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
find_package(plan_env REQUIRED)

# 包含目录
include_directories(
  include 
  ${EIGEN3_INCLUDE_DIR} 
  ${PCL_INCLUDE_DIRS}
)

# 库
add_library(path_searching 
  src/kinodynamic_astar.cpp 
  src/astar.cpp
  src/topo_prm.cpp
)

ament_target_dependencies(path_searching
  rclcpp
  std_msgs
  visualization_msgs
  pcl_conversions
  plan_env
)

# 安装
install(TARGETS
  path_searching
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY include/
  DESTINATION include/
)

# 导出依赖
ament_export_include_directories(include)
ament_export_libraries(path_searching)
ament_export_dependencies(
  rclcpp
  std_msgs
  visualization_msgs
  pcl_conversions
  plan_env
)

ament_package()  

