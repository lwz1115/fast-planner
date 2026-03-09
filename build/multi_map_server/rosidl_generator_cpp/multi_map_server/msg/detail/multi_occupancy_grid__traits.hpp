// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from multi_map_server:msg/MultiOccupancyGrid.idl
// generated code does not contain a copyright notice

#ifndef MULTI_MAP_SERVER__MSG__DETAIL__MULTI_OCCUPANCY_GRID__TRAITS_HPP_
#define MULTI_MAP_SERVER__MSG__DETAIL__MULTI_OCCUPANCY_GRID__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "multi_map_server/msg/detail/multi_occupancy_grid__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'maps'
#include "nav_msgs/msg/detail/occupancy_grid__traits.hpp"
// Member 'origins'
#include "geometry_msgs/msg/detail/pose__traits.hpp"

namespace multi_map_server
{

namespace msg
{

inline void to_flow_style_yaml(
  const MultiOccupancyGrid & msg,
  std::ostream & out)
{
  out << "{";
  // member: maps
  {
    if (msg.maps.size() == 0) {
      out << "maps: []";
    } else {
      out << "maps: [";
      size_t pending_items = msg.maps.size();
      for (auto item : msg.maps) {
        to_flow_style_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: origins
  {
    if (msg.origins.size() == 0) {
      out << "origins: []";
    } else {
      out << "origins: [";
      size_t pending_items = msg.origins.size();
      for (auto item : msg.origins) {
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
  const MultiOccupancyGrid & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: maps
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.maps.size() == 0) {
      out << "maps: []\n";
    } else {
      out << "maps:\n";
      for (auto item : msg.maps) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "-\n";
        to_block_style_yaml(item, out, indentation + 2);
      }
    }
  }

  // member: origins
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.origins.size() == 0) {
      out << "origins: []\n";
    } else {
      out << "origins:\n";
      for (auto item : msg.origins) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "-\n";
        to_block_style_yaml(item, out, indentation + 2);
      }
    }
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const MultiOccupancyGrid & msg, bool use_flow_style = false)
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
  const multi_map_server::msg::MultiOccupancyGrid & msg,
  std::ostream & out, size_t indentation = 0)
{
  multi_map_server::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use multi_map_server::msg::to_yaml() instead")]]
inline std::string to_yaml(const multi_map_server::msg::MultiOccupancyGrid & msg)
{
  return multi_map_server::msg::to_yaml(msg);
}

template<>
inline const char * data_type<multi_map_server::msg::MultiOccupancyGrid>()
{
  return "multi_map_server::msg::MultiOccupancyGrid";
}

template<>
inline const char * name<multi_map_server::msg::MultiOccupancyGrid>()
{
  return "multi_map_server/msg/MultiOccupancyGrid";
}

template<>
struct has_fixed_size<multi_map_server::msg::MultiOccupancyGrid>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<multi_map_server::msg::MultiOccupancyGrid>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<multi_map_server::msg::MultiOccupancyGrid>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // MULTI_MAP_SERVER__MSG__DETAIL__MULTI_OCCUPANCY_GRID__TRAITS_HPP_
