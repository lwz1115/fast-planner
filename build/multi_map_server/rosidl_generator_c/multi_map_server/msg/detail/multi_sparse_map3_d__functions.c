// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from multi_map_server:msg/MultiSparseMap3D.idl
// generated code does not contain a copyright notice
#include "multi_map_server/msg/detail/multi_sparse_map3_d__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `maps`
#include "multi_map_server/msg/detail/sparse_map3_d__functions.h"
// Member `origins`
#include "geometry_msgs/msg/detail/pose__functions.h"

bool
multi_map_server__msg__MultiSparseMap3D__init(multi_map_server__msg__MultiSparseMap3D * msg)
{
  if (!msg) {
    return false;
  }
  // maps
  if (!multi_map_server__msg__SparseMap3D__Sequence__init(&msg->maps, 0)) {
    multi_map_server__msg__MultiSparseMap3D__fini(msg);
    return false;
  }
  // origins
  if (!geometry_msgs__msg__Pose__Sequence__init(&msg->origins, 0)) {
    multi_map_server__msg__MultiSparseMap3D__fini(msg);
    return false;
  }
  return true;
}

void
multi_map_server__msg__MultiSparseMap3D__fini(multi_map_server__msg__MultiSparseMap3D * msg)
{
  if (!msg) {
    return;
  }
  // maps
  multi_map_server__msg__SparseMap3D__Sequence__fini(&msg->maps);
  // origins
  geometry_msgs__msg__Pose__Sequence__fini(&msg->origins);
}

bool
multi_map_server__msg__MultiSparseMap3D__are_equal(const multi_map_server__msg__MultiSparseMap3D * lhs, const multi_map_server__msg__MultiSparseMap3D * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // maps
  if (!multi_map_server__msg__SparseMap3D__Sequence__are_equal(
      &(lhs->maps), &(rhs->maps)))
  {
    return false;
  }
  // origins
  if (!geometry_msgs__msg__Pose__Sequence__are_equal(
      &(lhs->origins), &(rhs->origins)))
  {
    return false;
  }
  return true;
}

bool
multi_map_server__msg__MultiSparseMap3D__copy(
  const multi_map_server__msg__MultiSparseMap3D * input,
  multi_map_server__msg__MultiSparseMap3D * output)
{
  if (!input || !output) {
    return false;
  }
  // maps
  if (!multi_map_server__msg__SparseMap3D__Sequence__copy(
      &(input->maps), &(output->maps)))
  {
    return false;
  }
  // origins
  if (!geometry_msgs__msg__Pose__Sequence__copy(
      &(input->origins), &(output->origins)))
  {
    return false;
  }
  return true;
}

multi_map_server__msg__MultiSparseMap3D *
multi_map_server__msg__MultiSparseMap3D__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  multi_map_server__msg__MultiSparseMap3D * msg = (multi_map_server__msg__MultiSparseMap3D *)allocator.allocate(sizeof(multi_map_server__msg__MultiSparseMap3D), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(multi_map_server__msg__MultiSparseMap3D));
  bool success = multi_map_server__msg__MultiSparseMap3D__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
multi_map_server__msg__MultiSparseMap3D__destroy(multi_map_server__msg__MultiSparseMap3D * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    multi_map_server__msg__MultiSparseMap3D__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
multi_map_server__msg__MultiSparseMap3D__Sequence__init(multi_map_server__msg__MultiSparseMap3D__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  multi_map_server__msg__MultiSparseMap3D * data = NULL;

  if (size) {
    data = (multi_map_server__msg__MultiSparseMap3D *)allocator.zero_allocate(size, sizeof(multi_map_server__msg__MultiSparseMap3D), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = multi_map_server__msg__MultiSparseMap3D__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        multi_map_server__msg__MultiSparseMap3D__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
multi_map_server__msg__MultiSparseMap3D__Sequence__fini(multi_map_server__msg__MultiSparseMap3D__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      multi_map_server__msg__MultiSparseMap3D__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

multi_map_server__msg__MultiSparseMap3D__Sequence *
multi_map_server__msg__MultiSparseMap3D__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  multi_map_server__msg__MultiSparseMap3D__Sequence * array = (multi_map_server__msg__MultiSparseMap3D__Sequence *)allocator.allocate(sizeof(multi_map_server__msg__MultiSparseMap3D__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = multi_map_server__msg__MultiSparseMap3D__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
multi_map_server__msg__MultiSparseMap3D__Sequence__destroy(multi_map_server__msg__MultiSparseMap3D__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    multi_map_server__msg__MultiSparseMap3D__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
multi_map_server__msg__MultiSparseMap3D__Sequence__are_equal(const multi_map_server__msg__MultiSparseMap3D__Sequence * lhs, const multi_map_server__msg__MultiSparseMap3D__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!multi_map_server__msg__MultiSparseMap3D__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
multi_map_server__msg__MultiSparseMap3D__Sequence__copy(
  const multi_map_server__msg__MultiSparseMap3D__Sequence * input,
  multi_map_server__msg__MultiSparseMap3D__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(multi_map_server__msg__MultiSparseMap3D);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    multi_map_server__msg__MultiSparseMap3D * data =
      (multi_map_server__msg__MultiSparseMap3D *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!multi_map_server__msg__MultiSparseMap3D__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          multi_map_server__msg__MultiSparseMap3D__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!multi_map_server__msg__MultiSparseMap3D__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
