cmake_minimum_required(VERSION 3.8)
project(traj_utils)

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
find_package(bspline REQUIRED)
find_package(path_searching REQUIRED)
find_package(plan_env REQUIRED)
find_package(poly_traj REQUIRED)

# 包含目录
include_directories(
  include 
  ${EIGEN3_INCLUDE_DIR} 
  ${PCL_INCLUDE_DIRS}
  /root/colcon_ws/install/poly_traj/include
)

link_directories(${PCL_LIBRARY_DIRS})

# 库
add_library(traj_utils
  src/planning_visualization.cpp 
)

ament_target_dependencies(traj_utils
  rclcpp
  std_msgs
  visualization_msgs
  pcl_conversions
  bspline
  path_searching
  plan_env
  poly_traj
)

# 安装
install(TARGETS
  traj_utils
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY include/
  DESTINATION include/
)

# 导出依赖
ament_export_include_directories(include)
ament_export_libraries(traj_utils)
ament_export_dependencies(
  rclcpp
  std_msgs
  visualization_msgs
  pcl_conversions
  bspline
  path_searching
  plan_env
  poly_traj
)

ament_package()  

