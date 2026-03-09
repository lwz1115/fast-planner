// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from multi_map_server:msg/MultiSparseMap3D.idl
// generated code does not contain a copyright notice

#ifndef MULTI_MAP_SERVER__MSG__DETAIL__MULTI_SPARSE_MAP3_D__FUNCTIONS_H_
#define MULTI_MAP_SERVER__MSG__DETAIL__MULTI_SPARSE_MAP3_D__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/visibility_control.h"
#include "multi_map_server/msg/rosidl_generator_c__visibility_control.h"

#include "multi_map_server/msg/detail/multi_sparse_map3_d__struct.h"

/// Initialize msg/MultiSparseMap3D message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * multi_map_server__msg__MultiSparseMap3D
 * )) before or use
 * multi_map_server__msg__MultiSparseMap3D__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_multi_map_server
bool
multi_map_server__msg__MultiSparseMap3D__init(multi_map_server__msg__MultiSparseMap3D * msg);

/// Finalize msg/MultiSparseMap3D message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_multi_map_server
void
multi_map_server__msg__MultiSparseMap3D__fini(multi_map_server__msg__MultiSparseMap3D * msg);

/// Create msg/MultiSparseMap3D message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * multi_map_server__msg__MultiSparseMap3D__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_multi_map_server
multi_map_server__msg__MultiSparseMap3D *
multi_map_server__msg__MultiSparseMap3D__create();

/// Destroy msg/MultiSparseMap3D message.
/**
 * It calls
 * multi_map_server__msg__MultiSparseMap3D__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_multi_map_server
void
multi_map_server__msg__MultiSparseMap3D__destroy(multi_map_server__msg__MultiSparseMap3D * msg);

/// Check for msg/MultiSparseMap3D message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_multi_map_server
bool
multi_map_server__msg__MultiSparseMap3D__are_equal(const multi_map_server__msg__MultiSparseMap3D * lhs, const multi_map_server__msg__MultiSparseMap3D * rhs);

/// Copy a msg/MultiSparseMap3D message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_multi_map_server
bool
multi_map_server__msg__MultiSparseMap3D__copy(
  const multi_map_server__msg__MultiSparseMap3D * input,
  multi_map_server__msg__MultiSparseMap3D * output);

/// Initialize array of msg/MultiSparseMap3D messages.
/**
 * It allocates the memory for the number of elements and calls
 * multi_map_server__msg__MultiSparseMap3D__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_multi_map_server
bool
multi_map_server__msg__MultiSparseMap3D__Sequence__init(multi_map_server__msg__MultiSparseMap3D__Sequence * array, size_t size);

/// Finalize array of msg/MultiSparseMap3D messages.
/**
 * It calls
 * multi_map_server__msg__MultiSparseMap3D__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_multi_map_server
void
multi_map_server__msg__MultiSparseMap3D__Sequence__fini(multi_map_server__msg__MultiSparseMap3D__Sequence * array);

/// Create array of msg/MultiSparseMap3D messages.
/**
 * It allocates the memory for the array and calls
 * multi_map_server__msg__MultiSparseMap3D__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_multi_map_server
multi_map_server__msg__MultiSparseMap3D__Sequence *
multi_map_server__msg__MultiSparseMap3D__Sequence__create(size_t size);

/// Destroy array of msg/MultiSparseMap3D messages.
/**
 * It calls
 * multi_map_server__msg__MultiSparseMap3D__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_multi_map_server
void
multi_map_server__msg__MultiSparseMap3D__Sequence__destroy(multi_map_server__msg__MultiSparseMap3D__Sequence * array);

/// Check for msg/MultiSparseMap3D message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_multi_map_server
bool
multi_map_server__msg__MultiSparseMap3D__Sequence__are_equal(const multi_map_server__msg__MultiSparseMap3D__Sequence * lhs, const multi_map_server__msg__MultiSparseMap3D__Sequence * rhs);

/// Copy an array of msg/MultiSparseMap3D messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_multi_map_server
bool
multi_map_server__msg__MultiSparseMap3D__Sequence__copy(
  const multi_map_server__msg__MultiSparseMap3D__Sequence * input,
  multi_map_server__msg__MultiSparseMap3D__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // MULTI_MAP_SERVER__MSG__DETAIL__MULTI_SPARSE_MAP3_D__FUNCTIONS_H_
