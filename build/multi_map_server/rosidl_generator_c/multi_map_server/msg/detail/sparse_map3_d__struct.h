// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from multi_map_server:msg/SparseMap3D.idl
// generated code does not contain a copyright notice

#ifndef MULTI_MAP_SERVER__MSG__DETAIL__SPARSE_MAP3_D__STRUCT_H_
#define MULTI_MAP_SERVER__MSG__DETAIL__SPARSE_MAP3_D__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.h"
// Member 'info'
#include "nav_msgs/msg/detail/map_meta_data__struct.h"
// Member 'lists'
#include "multi_map_server/msg/detail/vertical_occupancy_grid_list__struct.h"

/// Struct defined in msg/SparseMap3D in the package multi_map_server.
typedef struct multi_map_server__msg__SparseMap3D
{
  std_msgs__msg__Header header;
  nav_msgs__msg__MapMetaData info;
  multi_map_server__msg__VerticalOccupancyGridList__Sequence lists;
} multi_map_server__msg__SparseMap3D;

// Struct for a sequence of multi_map_server__msg__SparseMap3D.
typedef struct multi_map_server__msg__SparseMap3D__Sequence
{
  multi_map_server__msg__SparseMap3D * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} multi_map_server__msg__SparseMap3D__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // MULTI_MAP_SERVER__MSG__DETAIL__SPARSE_MAP3_D__STRUCT_H_
