cmake_minimum_required(VERSION 3.8)
project(cmake_utils)

find_package(ament_cmake REQUIRED)

set(CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR}/cmake)

file(GLOB CMAKE_UILTS_FILES cmake/*.cmake)

ament_package()


