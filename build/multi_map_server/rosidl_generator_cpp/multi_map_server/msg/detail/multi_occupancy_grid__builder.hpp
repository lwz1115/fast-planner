// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from multi_map_server:msg/MultiOccupancyGrid.idl
// generated code does not contain a copyright notice

#ifndef MULTI_MAP_SERVER__MSG__DETAIL__MULTI_OCCUPANCY_GRID__BUILDER_HPP_
#define MULTI_MAP_SERVER__MSG__DETAIL__MULTI_OCCUPANCY_GRID__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "multi_map_server/msg/detail/multi_occupancy_grid__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace multi_map_server
{

namespace msg
{

namespace builder
{

class Init_MultiOccupancyGrid_origins
{
public:
  explicit Init_MultiOccupancyGrid_origins(::multi_map_server::msg::MultiOccupancyGrid & msg)
  : msg_(msg)
  {}
  ::multi_map_server::msg::MultiOccupancyGrid origins(::multi_map_server::msg::MultiOccupancyGrid::_origins_type arg)
  {
    msg_.origins = std::move(arg);
    return std::move(msg_);
  }

private:
  ::multi_map_server::msg::MultiOccupancyGrid msg_;
};

class Init_MultiOccupancyGrid_maps
{
public:
  Init_MultiOccupancyGrid_maps()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_MultiOccupancyGrid_origins maps(::multi_map_server::msg::MultiOccupancyGrid::_maps_type arg)
  {
    msg_.maps = std::move(arg);
    return Init_MultiOccupancyGrid_origins(msg_);
  }

private:
  ::multi_map_server::msg::MultiOccupancyGrid msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::multi_map_server::msg::MultiOccupancyGrid>()
{
  return multi_map_server::msg::builder::Init_MultiOccupancyGrid_maps();
}

}  // namespace multi_map_server

#endif  // MULTI_MAP_SERVER__MSG__DETAIL__MULTI_OCCUPANCY_GRID__BUILDER_HPP_
