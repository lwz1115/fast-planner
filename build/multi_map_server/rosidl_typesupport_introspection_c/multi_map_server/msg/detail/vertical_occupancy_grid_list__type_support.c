// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from multi_map_server:msg/VerticalOccupancyGridList.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "multi_map_server/msg/detail/vertical_occupancy_grid_list__rosidl_typesupport_introspection_c.h"
#include "multi_map_server/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "multi_map_server/msg/detail/vertical_occupancy_grid_list__functions.h"
#include "multi_map_server/msg/detail/vertical_occupancy_grid_list__struct.h"


// Include directives for member types
// Member `upper`
// Member `lower`
// Member `mass`
#include "rosidl_runtime_c/primitives_sequence_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__VerticalOccupancyGridList_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  multi_map_server__msg__VerticalOccupancyGridList__init(message_memory);
}

void multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__VerticalOccupancyGridList_fini_function(void * message_memory)
{
  multi_map_server__msg__VerticalOccupancyGridList__fini(message_memory);
}

size_t multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__size_function__VerticalOccupancyGridList__upper(
  const void * untyped_member)
{
  const rosidl_runtime_c__int32__Sequence * member =
    (const rosidl_runtime_c__int32__Sequence *)(untyped_member);
  return member->size;
}

const void * multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__get_const_function__VerticalOccupancyGridList__upper(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__int32__Sequence * member =
    (const rosidl_runtime_c__int32__Sequence *)(untyped_member);
  return &member->data[index];
}

void * multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__get_function__VerticalOccupancyGridList__upper(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__int32__Sequence * member =
    (rosidl_runtime_c__int32__Sequence *)(untyped_member);
  return &member->data[index];
}

void multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__fetch_function__VerticalOccupancyGridList__upper(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const int32_t * item =
    ((const int32_t *)
    multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__get_const_function__VerticalOccupancyGridList__upper(untyped_member, index));
  int32_t * value =
    (int32_t *)(untyped_value);
  *value = *item;
}

void multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__assign_function__VerticalOccupancyGridList__upper(
  void * untyped_member, size_t index, const void * untyped_value)
{
  int32_t * item =
    ((int32_t *)
    multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__get_function__VerticalOccupancyGridList__upper(untyped_member, index));
  const int32_t * value =
    (const int32_t *)(untyped_value);
  *item = *value;
}

bool multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__resize_function__VerticalOccupancyGridList__upper(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__int32__Sequence * member =
    (rosidl_runtime_c__int32__Sequence *)(untyped_member);
  rosidl_runtime_c__int32__Sequence__fini(member);
  return rosidl_runtime_c__int32__Sequence__init(member, size);
}

size_t multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__size_function__VerticalOccupancyGridList__lower(
  const void * untyped_member)
{
  const rosidl_runtime_c__int32__Sequence * member =
    (const rosidl_runtime_c__int32__Sequence *)(untyped_member);
  return member->size;
}

const void * multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__get_const_function__VerticalOccupancyGridList__lower(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__int32__Sequence * member =
    (const rosidl_runtime_c__int32__Sequence *)(untyped_member);
  return &member->data[index];
}

void * multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__get_function__VerticalOccupancyGridList__lower(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__int32__Sequence * member =
    (rosidl_runtime_c__int32__Sequence *)(untyped_member);
  return &member->data[index];
}

void multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__fetch_function__VerticalOccupancyGridList__lower(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const int32_t * item =
    ((const int32_t *)
    multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__get_const_function__VerticalOccupancyGridList__lower(untyped_member, index));
  int32_t * value =
    (int32_t *)(untyped_value);
  *value = *item;
}

void multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__assign_function__VerticalOccupancyGridList__lower(
  void * untyped_member, size_t index, const void * untyped_value)
{
  int32_t * item =
    ((int32_t *)
    multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__get_function__VerticalOccupancyGridList__lower(untyped_member, index));
  const int32_t * value =
    (const int32_t *)(untyped_value);
  *item = *value;
}

bool multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__resize_function__VerticalOccupancyGridList__lower(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__int32__Sequence * member =
    (rosidl_runtime_c__int32__Sequence *)(untyped_member);
  rosidl_runtime_c__int32__Sequence__fini(member);
  return rosidl_runtime_c__int32__Sequence__init(member, size);
}

size_t multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__size_function__VerticalOccupancyGridList__mass(
  const void * untyped_member)
{
  const rosidl_runtime_c__int32__Sequence * member =
    (const rosidl_runtime_c__int32__Sequence *)(untyped_member);
  return member->size;
}

