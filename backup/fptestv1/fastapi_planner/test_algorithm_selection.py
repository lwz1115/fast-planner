"""
Test algorithm selection functionality.

This test verifies that:
1. Algorithm parameter is properly validated
2. Topic routing works based on algorithm type
3. Default algorithm is "kinodynamic"
4. Invalid algorithm values are rejected with 400 status
"""

import pytest
from pydantic import ValidationError

from fastapi_planner.models import PlanRequest, Position
from fastapi_planner.config import ROSTopicsConfig


def test_algorithm_default_value():
    """Test that default algorithm is 'kinodynamic'."""
    request = PlanRequest(
        start=Position(x=0.0, y=0.0, z=1.0),
        goal=Position(x=10.0, y=5.0, z=1.5)
    )
    assert request.algorithm == "kinodynamic"


def test_algorithm_kinodynamic():
    """Test that 'kinodynamic' algorithm is accepted."""
    request = PlanRequest(
        start=Position(x=0.0, y=0.0, z=1.0),
        goal=Position(x=10.0, y=5.0, z=1.5),
        algorithm="kinodynamic"
    )
    assert request.algorithm == "kinodynamic"


def test_algorithm_topological():
    """Test that 'topological' algorithm is accepted."""
    request = PlanRequest(
        start=Position(x=0.0, y=0.0, z=1.0),
        goal=Position(x=10.0, y=5.0, z=1.5),
        algorithm="topological"
    )
    assert request.algorithm == "topological"


def test_algorithm_invalid():
    """Test that invalid algorithm values are rejected."""
    with pytest.raises(ValidationError) as exc_info:
        PlanRequest(
            start=Position(x=0.0, y=0.0, z=1.0),
            goal=Position(x=10.0, y=5.0, z=1.5),
            algorithm="invalid_algorithm"
        )
    
    # Verify the error is about the algorithm field
    errors = exc_info.value.errors()
    assert len(errors) > 0
    assert any("algorithm" in str(error.get("loc", [])) for error in errors)


def test_topic_routing_default():
    """Test topic routing with default configuration."""
    topics = ROSTopicsConfig()
    
    # Both algorithms should use default goal topic when no specific topics configured
    assert topics.get_goal_topic_for_algorithm("kinodynamic") == "/move_base_simple/goal"
    assert topics.get_goal_topic_for_algorithm("topological") == "/move_base_simple/goal"


def test_topic_routing_kinodynamic_specific():
    """Test topic routing with kinodynamic-specific topic."""
    topics = ROSTopicsConfig(
        kinodynamic_goal="/planning/kinodynamic_goal"
    )
    
    # Kinodynamic should use specific topic
    assert topics.get_goal_topic_for_algorithm("kinodynamic") == "/planning/kinodynamic_goal"
    # Topological should use default
    assert topics.get_goal_topic_for_algorithm("topological") == "/move_base_simple/goal"


def test_topic_routing_topological_specific():
    """Test topic routing with topological-specific topic."""
    topics = ROSTopicsConfig(
        topological_goal="/planning/topological_goal"
    )
    
    # Kinodynamic should use default
    assert topics.get_goal_topic_for_algorithm("kinodynamic") == "/move_base_simple/goal"
    # Topological should use specific topic
    assert topics.get_goal_topic_for_algorithm("topological") == "/planning/topological_goal"


def test_topic_routing_both_specific():
    """Test topic routing with both algorithm-specific topics."""
    topics = ROSTopicsConfig(
        kinodynamic_goal="/planning/kinodynamic_goal",
        topological_goal="/planning/topological_goal"
    )
    
    # Each algorithm should use its specific topic
    assert topics.get_goal_topic_for_algorithm("kinodynamic") == "/planning/kinodynamic_goal"
    assert topics.get_goal_topic_for_algorithm("topological") == "/planning/topological_goal"


def test_plan_request_with_all_parameters():
    """Test PlanRequest with all parameters including algorithm."""
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
