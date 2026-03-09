// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from multi_map_server:msg/MultiOccupancyGrid.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "multi_map_server/msg/detail/multi_occupancy_grid__rosidl_typesupport_introspection_c.h"
#include "multi_map_server/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "multi_map_server/msg/detail/multi_occupancy_grid__functions.h"
#include "multi_map_server/msg/detail/multi_occupancy_grid__struct.h"


// Include directives for member types
// Member `maps`
#include "nav_msgs/msg/occupancy_grid.h"
// Member `maps`
#include "nav_msgs/msg/detail/occupancy_grid__rosidl_typesupport_introspection_c.h"
// Member `origins`
#include "geometry_msgs/msg/pose.h"
// Member `origins`
#include "geometry_msgs/msg/detail/pose__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__MultiOccupancyGrid_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  multi_map_server__msg__MultiOccupancyGrid__init(message_memory);
}

void multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__MultiOccupancyGrid_fini_function(void * message_memory)
{
  multi_map_server__msg__MultiOccupancyGrid__fini(message_memory);
}

size_t multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__size_function__MultiOccupancyGrid__maps(
  const void * untyped_member)
{
  const nav_msgs__msg__OccupancyGrid__Sequence * member =
    (const nav_msgs__msg__OccupancyGrid__Sequence *)(untyped_member);
  return member->size;
}

const void * multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__get_const_function__MultiOccupancyGrid__maps(
  const void * untyped_member, size_t index)
{
  const nav_msgs__msg__OccupancyGrid__Sequence * member =
    (const nav_msgs__msg__OccupancyGrid__Sequence *)(untyped_member);
  return &member->data[index];
}

void * multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__get_function__MultiOccupancyGrid__maps(
  void * untyped_member, size_t index)
{
  nav_msgs__msg__OccupancyGrid__Sequence * member =
    (nav_msgs__msg__OccupancyGrid__Sequence *)(untyped_member);
  return &member->data[index];
}

void multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__fetch_function__MultiOccupancyGrid__maps(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const nav_msgs__msg__OccupancyGrid * item =
    ((const nav_msgs__msg__OccupancyGrid *)
    multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__get_const_function__MultiOccupancyGrid__maps(untyped_member, index));
  nav_msgs__msg__OccupancyGrid * value =
    (nav_msgs__msg__OccupancyGrid *)(untyped_value);
  *value = *item;
}

void multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__assign_function__MultiOccupancyGrid__maps(
  void * untyped_member, size_t index, const void * untyped_value)
{
  nav_msgs__msg__OccupancyGrid * item =
    ((nav_msgs__msg__OccupancyGrid *)
    multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__get_function__MultiOccupancyGrid__maps(untyped_member, index));
  const nav_msgs__msg__OccupancyGrid * value =
    (const nav_msgs__msg__OccupancyGrid *)(untyped_value);
  *item = *value;
}

bool multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__resize_function__MultiOccupancyGrid__maps(
  void * untyped_member, size_t size)
{
  nav_msgs__msg__OccupancyGrid__Sequence * member =
    (nav_msgs__msg__OccupancyGrid__Sequence *)(untyped_member);
  nav_msgs__msg__OccupancyGrid__Sequence__fini(member);
  return nav_msgs__msg__OccupancyGrid__Sequence__init(member, size);
}

size_t multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__size_function__MultiOccupancyGrid__origins(
  const void * untyped_member)
{
  const geometry_msgs__msg__Pose__Sequence * member =
    (const geometry_msgs__msg__Pose__Sequence *)(untyped_member);
  return member->size;
}

const void * multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__get_const_function__MultiOccupancyGrid__origins(
  const void * untyped_member, size_t index)
{
  const geometry_msgs__msg__Pose__Sequence * member =
    (const geometry_msgs__msg__Pose__Sequence *)(untyped_member);
  return &member->data[index];
}

void * multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__get_function__MultiOccupancyGrid__origins(
  void * untyped_member, size_t index)
{
  geometry_msgs__msg__Pose__Sequence * member =
    (geometry_msgs__msg__Pose__Sequence *)(untyped_member);
  return &member->data[index];
}

void multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__fetch_function__MultiOccupancyGrid__origins(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const geometry_msgs__msg__Pose * item =
    ((const geometry_msgs__msg__Pose *)
    multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__get_const_function__MultiOccupancyGrid__origins(untyped_member, index));
  geometry_msgs__msg__Pose * value =
    (geometry_msgs__msg__Pose *)(untyped_value);
  *value = *item;
}

void multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__assign_function__MultiOccupancyGrid__origins(
  void * untyped_member, size_t index, const void * untyped_value)
{
  geometry_msgs__msg__Pose * item =
    ((geometry_msgs__msg__Pose *)
    multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__get_function__MultiOccupancyGrid__origins(untyped_member, index));
  const geometry_msgs__msg__Pose * value =
    (const geometry_msgs__msg__Pose *)(untyped_value);
  *item = *value;
}

bool multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__resize_function__MultiOccupancyGrid__origins(
  void * untyped_member, size_t size)
{
  geometry_msgs__msg__Pose__Sequence * member =
    (geometry_msgs__msg__Pose__Sequence *)(untyped_member);
  geometry_msgs__msg__Pose__Sequence__fini(member);
  return geometry_msgs__msg__Pose__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__MultiOccupancyGrid_message_member_array[2] = {
  {
    "maps",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(multi_map_server__msg__MultiOccupancyGrid, maps),  // bytes offset in struct
    NULL,  // default value
    multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__size_function__MultiOccupancyGrid__maps,  // size() function pointer
    multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__get_const_function__MultiOccupancyGrid__maps,  // get_const(index) function pointer
    multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__get_function__MultiOccupancyGrid__maps,  // get(index) function pointer
    multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__fetch_function__MultiOccupancyGrid__maps,  // fetch(index, &value) function pointer
    multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__assign_function__MultiOccupancyGrid__maps,  // assign(index, value) function pointer
    multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__resize_function__MultiOccupancyGrid__maps  // resize(index) function pointer
  },
  {
    "origins",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(multi_map_server__msg__MultiOccupancyGrid, origins),  // bytes offset in struct
    NULL,  // default value
    multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__size_function__MultiOccupancyGrid__origins,  // size() function pointer
    multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__get_const_function__MultiOccupancyGrid__origins,  // get_const(index) function pointer
    multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__get_function__MultiOccupancyGrid__origins,  // get(index) function pointer
    multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__fetch_function__MultiOccupancyGrid__origins,  // fetch(index, &value) function pointer
    multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__assign_function__MultiOccupancyGrid__origins,  // assign(index, value) function pointer
    multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__resize_function__MultiOccupancyGrid__origins  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__MultiOccupancyGrid_message_members = {
  "multi_map_server__msg",  // message namespace
  "MultiOccupancyGrid",  // message name
  2,  // number of fields
  sizeof(multi_map_server__msg__MultiOccupancyGrid),
  multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__MultiOccupancyGrid_message_member_array,  // message members
  multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__MultiOccupancyGrid_init_function,  // function to initialize message memory (memory has to be allocated)
  multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__MultiOccupancyGrid_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__MultiOccupancyGrid_message_type_support_handle = {
  0,
  &multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__MultiOccupancyGrid_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_multi_map_server
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, multi_map_server, msg, MultiOccupancyGrid)() {
  multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__MultiOccupancyGrid_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, nav_msgs, msg, OccupancyGrid)();
  multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__MultiOccupancyGrid_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, geometry_msgs, msg, Pose)();
  if (!multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__MultiOccupancyGrid_message_type_support_handle.typesupport_identifier) {
    multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__MultiOccupancyGrid_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &multi_map_server__msg__MultiOccupancyGrid__rosidl_typesupport_introspection_c__MultiOccupancyGrid_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
