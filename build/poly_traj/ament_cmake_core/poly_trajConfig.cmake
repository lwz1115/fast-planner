# generated from ament/cmake/core/templates/nameConfig.cmake.in

# prevent multiple inclusion
if(_poly_traj_CONFIG_INCLUDED)
  # ensure to keep the found flag the same
  if(NOT DEFINED poly_traj_FOUND)
    # explicitly set it to FALSE, otherwise CMake will set it to TRUE
    set(poly_traj_FOUND FALSE)
  elseif(NOT poly_traj_FOUND)
    # use separate condition to avoid uninitialized variable warning
    set(poly_traj_FOUND FALSE)
  endif()
  return()
endif()
set(_poly_traj_CONFIG_INCLUDED TRUE)

# output package information
if(NOT poly_traj_FIND_QUIETLY)
  message(STATUS "Found poly_traj: 0.0.0 (${poly_traj_DIR})")
endif()

# warn when using a deprecated package
if(NOT "" STREQUAL "")
  set(_msg "Package 'poly_traj' is deprecated")
  # append custom deprecation text if available
  if(NOT "" STREQUAL "TRUE")
    set(_msg "${_msg} ()")
  endif()
  # optionally quiet the deprecation message
  if(NOT ${poly_traj_DEPRECATED_QUIET})
    message(DEPRECATION "${_msg}")
  endif()
endif()

# flag package as ament-based to distinguish it after being find_package()-ed
set(poly_traj_FOUND_AMENT_PACKAGE TRUE)

# include all config extra files
set(_extras "ament_cmake_export_targets-extras.cmake;ament_cmake_export_dependencies-extras.cmake;ament_cmake_export_include_directories-extras.cmake")
foreach(_extra ${_extras})
  include("${poly_traj_DIR}/${_extra}")
endforeach()
