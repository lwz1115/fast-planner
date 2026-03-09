// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from multi_map_server:msg/VerticalOccupancyGridList.idl
// generated code does not contain a copyright notice

#ifndef MULTI_MAP_SERVER__MSG__DETAIL__VERTICAL_OCCUPANCY_GRID_LIST__BUILDER_HPP_
#define MULTI_MAP_SERVER__MSG__DETAIL__VERTICAL_OCCUPANCY_GRID_LIST__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "multi_map_server/msg/detail/vertical_occupancy_grid_list__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace multi_map_server
{

namespace msg
{

namespace builder
{

class Init_VerticalOccupancyGridList_mass
{
public:
  explicit Init_VerticalOccupancyGridList_mass(::multi_map_server::msg::VerticalOccupancyGridList & msg)
  : msg_(msg)
  {}
  ::multi_map_server::msg::VerticalOccupancyGridList mass(::multi_map_server::msg::VerticalOccupancyGridList::_mass_type arg)
  {
    msg_.mass = std::move(arg);
    return std::move(msg_);
  }

private:
  ::multi_map_server::msg::VerticalOccupancyGridList msg_;
};

class Init_VerticalOccupancyGridList_lower
{
public:
  explicit Init_VerticalOccupancyGridList_lower(::multi_map_server::msg::VerticalOccupancyGridList & msg)
  : msg_(msg)
  {}
  Init_VerticalOccupancyGridList_mass lower(::multi_map_server::msg::VerticalOccupancyGridList::_lower_type arg)
  {
    msg_.lower = std::move(arg);
    return Init_VerticalOccupancyGridList_mass(msg_);
  }

private:
  ::multi_map_server::msg::VerticalOccupancyGridList msg_;
};

class Init_VerticalOccupancyGridList_upper
{
public:
  explicit Init_VerticalOccupancyGridList_upper(::multi_map_server::msg::VerticalOccupancyGridList & msg)
  : msg_(msg)
  {}
  Init_VerticalOccupancyGridList_lower upper(::multi_map_server::msg::VerticalOccupancyGridList::_upper_type arg)
  {
    msg_.upper = std::move(arg);
    return Init_VerticalOccupancyGridList_lower(msg_);
  }

private:
  ::multi_map_server::msg::VerticalOccupancyGridList msg_;
};

class Init_VerticalOccupancyGridList_y
{
public:
  explicit Init_VerticalOccupancyGridList_y(::multi_map_server::msg::VerticalOccupancyGridList & msg)
  : msg_(msg)
  {}
  Init_VerticalOccupancyGridList_upper y(::multi_map_server::msg::VerticalOccupancyGridList::_y_type arg)
  {
    msg_.y = std::move(arg);
    return Init_VerticalOccupancyGridList_upper(msg_);
  }

private:
  ::multi_map_server::msg::VerticalOccupancyGridList msg_;
};

class Init_VerticalOccupancyGridList_x
{
public:
  Init_VerticalOccupancyGridList_x()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_VerticalOccupancyGridList_y x(::multi_map_server::msg::VerticalOccupancyGridList::_x_type arg)
  {
    msg_.x = std::move(arg);
    return Init_VerticalOccupancyGridList_y(msg_);
  }

private:
  ::multi_map_server::msg::VerticalOccupancyGridList msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::multi_map_server::msg::VerticalOccupancyGridList>()
{
  return multi_map_server::msg::builder::Init_VerticalOccupancyGridList_x();
}

}  // namespace multi_map_server

#endif  // MULTI_MAP_SERVER__MSG__DETAIL__VERTICAL_OCCUPANCY_GRID_LIST__BUILDER_HPP_
