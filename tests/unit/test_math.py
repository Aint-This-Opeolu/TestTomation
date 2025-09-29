"""
Unit tests for math functions.

This module contains unit tests for basic math functions.
"""

import pytest
from src.utils.math_utils import add, subtract, multiply, divide


def test_add():
    """Test the add function."""
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0
    assert add(1.5, 2.5) == 4.0


def test_subtract():
    """Test the subtract function."""
    assert subtract(5, 3) == 2
    assert subtract(1, 1) == 0
    assert subtract(0, 5) == -5
    assert subtract(10.5, 0.5) == 10.0


def test_multiply():
    """Test the multiply function."""
    assert multiply(2, 3) == 6
    assert multiply(-1, 1) == -1
    assert multiply(0, 5) == 0
    assert multiply(2.5, 2) == 5.0


def test_divide():
    """Test the divide function."""
    assert divide(6, 3) == 2
    assert divide(1, 1) == 1
    assert divide(0, 5) == 0
    assert divide(5, 2) == 2.5


def test_divide_by_zero():
    """Test division by zero raises an exception."""
    with pytest.raises(ValueError) as excinfo:
        divide(5, 0)
    assert "Cannot divide by zero" in str(excinfo.value)


@pytest.mark.parametrize("a, b, expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
    (10, -5, 5),
])
def test_add_parametrized(a, b, expected):
    """Test the add function with multiple inputs using parametrize."""
    assert add(a, b) == expected


@pytest.mark.slow
def test_complex_calculation():
    """A more complex test marked as slow."""
    result = 0
    for i in range(1000000):
        result = add(result, i)
    assert result == 499999500000