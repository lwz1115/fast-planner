// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from multi_map_server:msg/SparseMap3D.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "multi_map_server/msg/detail/sparse_map3_d__rosidl_typesupport_introspection_c.h"
#include "multi_map_server/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "multi_map_server/msg/detail/sparse_map3_d__functions.h"
#include "multi_map_server/msg/detail/sparse_map3_d__struct.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/header.h"
// Member `header`
#include "std_msgs/msg/detail/header__rosidl_typesupport_introspection_c.h"
// Member `info`
#include "nav_msgs/msg/map_meta_data.h"
// Member `info`
#include "nav_msgs/msg/detail/map_meta_data__rosidl_typesupport_introspection_c.h"
// Member `lists`
#include "multi_map_server/msg/vertical_occupancy_grid_list.h"
// Member `lists`
#include "multi_map_server/msg/detail/vertical_occupancy_grid_list__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void multi_map_server__msg__SparseMap3D__rosidl_typesupport_introspection_c__SparseMap3D_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  multi_map_server__msg__SparseMap3D__init(message_memory);
}

void multi_map_server__msg__SparseMap3D__rosidl_typesupport_introspection_c__SparseMap3D_fini_function(void * message_memory)
{
  multi_map_server__msg__SparseMap3D__fini(message_memory);
}

size_t multi_map_server__msg__SparseMap3D__rosidl_typesupport_introspection_c__size_function__SparseMap3D__lists(
  const void * untyped_member)
{
  const multi_map_server__msg__VerticalOccupancyGridList__Sequence * member =
    (const multi_map_server__msg__VerticalOccupancyGridList__Sequence *)(untyped_member);
  return member->size;
}

const void * multi_map_server__msg__SparseMap3D__rosidl_typesupport_introspection_c__get_const_function__SparseMap3D__lists(
  const void * untyped_member, size_t index)
{
  const multi_map_server__msg__VerticalOccupancyGridList__Sequence * member =
    (const multi_map_server__msg__VerticalOccupancyGridList__Sequence *)(untyped_member);
  return &member->data[index];
}

void * multi_map_server__msg__SparseMap3D__rosidl_typesupport_introspection_c__get_function__SparseMap3D__lists(
  void * untyped_member, size_t index)
{
  multi_map_server__msg__VerticalOccupancyGridList__Sequence * member =
    (multi_map_server__msg__VerticalOccupancyGridList__Sequence *)(untyped_member);
  return &member->data[index];
}

void multi_map_server__msg__SparseMap3D__rosidl_typesupport_introspection_c__fetch_function__SparseMap3D__lists(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const multi_map_server__msg__VerticalOccupancyGridList * item =
    ((const multi_map_server__msg__VerticalOccupancyGridList *)
    multi_map_server__msg__SparseMap3D__rosidl_typesupport_introspection_c__get_const_function__SparseMap3D__lists(untyped_member, index));
  multi_map_server__msg__VerticalOccupancyGridList * value =
    (multi_map_server__msg__VerticalOccupancyGridList *)(untyped_value);
  *value = *item;
}

void multi_map_server__msg__SparseMap3D__rosidl_typesupport_introspection_c__assign_function__SparseMap3D__lists(
  void * untyped_member, size_t index, const void * untyped_value)
{
  multi_map_server__msg__VerticalOccupancyGridList * item =
    ((multi_map_server__msg__VerticalOccupancyGridList *)
    multi_map_server__msg__SparseMap3D__rosidl_typesupport_introspection_c__get_function__SparseMap3D__lists(untyped_member, index));
  const multi_map_server__msg__VerticalOccupancyGridList * value =
    (const multi_map_server__msg__VerticalOccupancyGridList *)(untyped_value);
  *item = *value;
}

bool multi_map_server__msg__SparseMap3D__rosidl_typesupport_introspection_c__resize_function__SparseMap3D__lists(
  void * untyped_member, size_t size)
{
  multi_map_server__msg__VerticalOccupancyGridList__Sequence * member =
    (multi_map_server__msg__VerticalOccupancyGridList__Sequence *)(untyped_member);
  multi_map_server__msg__VerticalOccupancyGridList__Sequence__fini(member);
  return multi_map_server__msg__VerticalOccupancyGridList__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember multi_map_server__msg__SparseMap3D__rosidl_typesupport_introspection_c__SparseMap3D_message_member_array[3] = {
  {
    "header",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(multi_map_server__msg__SparseMap3D, header),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "info",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(multi_map_server__msg__SparseMap3D, info),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "lists",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(multi_map_server__msg__SparseMap3D, lists),  // bytes offset in struct
    NULL,  // default value
    multi_map_server__msg__SparseMap3D__rosidl_typesupport_introspection_c__size_function__SparseMap3D__lists,  // size() function pointer
    multi_map_server__msg__SparseMap3D__rosidl_typesupport_introspection_c__get_const_function__SparseMap3D__lists,  // get_const(index) function pointer
    multi_map_server__msg__SparseMap3D__rosidl_typesupport_introspection_c__get_function__SparseMap3D__lists,  // get(index) function pointer
    multi_map_server__msg__SparseMap3D__rosidl_typesupport_introspection_c__fetch_function__SparseMap3D__lists,  // fetch(index, &value) function pointer
    multi_map_server__msg__SparseMap3D__rosidl_typesupport_introspection_c__assign_function__SparseMap3D__lists,  // assign(index, value) function pointer
    multi_map_server__msg__SparseMap3D__rosidl_typesupport_introspection_c__resize_function__SparseMap3D__lists  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers multi_map_server__msg__SparseMap3D__rosidl_typesupport_introspection_c__SparseMap3D_message_members = {
  "multi_map_server__msg",  // message namespace
  "SparseMap3D",  // message name
  3,  // number of fields
  sizeof(multi_map_server__msg__SparseMap3D),
  multi_map_server__msg__SparseMap3D__rosidl_typesupport_introspection_c__SparseMap3D_message_member_array,  // message members
  multi_map_server__msg__SparseMap3D__rosidl_typesupport_introspection_c__SparseMap3D_init_function,  // function to initialize message memory (memory has to be allocated)
  multi_map_server__msg__SparseMap3D__rosidl_typesupport_introspection_c__SparseMap3D_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t multi_map_server__msg__SparseMap3D__rosidl_typesupport_introspection_c__SparseMap3D_message_type_support_handle = {
  0,
  &multi_map_server__msg__SparseMap3D__rosidl_typesupport_introspection_c__SparseMap3D_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_multi_map_server
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, multi_map_server, msg, SparseMap3D)() {
  multi_map_server__msg__SparseMap3D__rosidl_typesupport_introspection_c__SparseMap3D_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, std_msgs, msg, Header)();
  multi_map_server__msg__SparseMap3D__rosidl_typesupport_introspection_c__SparseMap3D_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, nav_msgs, msg, MapMetaData)();
  multi_map_server__msg__SparseMap3D__rosidl_typesupport_introspection_c__SparseMap3D_message_member_array[2].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, multi_map_server, msg, VerticalOccupancyGridList)();
  if (!multi_map_server__msg__SparseMap3D__rosidl_typesupport_introspection_c__SparseMap3D_message_type_support_handle.typesupport_identifier) {
    multi_map_server__msg__SparseMap3D__rosidl_typesupport_introspection_c__SparseMap3D_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &multi_map_server__msg__SparseMap3D__rosidl_typesupport_introspection_c__SparseMap3D_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
