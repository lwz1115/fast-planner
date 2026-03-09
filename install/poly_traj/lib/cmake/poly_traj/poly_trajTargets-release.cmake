#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "poly_traj::poly_traj" for configuration "Release"
set_property(TARGET poly_traj::poly_traj APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(poly_traj::poly_traj PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libpoly_traj.a"
  )

list(APPEND _IMPORT_CHECK_TARGETS poly_traj::poly_traj )
list(APPEND _IMPORT_CHECK_FILES_FOR_poly_traj::poly_traj "${_IMPORT_PREFIX}/lib/libpoly_traj.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
