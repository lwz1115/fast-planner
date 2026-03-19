cmake_minimum_required(VERSION 3.8)
project(local_sensing_node)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_BUILD_TYPE Release)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -use_fast_math")

set(ENABLE_CUDA false)
# set(ENABLE_CUDA true)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(pcl_conversions REQUIRED)
find_package(quadrotor_msgs REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(PCL REQUIRED)

include_directories(
  ${EIGEN3_INCLUDE_DIRS}
  ${PCL_INCLUDE_DIRS}
)

if(ENABLE_CUDA)
  find_package(CUDA REQUIRED)
  find_package(OpenCV REQUIRED)
  find_package(cv_bridge REQUIRED)
  find_package(image_transport REQUIRED)
  find_package(Boost REQUIRED COMPONENTS system filesystem)
  
  set(CUDA_NVCC_FLAGS ${CUDA_NVCC_FLAGS};-O3 -use_fast_math)
  set(CUDA_NVCC_FLAGS 
      -gencode arch=compute_61,code=sm_61;
  )
  set(CUDA_PROPAGATE_HOST_FLAGS OFF)
  
  include_directories(
    ${OpenCV_INCLUDE_DIRS}
    ${Boost_INCLUDE_DIRS}
  )
  
  cuda_add_library(depth_render_cuda
      src/depth_render.cu
  )
  
  add_executable(pcl_render_node
    src/pcl_render_node.cpp
  )
  
  ament_target_dependencies(pcl_render_node
    rclcpp
    std_msgs
    geometry_msgs
    nav_msgs
    sensor_msgs
    pcl_conversions
    quadrotor_msgs
    cv_bridge
    image_transport
  )
  
  target_link_libraries(pcl_render_node
    depth_render_cuda
    ${OpenCV_LIBS}
    ${Boost_LIBRARIES}
    ${PCL_LIBRARIES}
  )
else()
  add_executable(pcl_render_node
    src/pointcloud_render_node.cpp
  )
  
  ament_target_dependencies(pcl_render_node
    rclcpp
    std_msgs
    geometry_msgs
    nav_msgs
    sensor_msgs
    pcl_conversions
    quadrotor_msgs
  )
  
  target_link_libraries(pcl_render_node
    ${PCL_LIBRARIES}
  )
endif()

install(TARGETS
  pcl_render_node
  DESTINATION lib/${PROJECT_NAME}
)

if(ENABLE_CUDA)
  install(TARGETS
    depth_render_cuda
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
  )
endif()

install(DIRECTORY params/
  DESTINATION share/${PROJECT_NAME}/params
)

ament_package()

