// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from multi_map_server:msg/MultiSparseMap3D.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "multi_map_server/msg/detail/multi_sparse_map3_d__rosidl_typesupport_introspection_c.h"
#include "multi_map_server/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "multi_map_server/msg/detail/multi_sparse_map3_d__functions.h"
#include "multi_map_server/msg/detail/multi_sparse_map3_d__struct.h"


// Include directives for member types
// Member `maps`
#include "multi_map_server/msg/sparse_map3_d.h"
// Member `maps`
#include "multi_map_server/msg/detail/sparse_map3_d__rosidl_typesupport_introspection_c.h"
// Member `origins`
#include "geometry_msgs/msg/pose.h"
// Member `origins`
#include "geometry_msgs/msg/detail/pose__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__MultiSparseMap3D_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  multi_map_server__msg__MultiSparseMap3D__init(message_memory);
}

void multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__MultiSparseMap3D_fini_function(void * message_memory)
{
  multi_map_server__msg__MultiSparseMap3D__fini(message_memory);
}

size_t multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__size_function__MultiSparseMap3D__maps(
  const void * untyped_member)
{
  const multi_map_server__msg__SparseMap3D__Sequence * member =
    (const multi_map_server__msg__SparseMap3D__Sequence *)(untyped_member);
  return member->size;
}

const void * multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__get_const_function__MultiSparseMap3D__maps(
  const void * untyped_member, size_t index)
{
  const multi_map_server__msg__SparseMap3D__Sequence * member =
    (const multi_map_server__msg__SparseMap3D__Sequence *)(untyped_member);
  return &member->data[index];
}

void * multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__get_function__MultiSparseMap3D__maps(
  void * untyped_member, size_t index)
{
  multi_map_server__msg__SparseMap3D__Sequence * member =
    (multi_map_server__msg__SparseMap3D__Sequence *)(untyped_member);
  return &member->data[index];
}

void multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__fetch_function__MultiSparseMap3D__maps(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const multi_map_server__msg__SparseMap3D * item =
    ((const multi_map_server__msg__SparseMap3D *)
    multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__get_const_function__MultiSparseMap3D__maps(untyped_member, index));
  multi_map_server__msg__SparseMap3D * value =
    (multi_map_server__msg__SparseMap3D *)(untyped_value);
  *value = *item;
}

void multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__assign_function__MultiSparseMap3D__maps(
  void * untyped_member, size_t index, const void * untyped_value)
{
  multi_map_server__msg__SparseMap3D * item =
    ((multi_map_server__msg__SparseMap3D *)
    multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__get_function__MultiSparseMap3D__maps(untyped_member, index));
  const multi_map_server__msg__SparseMap3D * value =
    (const multi_map_server__msg__SparseMap3D *)(untyped_value);
  *item = *value;
}

bool multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__resize_function__MultiSparseMap3D__maps(
  void * untyped_member, size_t size)
{
  multi_map_server__msg__SparseMap3D__Sequence * member =
    (multi_map_server__msg__SparseMap3D__Sequence *)(untyped_member);
  multi_map_server__msg__SparseMap3D__Sequence__fini(member);
  return multi_map_server__msg__SparseMap3D__Sequence__init(member, size);
}

size_t multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__size_function__MultiSparseMap3D__origins(
  const void * untyped_member)
{
  const geometry_msgs__msg__Pose__Sequence * member =
    (const geometry_msgs__msg__Pose__Sequence *)(untyped_member);
  return member->size;
}

const void * multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__get_const_function__MultiSparseMap3D__origins(
  const void * untyped_member, size_t index)
{
  const geometry_msgs__msg__Pose__Sequence * member =
    (const geometry_msgs__msg__Pose__Sequence *)(untyped_member);
  return &member->data[index];
}

void * multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__get_function__MultiSparseMap3D__origins(
  void * untyped_member, size_t index)
{
  geometry_msgs__msg__Pose__Sequence * member =
    (geometry_msgs__msg__Pose__Sequence *)(untyped_member);
  return &member->data[index];
}

void multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__fetch_function__MultiSparseMap3D__origins(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const geometry_msgs__msg__Pose * item =
    ((const geometry_msgs__msg__Pose *)
    multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__get_const_function__MultiSparseMap3D__origins(untyped_member, index));
  geometry_msgs__msg__Pose * value =
    (geometry_msgs__msg__Pose *)(untyped_value);
  *value = *item;
}

void multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__assign_function__MultiSparseMap3D__origins(
  void * untyped_member, size_t index, const void * untyped_value)
{
  geometry_msgs__msg__Pose * item =
    ((geometry_msgs__msg__Pose *)
    multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__get_function__MultiSparseMap3D__origins(untyped_member, index));
  const geometry_msgs__msg__Pose * value =
    (const geometry_msgs__msg__Pose *)(untyped_value);
  *item = *value;
}

bool multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__resize_function__MultiSparseMap3D__origins(
  void * untyped_member, size_t size)
{
  geometry_msgs__msg__Pose__Sequence * member =
    (geometry_msgs__msg__Pose__Sequence *)(untyped_member);
  geometry_msgs__msg__Pose__Sequence__fini(member);
  return geometry_msgs__msg__Pose__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__MultiSparseMap3D_message_member_array[2] = {
  {
    "maps",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(multi_map_server__msg__MultiSparseMap3D, maps),  // bytes offset in struct
    NULL,  // default value
    multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__size_function__MultiSparseMap3D__maps,  // size() function pointer
    multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__get_const_function__MultiSparseMap3D__maps,  // get_const(index) function pointer
    multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__get_function__MultiSparseMap3D__maps,  // get(index) function pointer
    multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__fetch_function__MultiSparseMap3D__maps,  // fetch(index, &value) function pointer
    multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__assign_function__MultiSparseMap3D__maps,  // assign(index, value) function pointer
    multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__resize_function__MultiSparseMap3D__maps  // resize(index) function pointer
  },
  {
    "origins",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(multi_map_server__msg__MultiSparseMap3D, origins),  // bytes offset in struct
    NULL,  // default value
    multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__size_function__MultiSparseMap3D__origins,  // size() function pointer
    multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__get_const_function__MultiSparseMap3D__origins,  // get_const(index) function pointer
    multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__get_function__MultiSparseMap3D__origins,  // get(index) function pointer
    multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__fetch_function__MultiSparseMap3D__origins,  // fetch(index, &value) function pointer
    multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__assign_function__MultiSparseMap3D__origins,  // assign(index, value) function pointer
    multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__resize_function__MultiSparseMap3D__origins  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__MultiSparseMap3D_message_members = {
  "multi_map_server__msg",  // message namespace
  "MultiSparseMap3D",  // message name
  2,  // number of fields
  sizeof(multi_map_server__msg__MultiSparseMap3D),
  multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__MultiSparseMap3D_message_member_array,  // message members
  multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__MultiSparseMap3D_init_function,  // function to initialize message memory (memory has to be allocated)
  multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__MultiSparseMap3D_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__MultiSparseMap3D_message_type_support_handle = {
  0,
  &multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__MultiSparseMap3D_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_multi_map_server
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, multi_map_server, msg, MultiSparseMap3D)() {
  multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__MultiSparseMap3D_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, multi_map_server, msg, SparseMap3D)();
  multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__MultiSparseMap3D_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, geometry_msgs, msg, Pose)();
  if (!multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__MultiSparseMap3D_message_type_support_handle.typesupport_identifier) {
    multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__MultiSparseMap3D_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &multi_map_server__msg__MultiSparseMap3D__rosidl_typesupport_introspection_c__MultiSparseMap3D_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
