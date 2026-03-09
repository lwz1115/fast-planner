"""
Simple test runner for algorithm selection without pytest.
"""

from pydantic import ValidationError

from fastapi_planner.models import PlanRequest, Position
from fastapi_planner.config import ROSTopicsConfig


def test_algorithm_default_value():
    """Test that default algorithm is 'kinodynamic'."""
    print("Testing default algorithm value...")
    request = PlanRequest(
        start=Position(x=0.0, y=0.0, z=1.0),
        goal=Position(x=10.0, y=5.0, z=1.5)
    )
    assert request.algorithm == "kinodynamic", f"Expected 'kinodynamic', got '{request.algorithm}'"
    print("✓ Default algorithm is 'kinodynamic'")


def test_algorithm_kinodynamic():
    """Test that 'kinodynamic' algorithm is accepted."""
    print("Testing kinodynamic algorithm...")
    request = PlanRequest(
        start=Position(x=0.0, y=0.0, z=1.0),
        goal=Position(x=10.0, y=5.0, z=1.5),
        algorithm="kinodynamic"
    )
    assert request.algorithm == "kinodynamic"
    print("✓ Kinodynamic algorithm accepted")


def test_algorithm_topological():
    """Test that 'topological' algorithm is accepted."""
    print("Testing topological algorithm...")
    request = PlanRequest(
        start=Position(x=0.0, y=0.0, z=1.0),
        goal=Position(x=10.0, y=5.0, z=1.5),
        algorithm="topological"
    )
    assert request.algorithm == "topological"
    print("✓ Topological algorithm accepted")


def test_algorithm_invalid():
    """Test that invalid algorithm values are rejected."""
    print("Testing invalid algorithm rejection...")
    try:
        PlanRequest(
            start=Position(x=0.0, y=0.0, z=1.0),
            goal=Position(x=10.0, y=5.0, z=1.5),
            algorithm="invalid_algorithm"
        )
        raise AssertionError("Expected ValidationError but none was raised")
    except ValidationError as e:
        errors = e.errors()
        assert len(errors) > 0
        assert any("algorithm" in str(error.get("loc", [])) for error in errors)
        print("✓ Invalid algorithm properly rejected with ValidationError")


def test_topic_routing_default():
    """Test topic routing with default configuration."""
    print("Testing default topic routing...")
    topics = ROSTopicsConfig()
    
    kino_topic = topics.get_goal_topic_for_algorithm("kinodynamic")
    topo_topic = topics.get_goal_topic_for_algorithm("topological")
    
    assert kino_topic == "/move_base_simple/goal", f"Expected '/move_base_simple/goal', got '{kino_topic}'"
    assert topo_topic == "/move_base_simple/goal", f"Expected '/move_base_simple/goal', got '{topo_topic}'"
    print("✓ Both algorithms use default goal topic")


def test_topic_routing_kinodynamic_specific():
    """Test topic routing with kinodynamic-specific topic."""
    print("Testing kinodynamic-specific topic routing...")
    topics = ROSTopicsConfig(
        kinodynamic_goal="/planning/kinodynamic_goal"
    )
    
    kino_topic = topics.get_goal_topic_for_algorithm("kinodynamic")
    topo_topic = topics.get_goal_topic_for_algorithm("topological")
    
    assert kino_topic == "/planning/kinodynamic_goal"
    assert topo_topic == "/move_base_simple/goal"
    print("✓ Kinodynamic uses specific topic, topological uses default")


def test_topic_routing_topological_specific():
    """Test topic routing with topological-specific topic."""
    print("Testing topological-specific topic routing...")
    topics = ROSTopicsConfig(
        topological_goal="/planning/topological_goal"
    )
    
    kino_topic = topics.get_goal_topic_for_algorithm("kinodynamic")
    topo_topic = topics.get_goal_topic_for_algorithm("topological")
    
    assert kino_topic == "/move_base_simple/goal"
    assert topo_topic == "/planning/topological_goal"
    print("✓ Topological uses specific topic, kinodynamic uses default")


def test_topic_routing_both_specific():
    """Test topic routing with both algorithm-specific topics."""
    print("Testing both algorithm-specific topics...")
    topics = ROSTopicsConfig(
        kinodynamic_goal="/planning/kinodynamic_goal",
        topological_goal="/planning/topological_goal"
    )
    
    kino_topic = topics.get_goal_topic_for_algorithm("kinodynamic")
    topo_topic = topics.get_goal_topic_for_algorithm("topological")
    
    assert kino_topic == "/planning/kinodynamic_goal"
    assert topo_topic == "/planning/topological_goal"
    print("✓ Each algorithm uses its specific topic")


def test_plan_request_with_all_parameters():
    """Test PlanRequest with all parameters including algorithm."""
    print("Testing PlanRequest with all parameters...")
    request = PlanRequest(
        start=Position(x=0.0, y=0.0, z=1.0),
        goal=Position(x=10.0, y=5.0, z=1.5),
        max_velocity=3.0,
        max_acceleration=2.0,
        algorithm="topological",
        use_current_odom=False
    )
    
    assert request.start.x == 0.0
    assert request.goal.x == 10.0
    assert request.max_velocity == 3.0
    assert request.max_acceleration == 2.0
    assert request.algorithm == "topological"
    assert request.use_current_odom is False
    print("✓ PlanRequest with all parameters works correctly")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("Algorithm Selection Tests")
    print("="*60 + "\n")
    
    tests = [
        test_algorithm_default_value,
        test_algorithm_kinodynamic,
        test_algorithm_topological,
        test_algorithm_invalid,
        test_topic_routing_default,
        test_topic_routing_kinodynamic_specific,
        test_topic_routing_topological_specific,
        test_topic_routing_both_specific,
        test_plan_request_with_all_parameters,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
