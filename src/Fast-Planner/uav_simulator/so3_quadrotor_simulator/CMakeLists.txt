cmake_minimum_required(VERSION 3.8)
project(so3_quadrotor_simulator)

set(CMAKE_CXX_STANDARD 14)

# 查找依赖
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(visualization_msgs REQUIRED)
find_package(quadrotor_msgs REQUIRED)
find_package(uav_utils REQUIRED)
find_package(cmake_utils REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(Armadillo REQUIRED)

# 包含目录
include_directories(
  include
  include/ode
  ${EIGEN3_INCLUDE_DIR}
  ${ARMADILLO_INCLUDE_DIRS}
)

# 库
add_library(quadrotor_dynamics 
  src/dynamics/Quadrotor.cpp
)

ament_target_dependencies(quadrotor_dynamics
  rclcpp
  std_msgs
  geometry_msgs
  nav_msgs
  sensor_msgs
  visualization_msgs
)

# 可执行文件
add_executable(quadrotor_simulator_so3
  src/quadrotor_simulator_so3.cpp
)

ament_target_dependencies(quadrotor_simulator_so3
  rclcpp
  std_msgs
  geometry_msgs
  nav_msgs
  sensor_msgs
  visualization_msgs
  quadrotor_msgs
  uav_utils
)

target_link_libraries(quadrotor_simulator_so3
  quadrotor_dynamics
  ${ARMADILLO_LIBRARIES}
)

# 安装
install(TARGETS
  quadrotor_dynamics
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
)

install(TARGETS
  quadrotor_simulator_so3
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY include/
  DESTINATION include/${PROJECT_NAME}
)

install(DIRECTORY launch/
  DESTINATION share/${PROJECT_NAME}/launch
)

install(DIRECTORY config/
  DESTINATION share/${PROJECT_NAME}/config
)

ament_package()


