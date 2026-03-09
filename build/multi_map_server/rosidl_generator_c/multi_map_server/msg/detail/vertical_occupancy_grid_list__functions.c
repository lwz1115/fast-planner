// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from multi_map_server:msg/VerticalOccupancyGridList.idl
// generated code does not contain a copyright notice
#include "multi_map_server/msg/detail/vertical_occupancy_grid_list__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `upper`
// Member `lower`
// Member `mass`
#include "rosidl_runtime_c/primitives_sequence_functions.h"

bool
multi_map_server__msg__VerticalOccupancyGridList__init(multi_map_server__msg__VerticalOccupancyGridList * msg)
{
  if (!msg) {
    return false;
  }
  // x
  // y
  // upper
  if (!rosidl_runtime_c__int32__Sequence__init(&msg->upper, 0)) {
    multi_map_server__msg__VerticalOccupancyGridList__fini(msg);
    return false;
  }
  // lower
  if (!rosidl_runtime_c__int32__Sequence__init(&msg->lower, 0)) {
    multi_map_server__msg__VerticalOccupancyGridList__fini(msg);
    return false;
  }
  // mass
  if (!rosidl_runtime_c__int32__Sequence__init(&msg->mass, 0)) {
    multi_map_server__msg__VerticalOccupancyGridList__fini(msg);
    return false;
  }
  return true;
}

void
multi_map_server__msg__VerticalOccupancyGridList__fini(multi_map_server__msg__VerticalOccupancyGridList * msg)
{
  if (!msg) {
    return;
  }
  // x
  // y
  // upper
  rosidl_runtime_c__int32__Sequence__fini(&msg->upper);
  // lower
  rosidl_runtime_c__int32__Sequence__fini(&msg->lower);
  // mass
  rosidl_runtime_c__int32__Sequence__fini(&msg->mass);
}

bool
multi_map_server__msg__VerticalOccupancyGridList__are_equal(const multi_map_server__msg__VerticalOccupancyGridList * lhs, const multi_map_server__msg__VerticalOccupancyGridList * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // x
  if (lhs->x != rhs->x) {
    return false;
  }
  // y
  if (lhs->y != rhs->y) {
    return false;
  }
  // upper
  if (!rosidl_runtime_c__int32__Sequence__are_equal(
      &(lhs->upper), &(rhs->upper)))
  {
    return false;
  }
  // lower
  if (!rosidl_runtime_c__int32__Sequence__are_equal(
      &(lhs->lower), &(rhs->lower)))
  {
    return false;
  }
  // mass
  if (!rosidl_runtime_c__int32__Sequence__are_equal(
      &(lhs->mass), &(rhs->mass)))
  {
    return false;
  }
  return true;
}

bool
multi_map_server__msg__VerticalOccupancyGridList__copy(
  const multi_map_server__msg__VerticalOccupancyGridList * input,
  multi_map_server__msg__VerticalOccupancyGridList * output)
{
  if (!input || !output) {
    return false;
  }
  // x
  output->x = input->x;
  // y
  output->y = input->y;
  // upper
  if (!rosidl_runtime_c__int32__Sequence__copy(
      &(input->upper), &(output->upper)))
  {
    return false;
  }
  // lower
  if (!rosidl_runtime_c__int32__Sequence__copy(
      &(input->lower), &(output->lower)))
  {
    return false;
  }
  // mass
  if (!rosidl_runtime_c__int32__Sequence__copy(
      &(input->mass), &(output->mass)))
  {
    return false;
  }
  return true;
}

multi_map_server__msg__VerticalOccupancyGridList *
multi_map_server__msg__VerticalOccupancyGridList__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  multi_map_server__msg__VerticalOccupancyGridList * msg = (multi_map_server__msg__VerticalOccupancyGridList *)allocator.allocate(sizeof(multi_map_server__msg__VerticalOccupancyGridList), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(multi_map_server__msg__VerticalOccupancyGridList));
  bool success = multi_map_server__msg__VerticalOccupancyGridList__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
multi_map_server__msg__VerticalOccupancyGridList__destroy(multi_map_server__msg__VerticalOccupancyGridList * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    multi_map_server__msg__VerticalOccupancyGridList__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
multi_map_server__msg__VerticalOccupancyGridList__Sequence__init(multi_map_server__msg__VerticalOccupancyGridList__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  multi_map_server__msg__VerticalOccupancyGridList * data = NULL;

  if (size) {
    data = (multi_map_server__msg__VerticalOccupancyGridList *)allocator.zero_allocate(size, sizeof(multi_map_server__msg__VerticalOccupancyGridList), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = multi_map_server__msg__VerticalOccupancyGridList__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        multi_map_server__msg__VerticalOccupancyGridList__fini(&data[i - 1]);
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
multi_map_server__msg__VerticalOccupancyGridList__Sequence__fini(multi_map_server__msg__VerticalOccupancyGridList__Sequence * array)
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
      multi_map_server__msg__VerticalOccupancyGridList__fini(&array->data[i]);
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

multi_map_server__msg__VerticalOccupancyGridList__Sequence *
multi_map_server__msg__VerticalOccupancyGridList__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  multi_map_server__msg__VerticalOccupancyGridList__Sequence * array = (multi_map_server__msg__VerticalOccupancyGridList__Sequence *)allocator.allocate(sizeof(multi_map_server__msg__VerticalOccupancyGridList__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = multi_map_server__msg__VerticalOccupancyGridList__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
multi_map_server__msg__VerticalOccupancyGridList__Sequence__destroy(multi_map_server__msg__VerticalOccupancyGridList__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    multi_map_server__msg__VerticalOccupancyGridList__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
multi_map_server__msg__VerticalOccupancyGridList__Sequence__are_equal(const multi_map_server__msg__VerticalOccupancyGridList__Sequence * lhs, const multi_map_server__msg__VerticalOccupancyGridList__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!multi_map_server__msg__VerticalOccupancyGridList__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
multi_map_server__msg__VerticalOccupancyGridList__Sequence__copy(
  const multi_map_server__msg__VerticalOccupancyGridList__Sequence * input,
  multi_map_server__msg__VerticalOccupancyGridList__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(multi_map_server__msg__VerticalOccupancyGridList);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    multi_map_server__msg__VerticalOccupancyGridList * data =
      (multi_map_server__msg__VerticalOccupancyGridList *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!multi_map_server__msg__VerticalOccupancyGridList__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          multi_map_server__msg__VerticalOccupancyGridList__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!multi_map_server__msg__VerticalOccupancyGridList__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
