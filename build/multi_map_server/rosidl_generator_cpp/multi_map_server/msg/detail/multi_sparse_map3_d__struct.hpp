// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from multi_map_server:msg/MultiSparseMap3D.idl
// generated code does not contain a copyright notice

#ifndef MULTI_MAP_SERVER__MSG__DETAIL__MULTI_SPARSE_MAP3_D__STRUCT_HPP_
#define MULTI_MAP_SERVER__MSG__DETAIL__MULTI_SPARSE_MAP3_D__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'maps'
#include "multi_map_server/msg/detail/sparse_map3_d__struct.hpp"
// Member 'origins'
#include "geometry_msgs/msg/detail/pose__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__multi_map_server__msg__MultiSparseMap3D __attribute__((deprecated))
#else
# define DEPRECATED__multi_map_server__msg__MultiSparseMap3D __declspec(deprecated)
#endif

namespace multi_map_server
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct MultiSparseMap3D_
{
  using Type = MultiSparseMap3D_<ContainerAllocator>;

  explicit MultiSparseMap3D_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_init;
  }

  explicit MultiSparseMap3D_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_init;
    (void)_alloc;
  }

  // field types and members
  using _maps_type =
    std::vector<multi_map_server::msg::SparseMap3D_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<multi_map_server::msg::SparseMap3D_<ContainerAllocator>>>;
  _maps_type maps;
  using _origins_type =
    std::vector<geometry_msgs::msg::Pose_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<geometry_msgs::msg::Pose_<ContainerAllocator>>>;
  _origins_type origins;

  // setters for named parameter idiom
  Type & set__maps(
    const std::vector<multi_map_server::msg::SparseMap3D_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<multi_map_server::msg::SparseMap3D_<ContainerAllocator>>> & _arg)
  {
    this->maps = _arg;
    return *this;
  }
  Type & set__origins(
    const std::vector<geometry_msgs::msg::Pose_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<geometry_msgs::msg::Pose_<ContainerAllocator>>> & _arg)
  {
    this->origins = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    multi_map_server::msg::MultiSparseMap3D_<ContainerAllocator> *;
  using ConstRawPtr =
    const multi_map_server::msg::MultiSparseMap3D_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<multi_map_server::msg::MultiSparseMap3D_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<multi_map_server::msg::MultiSparseMap3D_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      multi_map_server::msg::MultiSparseMap3D_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<multi_map_server::msg::MultiSparseMap3D_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      multi_map_server::msg::MultiSparseMap3D_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<multi_map_server::msg::MultiSparseMap3D_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<multi_map_server::msg::MultiSparseMap3D_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<multi_map_server::msg::MultiSparseMap3D_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__multi_map_server__msg__MultiSparseMap3D
    std::shared_ptr<multi_map_server::msg::MultiSparseMap3D_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__multi_map_server__msg__MultiSparseMap3D
    std::shared_ptr<multi_map_server::msg::MultiSparseMap3D_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const MultiSparseMap3D_ & other) const
  {
    if (this->maps != other.maps) {
      return false;
    }
    if (this->origins != other.origins) {
      return false;
    }
    return true;
  }
  bool operator!=(const MultiSparseMap3D_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct MultiSparseMap3D_

// alias to use template instance with default allocator
using MultiSparseMap3D =
  multi_map_server::msg::MultiSparseMap3D_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace multi_map_server

#endif  // MULTI_MAP_SERVER__MSG__DETAIL__MULTI_SPARSE_MAP3_D__STRUCT_HPP_
