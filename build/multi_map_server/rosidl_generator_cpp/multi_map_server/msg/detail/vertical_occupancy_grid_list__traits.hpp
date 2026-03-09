// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from multi_map_server:msg/VerticalOccupancyGridList.idl
// generated code does not contain a copyright notice

#ifndef MULTI_MAP_SERVER__MSG__DETAIL__VERTICAL_OCCUPANCY_GRID_LIST__TRAITS_HPP_
#define MULTI_MAP_SERVER__MSG__DETAIL__VERTICAL_OCCUPANCY_GRID_LIST__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "multi_map_server/msg/detail/vertical_occupancy_grid_list__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace multi_map_server
{

namespace msg
{

inline void to_flow_style_yaml(
  const VerticalOccupancyGridList & msg,
  std::ostream & out)
{
  out << "{";
  // member: x
  {
    out << "x: ";
    rosidl_generator_traits::value_to_yaml(msg.x, out);
    out << ", ";
  }

  // member: y
  {
    out << "y: ";
    rosidl_generator_traits::value_to_yaml(msg.y, out);
    out << ", ";
  }

  // member: upper
  {
    if (msg.upper.size() == 0) {
      out << "upper: []";
    } else {
      out << "upper: [";
      size_t pending_items = msg.upper.size();
      for (auto item : msg.upper) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: lower
  {
    if (msg.lower.size() == 0) {
      out << "lower: []";
    } else {
      out << "lower: [";
      size_t pending_items = msg.lower.size();
      for (auto item : msg.lower) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: mass
  {
    if (msg.mass.size() == 0) {
      out << "mass: []";
    } else {
      out << "mass: [";
      size_t pending_items = msg.mass.size();
      for (auto item : msg.mass) {
        rosidl_generator_traits::value_to_yaml(item, out);
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
  const VerticalOccupancyGridList & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: x
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "x: ";
    rosidl_generator_traits::value_to_yaml(msg.x, out);
    out << "\n";
  }

  // member: y
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "y: ";
    rosidl_generator_traits::value_to_yaml(msg.y, out);
    out << "\n";
  }

  // member: upper
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.upper.size() == 0) {
      out << "upper: []\n";
    } else {
      out << "upper:\n";
      for (auto item : msg.upper) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: lower
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.lower.size() == 0) {
      out << "lower: []\n";
    } else {
      out << "lower:\n";
      for (auto item : msg.lower) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: mass
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.mass.size() == 0) {
      out << "mass: []\n";
    } else {
      out << "mass:\n";
      for (auto item : msg.mass) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const VerticalOccupancyGridList & msg, bool use_flow_style = false)
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
  const multi_map_server::msg::VerticalOccupancyGridList & msg,
  std::ostream & out, size_t indentation = 0)
{
  multi_map_server::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use multi_map_server::msg::to_yaml() instead")]]
inline std::string to_yaml(const multi_map_server::msg::VerticalOccupancyGridList & msg)
{
  return multi_map_server::msg::to_yaml(msg);
}

template<>
inline const char * data_type<multi_map_server::msg::VerticalOccupancyGridList>()
{
  return "multi_map_server::msg::VerticalOccupancyGridList";
}

template<>
inline const char * name<multi_map_server::msg::VerticalOccupancyGridList>()
{
  return "multi_map_server/msg/VerticalOccupancyGridList";
}

template<>
struct has_fixed_size<multi_map_server::msg::VerticalOccupancyGridList>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<multi_map_server::msg::VerticalOccupancyGridList>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<multi_map_server::msg::VerticalOccupancyGridList>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // MULTI_MAP_SERVER__MSG__DETAIL__VERTICAL_OCCUPANCY_GRID_LIST__TRAITS_HPP_
