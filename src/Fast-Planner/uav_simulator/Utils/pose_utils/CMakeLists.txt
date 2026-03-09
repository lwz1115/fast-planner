cmake_minimum_required(VERSION 3.8)
project(pose_utils)

set(CMAKE_CXX_STANDARD 14)

# 查找依赖
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(Armadillo REQUIRED)

# 包含目录
include_directories(
  include
  ${ARMADILLO_INCLUDE_DIRS}
)

# 库
add_library(pose_utils 
  src/pose_utils.cpp
)

ament_target_dependencies(pose_utils
  rclcpp
)

target_link_libraries(pose_utils
  ${ARMADILLO_LIBRARIES}
)

# 安装
install(TARGETS
  pose_utils
  EXPORT pose_utilsTargets
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY include/
  DESTINATION include
)

install(EXPORT pose_utilsTargets
  FILE pose_utilsTargets.cmake
  NAMESPACE pose_utils::
  DESTINATION lib/cmake/${PROJECT_NAME}
)

ament_export_targets(pose_utilsTargets HAS_LIBRARY_TARGET)
ament_export_dependencies(rclcpp Armadillo)
ament_export_include_directories(include)

ament_package()

