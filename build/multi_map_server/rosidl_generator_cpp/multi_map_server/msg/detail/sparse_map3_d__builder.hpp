// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from multi_map_server:msg/SparseMap3D.idl
// generated code does not contain a copyright notice

#ifndef MULTI_MAP_SERVER__MSG__DETAIL__SPARSE_MAP3_D__BUILDER_HPP_
#define MULTI_MAP_SERVER__MSG__DETAIL__SPARSE_MAP3_D__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "multi_map_server/msg/detail/sparse_map3_d__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace multi_map_server
{

namespace msg
{

namespace builder
{

class Init_SparseMap3D_lists
{
public:
  explicit Init_SparseMap3D_lists(::multi_map_server::msg::SparseMap3D & msg)
  : msg_(msg)
  {}
  ::multi_map_server::msg::SparseMap3D lists(::multi_map_server::msg::SparseMap3D::_lists_type arg)
  {
    msg_.lists = std::move(arg);
    return std::move(msg_);
  }

private:
  ::multi_map_server::msg::SparseMap3D msg_;
};

class Init_SparseMap3D_info
{
public:
  explicit Init_SparseMap3D_info(::multi_map_server::msg::SparseMap3D & msg)
  : msg_(msg)
  {}
  Init_SparseMap3D_lists info(::multi_map_server::msg::SparseMap3D::_info_type arg)
  {
    msg_.info = std::move(arg);
    return Init_SparseMap3D_lists(msg_);
  }

private:
  ::multi_map_server::msg::SparseMap3D msg_;
};

class Init_SparseMap3D_header
{
public:
  Init_SparseMap3D_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_SparseMap3D_info header(::multi_map_server::msg::SparseMap3D::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_SparseMap3D_info(msg_);
  }

private:
  ::multi_map_server::msg::SparseMap3D msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::multi_map_server::msg::SparseMap3D>()
{
  return multi_map_server::msg::builder::Init_SparseMap3D_header();
}

}  // namespace multi_map_server

#endif  // MULTI_MAP_SERVER__MSG__DETAIL__SPARSE_MAP3_D__BUILDER_HPP_
