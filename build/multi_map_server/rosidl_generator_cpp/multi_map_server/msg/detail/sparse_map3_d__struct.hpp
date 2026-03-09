// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from multi_map_server:msg/SparseMap3D.idl
// generated code does not contain a copyright notice

#ifndef MULTI_MAP_SERVER__MSG__DETAIL__SPARSE_MAP3_D__STRUCT_HPP_
#define MULTI_MAP_SERVER__MSG__DETAIL__SPARSE_MAP3_D__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.hpp"
// Member 'info'
#include "nav_msgs/msg/detail/map_meta_data__struct.hpp"
// Member 'lists'
#include "multi_map_server/msg/detail/vertical_occupancy_grid_list__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__multi_map_server__msg__SparseMap3D __attribute__((deprecated))
#else
# define DEPRECATED__multi_map_server__msg__SparseMap3D __declspec(deprecated)
#endif

namespace multi_map_server
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct SparseMap3D_
{
  using Type = SparseMap3D_<ContainerAllocator>;

  explicit SparseMap3D_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init),
    info(_init)
  {
    (void)_init;
  }

  explicit SparseMap3D_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init),
    info(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _info_type =
    nav_msgs::msg::MapMetaData_<ContainerAllocator>;
  _info_type info;
  using _lists_type =
    std::vector<multi_map_server::msg::VerticalOccupancyGridList_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<multi_map_server::msg::VerticalOccupancyGridList_<ContainerAllocator>>>;
  _lists_type lists;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__info(
    const nav_msgs::msg::MapMetaData_<ContainerAllocator> & _arg)
  {
    this->info = _arg;
    return *this;
  }
  Type & set__lists(
    const std::vector<multi_map_server::msg::VerticalOccupancyGridList_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<multi_map_server::msg::VerticalOccupancyGridList_<ContainerAllocator>>> & _arg)
  {
    this->lists = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    multi_map_server::msg::SparseMap3D_<ContainerAllocator> *;
  using ConstRawPtr =
    const multi_map_server::msg::SparseMap3D_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<multi_map_server::msg::SparseMap3D_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<multi_map_server::msg::SparseMap3D_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      multi_map_server::msg::SparseMap3D_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<multi_map_server::msg::SparseMap3D_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      multi_map_server::msg::SparseMap3D_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<multi_map_server::msg::SparseMap3D_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<multi_map_server::msg::SparseMap3D_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<multi_map_server::msg::SparseMap3D_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__multi_map_server__msg__SparseMap3D
    std::shared_ptr<multi_map_server::msg::SparseMap3D_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__multi_map_server__msg__SparseMap3D
    std::shared_ptr<multi_map_server::msg::SparseMap3D_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const SparseMap3D_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->info != other.info) {
      return false;
    }
    if (this->lists != other.lists) {
      return false;
    }
    return true;
  }
  bool operator!=(const SparseMap3D_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct SparseMap3D_

// alias to use template instance with default allocator
using SparseMap3D =
  multi_map_server::msg::SparseMap3D_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace multi_map_server

#endif  // MULTI_MAP_SERVER__MSG__DETAIL__SPARSE_MAP3_D__STRUCT_HPP_
