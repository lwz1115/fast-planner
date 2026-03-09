// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from multi_map_server:msg/VerticalOccupancyGridList.idl
// generated code does not contain a copyright notice

#ifndef MULTI_MAP_SERVER__MSG__DETAIL__VERTICAL_OCCUPANCY_GRID_LIST__STRUCT_H_
#define MULTI_MAP_SERVER__MSG__DETAIL__VERTICAL_OCCUPANCY_GRID_LIST__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'upper'
// Member 'lower'
// Member 'mass'
#include "rosidl_runtime_c/primitives_sequence.h"

/// Struct defined in msg/VerticalOccupancyGridList in the package multi_map_server.
typedef struct multi_map_server__msg__VerticalOccupancyGridList
{
  float x;
  float y;
  rosidl_runtime_c__int32__Sequence upper;
  rosidl_runtime_c__int32__Sequence lower;
  rosidl_runtime_c__int32__Sequence mass;
} multi_map_server__msg__VerticalOccupancyGridList;

// Struct for a sequence of multi_map_server__msg__VerticalOccupancyGridList.
typedef struct multi_map_server__msg__VerticalOccupancyGridList__Sequence
{
  multi_map_server__msg__VerticalOccupancyGridList * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} multi_map_server__msg__VerticalOccupancyGridList__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // MULTI_MAP_SERVER__MSG__DETAIL__VERTICAL_OCCUPANCY_GRID_LIST__STRUCT_H_
