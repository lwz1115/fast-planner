#!/usr/bin/env python3
"""
Verification script for algorithm selection implementation.

This script demonstrates that the algorithm selection feature works correctly
by testing the key components without requiring a full ROS environment.
"""

import sys
from fastapi_planner.models import PlanRequest, Position
from fastapi_planner.config import ROSTopicsConfig


def print_section(title):
    """Print a section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def verify_model_validation():
    """Verify PlanRequest model handles algorithm parameter correctly."""
    print_section("1. Model Validation")
    
    # Test 1: Default algorithm
    print("\n✓ Test 1: Default algorithm value")
    request = PlanRequest(
        start=Position(x=0.0, y=0.0, z=1.0),
        goal=Position(x=10.0, y=5.0, z=1.5)
    )
    print(f"  Default algorithm: {request.algorithm}")
    assert request.algorithm == "kinodynamic", "Default should be kinodynamic"
    
    # Test 2: Explicit kinodynamic
    print("\n✓ Test 2: Explicit kinodynamic algorithm")
    request = PlanRequest(
        start=Position(x=0.0, y=0.0, z=1.0),
        goal=Position(x=10.0, y=5.0, z=1.5),
        algorithm="kinodynamic"
    )
    print(f"  Algorithm: {request.algorithm}")
    assert request.algorithm == "kinodynamic"
    
    # Test 3: Topological algorithm
    print("\n✓ Test 3: Topological algorithm")
    request = PlanRequest(
        start=Position(x=0.0, y=0.0, z=1.0),
        goal=Position(x=10.0, y=5.0, z=1.5),
        algorithm="topological"
    )
    print(f"  Algorithm: {request.algorithm}")
    assert request.algorithm == "topological"
    
    # Test 4: Invalid algorithm
    print("\n✓ Test 4: Invalid algorithm rejection")
    try:
        from pydantic import ValidationError
        request = PlanRequest(
            start=Position(x=0.0, y=0.0, z=1.0),
            goal=Position(x=10.0, y=5.0, z=1.5),
            algorithm="invalid"
        )
        print("  ERROR: Should have raised ValidationError!")
        return False
    except ValidationError as e:
        print(f"  Correctly rejected with ValidationError")
        print(f"  Error details: {e.errors()[0]['msg']}")
    
    return True


def verify_topic_routing():
    """Verify topic routing configuration works correctly."""
    print_section("2. Topic Routing Configuration")
    
    # Test 1: Default configuration
    print("\n✓ Test 1: Default configuration (no algorithm-specific topics)")
    topics = ROSTopicsConfig()
    kino_topic = topics.get_goal_topic_for_algorithm("kinodynamic")
    topo_topic = topics.get_goal_topic_for_algorithm("topological")
    print(f"  Kinodynamic topic: {kino_topic}")
    print(f"  Topological topic: {topo_topic}")
    assert kino_topic == "/move_base_simple/goal"
    assert topo_topic == "/move_base_simple/goal"
    
    # Test 2: Kinodynamic-specific topic
    print("\n✓ Test 2: Kinodynamic-specific topic configured")
    topics = ROSTopicsConfig(
        kinodynamic_goal="/planning/kino_goal"
    )
    kino_topic = topics.get_goal_topic_for_algorithm("kinodynamic")
    topo_topic = topics.get_goal_topic_for_algorithm("topological")
    print(f"  Kinodynamic topic: {kino_topic}")
    print(f"  Topological topic: {topo_topic}")
    assert kino_topic == "/planning/kino_goal"
    assert topo_topic == "/move_base_simple/goal"
    
    # Test 3: Topological-specific topic
    print("\n✓ Test 3: Topological-specific topic configured")
    topics = ROSTopicsConfig(
        topological_goal="/planning/topo_goal"
    )
    kino_topic = topics.get_goal_topic_for_algorithm("kinodynamic")
    topo_topic = topics.get_goal_topic_for_algorithm("topological")
    print(f"  Kinodynamic topic: {kino_topic}")
    print(f"  Topological topic: {topo_topic}")
    assert kino_topic == "/move_base_simple/goal"
    assert topo_topic == "/planning/topo_goal"
    
    # Test 4: Both algorithm-specific topics
    print("\n✓ Test 4: Both algorithm-specific topics configured")
    topics = ROSTopicsConfig(
        kinodynamic_goal="/planning/kino_goal",
        topological_goal="/planning/topo_goal"
    )
    kino_topic = topics.get_goal_topic_for_algorithm("kinodynamic")
    topo_topic = topics.get_goal_topic_for_algorithm("topological")
    print(f"  Kinodynamic topic: {kino_topic}")
    print(f"  Topological topic: {topo_topic}")
    assert kino_topic == "/planning/kino_goal"
    assert topo_topic == "/planning/topo_goal"
    
    return True


def verify_request_serialization():
    """Verify requests serialize correctly with algorithm parameter."""
    print_section("3. Request Serialization")
    
    print("\n✓ Test: Request with topological algorithm serializes correctly")
    request = PlanRequest(
        start=Position(x=0.0, y=0.0, z=1.0),
        goal=Position(x=10.0, y=5.0, z=1.5),
        max_velocity=3.0,
        max_acceleration=2.0,
        algorithm="topological",
        use_current_odom=False
    )
    
    # Convert to dict (as would be sent in JSON)
    request_dict = request.dict()
    print(f"  Serialized request:")
    for key, value in request_dict.items():
        if isinstance(value, dict):
            print(f"    {key}: {value}")
        else:
            print(f"    {key}: {value}")
    
    assert request_dict["algorithm"] == "topological"
    assert request_dict["max_velocity"] == 3.0
    assert request_dict["max_acceleration"] == 2.0
    
    return True


def main():
    """Run all verification tests."""
    print("\n" + "="*70)
    print("  Algorithm Selection Implementation Verification")
    print("="*70)
    
    try:
        # Run verification tests
        success = True
        success = verify_model_validation() and success
        success = verify_topic_routing() and success
        success = verify_request_serialization() and success
        
        # Print summary
        print_section("Verification Summary")
        if success:
            print("\n✅ All verification tests passed!")
            print("\nImplementation Status:")
            print("  ✓ Algorithm parameter handling (Req 7.1, 7.2)")
            print("  ✓ Topic routing based on algorithm (Req 7.3)")
            print("  ✓ Validation for supported algorithms (Req 7.4)")
            print("\nThe algorithm selection feature is fully implemented and working.")
            return 0
        else:
            print("\n❌ Some verification tests failed!")
            return 1
            
    except Exception as e:
        print(f"\n❌ Verification failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
