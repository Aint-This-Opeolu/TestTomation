"""
Math utility functions.

This module provides basic math operations.
"""


def add(a, b):
    """
    Add two numbers and return the result.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        The sum of a and b
    """
    return a + b


def subtract(a, b):
    """
    Subtract b from a and return the result.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        The difference between a and b (a - b)
    """
    return a - b


def multiply(a, b):
    """
    Multiply two numbers and return the result.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        The product of a and b
    """
    return a * b


def divide(a, b):
    """
    Divide a by b and return the result.
    
    Args:
        a: Numerator
        b: Denominator
        
    Returns:
        The quotient of a divided by b
        
    Raises:
        ValueError: If b is zero
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def factorial(n):
    """
    Calculate the factorial of n.
    
    Args:
        n: A non-negative integer
        
    Returns:
        The factorial of n
        
    Raises:
        ValueError: If n is negative
    """
    if not isinstance(n, int):
        raise TypeError("Input must be an integer")
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)


def fibonacci(n):
    """
    Calculate the nth Fibonacci number.
    
    Args:
        n: A non-negative integer
        
    Returns:
        The nth Fibonacci number
        
    Raises:
        ValueError: If n is negative
    """
    if not isinstance(n, int):
        raise TypeError("Input must be an integer")
    if n < 0:
        raise ValueError("Fibonacci is not defined for negative numbers")
    if n == 0:
        return 0
    if n == 1:
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)