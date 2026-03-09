// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from multi_map_server:msg/MultiSparseMap3D.idl
// generated code does not contain a copyright notice

#ifndef MULTI_MAP_SERVER__MSG__DETAIL__MULTI_SPARSE_MAP3_D__STRUCT_H_
#define MULTI_MAP_SERVER__MSG__DETAIL__MULTI_SPARSE_MAP3_D__STRUCT_H_

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
#include "multi_map_server/msg/detail/sparse_map3_d__struct.h"
// Member 'origins'
#include "geometry_msgs/msg/detail/pose__struct.h"

/// Struct defined in msg/MultiSparseMap3D in the package multi_map_server.
typedef struct multi_map_server__msg__MultiSparseMap3D
{
  multi_map_server__msg__SparseMap3D__Sequence maps;
  geometry_msgs__msg__Pose__Sequence origins;
} multi_map_server__msg__MultiSparseMap3D;

// Struct for a sequence of multi_map_server__msg__MultiSparseMap3D.
typedef struct multi_map_server__msg__MultiSparseMap3D__Sequence
{
  multi_map_server__msg__MultiSparseMap3D * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} multi_map_server__msg__MultiSparseMap3D__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // MULTI_MAP_SERVER__MSG__DETAIL__MULTI_SPARSE_MAP3_D__STRUCT_H_
