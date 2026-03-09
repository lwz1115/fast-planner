// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from multi_map_server:msg/MultiSparseMap3D.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "multi_map_server/msg/detail/multi_sparse_map3_d__struct.hpp"
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

void MultiSparseMap3D_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) multi_map_server::msg::MultiSparseMap3D(_init);
}

void MultiSparseMap3D_fini_function(void * message_memory)
{
  auto typed_message = static_cast<multi_map_server::msg::MultiSparseMap3D *>(message_memory);
  typed_message->~MultiSparseMap3D();
}

size_t size_function__MultiSparseMap3D__maps(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<multi_map_server::msg::SparseMap3D> *>(untyped_member);
  return member->size();
}

const void * get_const_function__MultiSparseMap3D__maps(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<multi_map_server::msg::SparseMap3D> *>(untyped_member);
  return &member[index];
}

void * get_function__MultiSparseMap3D__maps(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<multi_map_server::msg::SparseMap3D> *>(untyped_member);
  return &member[index];
}

void fetch_function__MultiSparseMap3D__maps(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const multi_map_server::msg::SparseMap3D *>(
    get_const_function__MultiSparseMap3D__maps(untyped_member, index));
  auto & value = *reinterpret_cast<multi_map_server::msg::SparseMap3D *>(untyped_value);
  value = item;
}

void assign_function__MultiSparseMap3D__maps(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<multi_map_server::msg::SparseMap3D *>(
    get_function__MultiSparseMap3D__maps(untyped_member, index));
  const auto & value = *reinterpret_cast<const multi_map_server::msg::SparseMap3D *>(untyped_value);
  item = value;
}

void resize_function__MultiSparseMap3D__maps(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<multi_map_server::msg::SparseMap3D> *>(untyped_member);
  member->resize(size);
}

size_t size_function__MultiSparseMap3D__origins(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<geometry_msgs::msg::Pose> *>(untyped_member);
  return member->size();
}

const void * get_const_function__MultiSparseMap3D__origins(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<geometry_msgs::msg::Pose> *>(untyped_member);
  return &member[index];
}

void * get_function__MultiSparseMap3D__origins(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<geometry_msgs::msg::Pose> *>(untyped_member);
  return &member[index];
}

void fetch_function__MultiSparseMap3D__origins(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const geometry_msgs::msg::Pose *>(
    get_const_function__MultiSparseMap3D__origins(untyped_member, index));
  auto & value = *reinterpret_cast<geometry_msgs::msg::Pose *>(untyped_value);
  value = item;
}

void assign_function__MultiSparseMap3D__origins(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<geometry_msgs::msg::Pose *>(
    get_function__MultiSparseMap3D__origins(untyped_member, index));
  const auto & value = *reinterpret_cast<const geometry_msgs::msg::Pose *>(untyped_value);
  item = value;
}

void resize_function__MultiSparseMap3D__origins(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<geometry_msgs::msg::Pose> *>(untyped_member);
  member->resize(size);
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember MultiSparseMap3D_message_member_array[2] = {
  {
    "maps",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<multi_map_server::msg::SparseMap3D>(),  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(multi_map_server::msg::MultiSparseMap3D, maps),  // bytes offset in struct
    nullptr,  // default value
    size_function__MultiSparseMap3D__maps,  // size() function pointer
    get_const_function__MultiSparseMap3D__maps,  // get_const(index) function pointer
    get_function__MultiSparseMap3D__maps,  // get(index) function pointer
    fetch_function__MultiSparseMap3D__maps,  // fetch(index, &value) function pointer
    assign_function__MultiSparseMap3D__maps,  // assign(index, value) function pointer
    resize_function__MultiSparseMap3D__maps  // resize(index) function pointer
  },
  {
    "origins",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<geometry_msgs::msg::Pose>(),  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(multi_map_server::msg::MultiSparseMap3D, origins),  // bytes offset in struct
    nullptr,  // default value
    size_function__MultiSparseMap3D__origins,  // size() function pointer
    get_const_function__MultiSparseMap3D__origins,  // get_const(index) function pointer
    get_function__MultiSparseMap3D__origins,  // get(index) function pointer
    fetch_function__MultiSparseMap3D__origins,  // fetch(index, &value) function pointer
    assign_function__MultiSparseMap3D__origins,  // assign(index, value) function pointer
    resize_function__MultiSparseMap3D__origins  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers MultiSparseMap3D_message_members = {
  "multi_map_server::msg",  // message namespace
  "MultiSparseMap3D",  // message name
  2,  // number of fields
  sizeof(multi_map_server::msg::MultiSparseMap3D),
  MultiSparseMap3D_message_member_array,  // message members
  MultiSparseMap3D_init_function,  // function to initialize message memory (memory has to be allocated)
  MultiSparseMap3D_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t MultiSparseMap3D_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &MultiSparseMap3D_message_members,
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
get_message_type_support_handle<multi_map_server::msg::MultiSparseMap3D>()
{
  return &::multi_map_server::msg::rosidl_typesupport_introspection_cpp::MultiSparseMap3D_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, multi_map_server, msg, MultiSparseMap3D)() {
  return &::multi_map_server::msg::rosidl_typesupport_introspection_cpp::MultiSparseMap3D_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
