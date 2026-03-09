// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from multi_map_server:msg/SparseMap3D.idl
// generated code does not contain a copyright notice

#ifndef MULTI_MAP_SERVER__MSG__DETAIL__SPARSE_MAP3_D__TRAITS_HPP_
#define MULTI_MAP_SERVER__MSG__DETAIL__SPARSE_MAP3_D__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "multi_map_server/msg/detail/sparse_map3_d__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"
// Member 'info'
#include "nav_msgs/msg/detail/map_meta_data__traits.hpp"
// Member 'lists'
#include "multi_map_server/msg/detail/vertical_occupancy_grid_list__traits.hpp"

namespace multi_map_server
{

namespace msg
{

inline void to_flow_style_yaml(
  const SparseMap3D & msg,
  std::ostream & out)
{
  out << "{";
  // member: header
  {
    out << "header: ";
    to_flow_style_yaml(msg.header, out);
    out << ", ";
  }

  // member: info
  {
    out << "info: ";
    to_flow_style_yaml(msg.info, out);
    out << ", ";
  }

  // member: lists
  {
    if (msg.lists.size() == 0) {
      out << "lists: []";
    } else {
      out << "lists: [";
      size_t pending_items = msg.lists.size();
      for (auto item : msg.lists) {
        to_flow_style_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const SparseMap3D & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: header
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "header:\n";
    to_block_style_yaml(msg.header, out, indentation + 2);
  }

  // member: info
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "info:\n";
    to_block_style_yaml(msg.info, out, indentation + 2);
  }

  // member: lists
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.lists.size() == 0) {
      out << "lists: []\n";
    } else {
      out << "lists:\n";
      for (auto item : msg.lists) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "-\n";
        to_block_style_yaml(item, out, indentation + 2);
      }
    }
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const SparseMap3D & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace multi_map_server

namespace rosidl_generator_traits
{

[[deprecated("use multi_map_server::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const multi_map_server::msg::SparseMap3D & msg,
  std::ostream & out, size_t indentation = 0)
{
  multi_map_server::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use multi_map_server::msg::to_yaml() instead")]]
inline std::string to_yaml(const multi_map_server::msg::SparseMap3D & msg)
{
  return multi_map_server::msg::to_yaml(msg);
}

template<>
inline const char * data_type<multi_map_server::msg::SparseMap3D>()
{
  return "multi_map_server::msg::SparseMap3D";
}

template<>
inline const char * name<multi_map_server::msg::SparseMap3D>()
{
  return "multi_map_server/msg/SparseMap3D";
}

template<>
struct has_fixed_size<multi_map_server::msg::SparseMap3D>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<multi_map_server::msg::SparseMap3D>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<multi_map_server::msg::SparseMap3D>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // MULTI_MAP_SERVER__MSG__DETAIL__SPARSE_MAP3_D__TRAITS_HPP_
