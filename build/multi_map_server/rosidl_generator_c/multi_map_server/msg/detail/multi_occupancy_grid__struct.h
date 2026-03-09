// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from multi_map_server:msg/MultiOccupancyGrid.idl
// generated code does not contain a copyright notice

#ifndef MULTI_MAP_SERVER__MSG__DETAIL__MULTI_OCCUPANCY_GRID__STRUCT_H_
#define MULTI_MAP_SERVER__MSG__DETAIL__MULTI_OCCUPANCY_GRID__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'maps'
#include "nav_msgs/msg/detail/occupancy_grid__struct.h"
// Member 'origins'
#include "geometry_msgs/msg/detail/pose__struct.h"

/// Struct defined in msg/MultiOccupancyGrid in the package multi_map_server.
typedef struct multi_map_server__msg__MultiOccupancyGrid
{
  nav_msgs__msg__OccupancyGrid__Sequence maps;
  geometry_msgs__msg__Pose__Sequence origins;
} multi_map_server__msg__MultiOccupancyGrid;

// Struct for a sequence of multi_map_server__msg__MultiOccupancyGrid.
typedef struct multi_map_server__msg__MultiOccupancyGrid__Sequence
{
  multi_map_server__msg__MultiOccupancyGrid * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} multi_map_server__msg__MultiOccupancyGrid__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // MULTI_MAP_SERVER__MSG__DETAIL__MULTI_OCCUPANCY_GRID__STRUCT_H_
