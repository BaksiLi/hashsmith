"""
HashSmith Pattern Engine

Compositional pattern engine for generating targeted password dictionaries.
"""

from .engine import (
    # Base class
    BasePattern,
    Birthday,
    InterleavePattern,
    # Primitive Patterns
    P,
    # Composite Patterns
    PAnd,
    PatternType,
    POr,
    RepeatPattern,
    # Core Components
    Transform,
    # Helper Functions
    save_to_file,
    # Constants
    EMPTY,
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
    # Constants
    "EMPTY",
]