const void * multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__get_const_function__VerticalOccupancyGridList__mass(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__int32__Sequence * member =
    (const rosidl_runtime_c__int32__Sequence *)(untyped_member);
  return &member->data[index];
}

void * multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__get_function__VerticalOccupancyGridList__mass(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__int32__Sequence * member =
    (rosidl_runtime_c__int32__Sequence *)(untyped_member);
  return &member->data[index];
}

void multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__fetch_function__VerticalOccupancyGridList__mass(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const int32_t * item =
    ((const int32_t *)
    multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__get_const_function__VerticalOccupancyGridList__mass(untyped_member, index));
  int32_t * value =
    (int32_t *)(untyped_value);
  *value = *item;
}

void multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__assign_function__VerticalOccupancyGridList__mass(
  void * untyped_member, size_t index, const void * untyped_value)
{
  int32_t * item =
    ((int32_t *)
    multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__get_function__VerticalOccupancyGridList__mass(untyped_member, index));
  const int32_t * value =
    (const int32_t *)(untyped_value);
  *item = *value;
}

bool multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__resize_function__VerticalOccupancyGridList__mass(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__int32__Sequence * member =
    (rosidl_runtime_c__int32__Sequence *)(untyped_member);
  rosidl_runtime_c__int32__Sequence__fini(member);
  return rosidl_runtime_c__int32__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__VerticalOccupancyGridList_message_member_array[5] = {
  {
    "x",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(multi_map_server__msg__VerticalOccupancyGridList, x),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "y",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(multi_map_server__msg__VerticalOccupancyGridList, y),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "upper",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT32,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(multi_map_server__msg__VerticalOccupancyGridList, upper),  // bytes offset in struct
    NULL,  // default value
    multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__size_function__VerticalOccupancyGridList__upper,  // size() function pointer
    multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__get_const_function__VerticalOccupancyGridList__upper,  // get_const(index) function pointer
    multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__get_function__VerticalOccupancyGridList__upper,  // get(index) function pointer
    multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__fetch_function__VerticalOccupancyGridList__upper,  // fetch(index, &value) function pointer
    multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__assign_function__VerticalOccupancyGridList__upper,  // assign(index, value) function pointer
    multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__resize_function__VerticalOccupancyGridList__upper  // resize(index) function pointer
  },
  {
    "lower",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT32,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(multi_map_server__msg__VerticalOccupancyGridList, lower),  // bytes offset in struct
    NULL,  // default value
    multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__size_function__VerticalOccupancyGridList__lower,  // size() function pointer
    multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__get_const_function__VerticalOccupancyGridList__lower,  // get_const(index) function pointer
    multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__get_function__VerticalOccupancyGridList__lower,  // get(index) function pointer
    multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__fetch_function__VerticalOccupancyGridList__lower,  // fetch(index, &value) function pointer
    multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__assign_function__VerticalOccupancyGridList__lower,  // assign(index, value) function pointer
    multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__resize_function__VerticalOccupancyGridList__lower  // resize(index) function pointer
  },
  {
    "mass",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT32,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(multi_map_server__msg__VerticalOccupancyGridList, mass),  // bytes offset in struct
    NULL,  // default value
    multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__size_function__VerticalOccupancyGridList__mass,  // size() function pointer
    multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__get_const_function__VerticalOccupancyGridList__mass,  // get_const(index) function pointer
    multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__get_function__VerticalOccupancyGridList__mass,  // get(index) function pointer
    multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__fetch_function__VerticalOccupancyGridList__mass,  // fetch(index, &value) function pointer
    multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__assign_function__VerticalOccupancyGridList__mass,  // assign(index, value) function pointer
    multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__resize_function__VerticalOccupancyGridList__mass  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__VerticalOccupancyGridList_message_members = {
  "multi_map_server__msg",  // message namespace
  "VerticalOccupancyGridList",  // message name
  5,  // number of fields
  sizeof(multi_map_server__msg__VerticalOccupancyGridList),
  multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__VerticalOccupancyGridList_message_member_array,  // message members
  multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__VerticalOccupancyGridList_init_function,  // function to initialize message memory (memory has to be allocated)
  multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__VerticalOccupancyGridList_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__VerticalOccupancyGridList_message_type_support_handle = {
  0,
  &multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__VerticalOccupancyGridList_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_multi_map_server
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, multi_map_server, msg, VerticalOccupancyGridList)() {
  if (!multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__VerticalOccupancyGridList_message_type_support_handle.typesupport_identifier) {
    multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__VerticalOccupancyGridList_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &multi_map_server__msg__VerticalOccupancyGridList__rosidl_typesupport_introspection_c__VerticalOccupancyGridList_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
