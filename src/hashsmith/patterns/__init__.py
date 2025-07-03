"""
HashSmith Pattern Engine

Compositional pattern engine for generating targeted password dictionaries.
"""

from .engine import (
    # Base class
    BasePattern,
    
    # Primitive Patterns
    P,
    Birthday,
    
    # Composite Patterns
    PAnd,
    POr,
    RepeatPattern,
    InterleavePattern,
    
    # Core Components
    Transform,
    PatternType,
    
    # Helper Functions
    save_to_file
)

__all__ = [
    # Base
    "BasePattern",
    
    # Primitives
    "P",
    "Birthday",
    
    # Composites
    "PAnd",
    "POr",
    "RepeatPattern",
    "InterleavePattern",
    
    # Core
    "Transform",
    "PatternType",
    
    # Helpers
    "save_to_file",
]
