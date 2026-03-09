// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from multi_map_server:msg/VerticalOccupancyGridList.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "multi_map_server/msg/detail/vertical_occupancy_grid_list__struct.hpp"
#include "rosidl_typesupport_introspection_cpp/field_types.hpp"
#include "rosidl_typesupport_introspection_cpp/identifier.hpp"
#include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
#include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace multi_map_server
{

namespace msg
{

namespace rosidl_typesupport_introspection_cpp
{

void VerticalOccupancyGridList_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) multi_map_server::msg::VerticalOccupancyGridList(_init);
}

void VerticalOccupancyGridList_fini_function(void * message_memory)
{
  auto typed_message = static_cast<multi_map_server::msg::VerticalOccupancyGridList *>(message_memory);
  typed_message->~VerticalOccupancyGridList();
}

size_t size_function__VerticalOccupancyGridList__upper(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<int32_t> *>(untyped_member);
  return member->size();
}

const void * get_const_function__VerticalOccupancyGridList__upper(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<int32_t> *>(untyped_member);
  return &member[index];
}

void * get_function__VerticalOccupancyGridList__upper(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<int32_t> *>(untyped_member);
  return &member[index];
}

void fetch_function__VerticalOccupancyGridList__upper(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const int32_t *>(
    get_const_function__VerticalOccupancyGridList__upper(untyped_member, index));
  auto & value = *reinterpret_cast<int32_t *>(untyped_value);
  value = item;
}

void assign_function__VerticalOccupancyGridList__upper(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<int32_t *>(
    get_function__VerticalOccupancyGridList__upper(untyped_member, index));
  const auto & value = *reinterpret_cast<const int32_t *>(untyped_value);
  item = value;
}

void resize_function__VerticalOccupancyGridList__upper(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<int32_t> *>(untyped_member);
  member->resize(size);
}

size_t size_function__VerticalOccupancyGridList__lower(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<int32_t> *>(untyped_member);
  return member->size();
}

const void * get_const_function__VerticalOccupancyGridList__lower(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<int32_t> *>(untyped_member);
  return &member[index];
}

void * get_function__VerticalOccupancyGridList__lower(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<int32_t> *>(untyped_member);
  return &member[index];
}

void fetch_function__VerticalOccupancyGridList__lower(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const int32_t *>(
    get_const_function__VerticalOccupancyGridList__lower(untyped_member, index));
  auto & value = *reinterpret_cast<int32_t *>(untyped_value);
  value = item;
}

void assign_function__VerticalOccupancyGridList__lower(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<int32_t *>(
    get_function__VerticalOccupancyGridList__lower(untyped_member, index));
  const auto & value = *reinterpret_cast<const int32_t *>(untyped_value);
  item = value;
}

void resize_function__VerticalOccupancyGridList__lower(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<int32_t> *>(untyped_member);
  member->resize(size);
}

size_t size_function__VerticalOccupancyGridList__mass(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<int32_t> *>(untyped_member);
  return member->size();
}

const void * get_const_function__VerticalOccupancyGridList__mass(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<int32_t> *>(untyped_member);
  return &member[index];
}

void * get_function__VerticalOccupancyGridList__mass(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<int32_t> *>(untyped_member);
  return &member[index];
}

void fetch_function__VerticalOccupancyGridList__mass(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const int32_t *>(
    get_const_function__VerticalOccupancyGridList__mass(untyped_member, index));
  auto & value = *reinterpret_cast<int32_t *>(untyped_value);
  value = item;
}

void assign_function__VerticalOccupancyGridList__mass(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<int32_t *>(
    get_function__VerticalOccupancyGridList__mass(untyped_member, index));
  const auto & value = *reinterpret_cast<const int32_t *>(untyped_value);
  item = value;
}

void resize_function__VerticalOccupancyGridList__mass(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<int32_t> *>(untyped_member);
  member->resize(size);
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember VerticalOccupancyGridList_message_member_array[5] = {
  {
    "x",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(multi_map_server::msg::VerticalOccupancyGridList, x),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "y",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(multi_map_server::msg::VerticalOccupancyGridList, y),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "upper",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_INT32,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(multi_map_server::msg::VerticalOccupancyGridList, upper),  // bytes offset in struct
    nullptr,  // default value
    size_function__VerticalOccupancyGridList__upper,  // size() function pointer
    get_const_function__VerticalOccupancyGridList__upper,  // get_const(index) function pointer
    get_function__VerticalOccupancyGridList__upper,  // get(index) function pointer
    fetch_function__VerticalOccupancyGridList__upper,  // fetch(index, &value) function pointer
    assign_function__VerticalOccupancyGridList__upper,  // assign(index, value) function pointer
    resize_function__VerticalOccupancyGridList__upper  // resize(index) function pointer
  },
  {
    "lower",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_INT32,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(multi_map_server::msg::VerticalOccupancyGridList, lower),  // bytes offset in struct
    nullptr,  // default value
    size_function__VerticalOccupancyGridList__lower,  // size() function pointer
    get_const_function__VerticalOccupancyGridList__lower,  // get_const(index) function pointer
    get_function__VerticalOccupancyGridList__lower,  // get(index) function pointer
    fetch_function__VerticalOccupancyGridList__lower,  // fetch(index, &value) function pointer
    assign_function__VerticalOccupancyGridList__lower,  // assign(index, value) function pointer
    resize_function__VerticalOccupancyGridList__lower  // resize(index) function pointer
  },
  {
    "mass",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_INT32,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(multi_map_server::msg::VerticalOccupancyGridList, mass),  // bytes offset in struct
    nullptr,  // default value
    size_function__VerticalOccupancyGridList__mass,  // size() function pointer
    get_const_function__VerticalOccupancyGridList__mass,  // get_const(index) function pointer
    get_function__VerticalOccupancyGridList__mass,  // get(index) function pointer
    fetch_function__VerticalOccupancyGridList__mass,  // fetch(index, &value) function pointer
    assign_function__VerticalOccupancyGridList__mass,  // assign(index, value) function pointer
    resize_function__VerticalOccupancyGridList__mass  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers VerticalOccupancyGridList_message_members = {
  "multi_map_server::msg",  // message namespace
  "VerticalOccupancyGridList",  // message name
  5,  // number of fields
  sizeof(multi_map_server::msg::VerticalOccupancyGridList),
  VerticalOccupancyGridList_message_member_array,  // message members
  VerticalOccupancyGridList_init_function,  // function to initialize message memory (memory has to be allocated)
  VerticalOccupancyGridList_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t VerticalOccupancyGridList_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &VerticalOccupancyGridList_message_members,
  get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace msg

}  // namespace multi_map_server


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<multi_map_server::msg::VerticalOccupancyGridList>()
{
  return &::multi_map_server::msg::rosidl_typesupport_introspection_cpp::VerticalOccupancyGridList_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, multi_map_server, msg, VerticalOccupancyGridList)() {
  return &::multi_map_server::msg::rosidl_typesupport_introspection_cpp::VerticalOccupancyGridList_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
