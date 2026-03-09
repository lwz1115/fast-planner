// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from multi_map_server:msg/MultiSparseMap3D.idl
// generated code does not contain a copyright notice

#ifndef MULTI_MAP_SERVER__MSG__DETAIL__MULTI_SPARSE_MAP3_D__BUILDER_HPP_
#define MULTI_MAP_SERVER__MSG__DETAIL__MULTI_SPARSE_MAP3_D__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "multi_map_server/msg/detail/multi_sparse_map3_d__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace multi_map_server
{

namespace msg
{

namespace builder
{

class Init_MultiSparseMap3D_origins
{
public:
  explicit Init_MultiSparseMap3D_origins(::multi_map_server::msg::MultiSparseMap3D & msg)
  : msg_(msg)
  {}
  ::multi_map_server::msg::MultiSparseMap3D origins(::multi_map_server::msg::MultiSparseMap3D::_origins_type arg)
  {
    msg_.origins = std::move(arg);
    return std::move(msg_);
  }

private:
  ::multi_map_server::msg::MultiSparseMap3D msg_;
};

class Init_MultiSparseMap3D_maps
{
public:
  Init_MultiSparseMap3D_maps()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_MultiSparseMap3D_origins maps(::multi_map_server::msg::MultiSparseMap3D::_maps_type arg)
  {
    msg_.maps = std::move(arg);
    return Init_MultiSparseMap3D_origins(msg_);
  }

private:
  ::multi_map_server::msg::MultiSparseMap3D msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::multi_map_server::msg::MultiSparseMap3D>()
{
  return multi_map_server::msg::builder::Init_MultiSparseMap3D_maps();
}

}  // namespace multi_map_server

#endif  // MULTI_MAP_SERVER__MSG__DETAIL__MULTI_SPARSE_MAP3_D__BUILDER_HPP_
