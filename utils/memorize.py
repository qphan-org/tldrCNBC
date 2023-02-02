from __future__ import annotations
from functools import wraps

def memorize(func: function):
    """Store values of a given input, and return the values if the input has been computed before

    Args:
        func (function): function that computes the input

    Returns:
        any: output value of the input
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        key = str(args) + str(kwargs)
        
        if key not in cache:
            cache[key] = func(*args, **kwargs)

        return cache[key]
    return wrapper