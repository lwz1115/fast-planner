#----------------------------------------------------------------
# Generated CMake target import file.
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "pose_utils::pose_utils" for configuration ""
set_property(TARGET pose_utils::pose_utils APPEND PROPERTY IMPORTED_CONFIGURATIONS NOCONFIG)
set_target_properties(pose_utils::pose_utils PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_NOCONFIG "CXX"
  IMPORTED_LOCATION_NOCONFIG "${_IMPORT_PREFIX}/lib/libpose_utils.a"
  )

list(APPEND _IMPORT_CHECK_TARGETS pose_utils::pose_utils )
list(APPEND _IMPORT_CHECK_FILES_FOR_pose_utils::pose_utils "${_IMPORT_PREFIX}/lib/libpose_utils.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
