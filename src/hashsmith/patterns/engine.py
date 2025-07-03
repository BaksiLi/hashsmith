"""
Pattern-based password generation engine with compositional design.

This module implements a LISP-influenced approach to password generation where
passwords are built from composable patterns with explicit transformations.
"""

from abc import ABC, abstractmethod
from typing import List, Iterator, Callable, Union, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum, auto
import itertools
import re
from pathlib import Path
from datetime import date


class Transform(Enum):
    """Standard text transformations for password patterns."""
    LOWER = auto()
    UPPER = auto() 
    CAPITALIZE = auto()
    TITLE = auto()
    REVERSE = auto()
    LEET_BASIC = auto()      # a->@, e->3, i->1, o->0, s->$
    LEET_ADVANCED = auto()   # More extensive leet speak
    
    # Numeric transformations
    ZERO_PAD_2 = auto()      # 5 -> 05
    ZERO_PAD_4 = auto()      # 5 -> 0005


class PatternType(Enum):
    """Types of pattern composition."""
    AND = auto()             # Sequential concatenation (replaces Ordered)
    OR = auto()              # One of several alternatives


@dataclass
class TransformConfig:
    """Configuration for pattern transformations."""
    transforms: List[Transform]
    probability: float = 1.0
    custom_fn: Optional[Callable[[str], str]] = None
    
    def estimate_count(self) -> int:
        """Estimate number of possible outputs."""
        pass

    def generate(self, min_len: int = 0, max_len: int = 99) -> Iterator[str]:
        """
        Generate all possible values for this pattern, applying constraints.
        This is a wrapper around the internal _generate method.
        """
        for password in self._generate():
            if min_len <= len(password) <= max_len:
                yield password

    @abstractmethod
    def _generate(self) -> Iterator[str]:
        """Internal generator without constraints."""
        pass


class BasePattern(ABC):
    """Abstract base for all password patterns."""
    
    def __init__(self, name: str = ""):
        self.name = name
    
    @abstractmethod
    def _generate(self) -> Iterator[str]:
        """Internal generator without constraints."""
        pass
    
    @abstractmethod
    def estimate_count(self) -> int:
        """Estimate number of possible outputs."""
        pass

    def generate(self, min_len: int = 0, max_len: int = 99) -> Iterator[str]:
        """
        Generate all possible values for this pattern, applying constraints.
        This is a wrapper around the internal _generate method.
        """
        for password in self._generate():
            if min_len <= len(password) <= max_len:
                yield password

    def __or__(self, other: 'BasePattern') -> 'POr':
        """Syntactic sugar for POr(self, other)."""
        return POr(self, other)

    def __and__(self, other: 'BasePattern') -> 'PAnd':
        """Syntactic sugar for PAnd(self, other)."""
        return PAnd(self, other)


class P(BasePattern):
    """Basic pattern containing a list of strings with transformations."""
    
    def __init__(self, items: List[str], name: str = "", 
                 transforms: Optional[List[Transform]] = None,
                 custom_transforms: Optional[List[Callable[[str], str]]] = None):
        super().__init__(name)
        self.items = items
        self.transforms = transforms or []  # Default to no transforms
        self.custom_transforms = custom_transforms or []
    
    def alter(self, *transforms: Union[Transform, Callable[[str], str]]) -> 'P':
        """Add transformations to this pattern (fluent interface)."""
        if not transforms:
            # If no transforms provided, return self unchanged
            return self
            
        # Generate all current results and use them as base items for new pattern
        current_results = list(self._generate())
        
        # Create new pattern with current results as base items and new transforms
        new_transforms = []
        new_custom = []
        
        for t in transforms:
            if isinstance(t, Transform):
                new_transforms.append(t)
            elif callable(t):
                new_custom.append(t)
                
        return P(current_results, self.name, new_transforms, new_custom)
    
    def lambda_transform(self, fn: Callable[[str], str]) -> 'P':
        """Add custom lambda transformation."""
        new_custom = self.custom_transforms + [fn]
        return P(self.items, self.name, self.transforms, new_custom)
    
    def _generate(self) -> Iterator[str]:
        """Generate original items plus all transformed versions."""
        # Create a combined list of all transform functions
        all_transforms: List[Callable[[str], str]] = [
            lambda text, t=t: self._apply_transform(text, t) for t in self.transforms
        ]
        all_transforms.extend(self.custom_transforms)

        for item in self.items:
            # Always yield the original item first
            yield item
            
            # Then yield transformed versions if any transforms exist
            if all_transforms:
                # Use a set to avoid duplicate yields from different transforms
                # (e.g., LOWER on "test" and CAPITALIZE on "test" are the same)
                yielded = set([item])  # Include original to avoid re-yielding it
                for transform_fn in all_transforms:
                    result = transform_fn(item)
                    if result not in yielded:
                        yielded.add(result)
                        yield result
    
    def estimate_count(self) -> int:
        # Always include original items (1) plus any transforms
        transform_count = len(self.transforms) + len(self.custom_transforms)
        return len(self.items) * (1 + transform_count)
    
    def _apply_transform(self, text: str, transform: Transform) -> str:
        """Apply a single transformation to text."""
        if transform == Transform.LOWER:
            return text.lower()
        elif transform == Transform.UPPER:
            return text.upper()
        elif transform == Transform.CAPITALIZE:
            return text.capitalize()
        elif transform == Transform.TITLE:
            return text.title()
        elif transform == Transform.REVERSE:
            return text[::-1]
        elif transform == Transform.LEET_BASIC:
            return self._leet_basic(text)
        elif transform == Transform.LEET_ADVANCED:
            return self._leet_advanced(text)
        elif transform == Transform.ZERO_PAD_2:
            return text.zfill(2) if text.isdigit() else text
        elif transform == Transform.ZERO_PAD_4:
            return text.zfill(4) if text.isdigit() else text
        else:
            return text
    
    def _leet_basic(self, text: str) -> str:
        """Basic leet speak transformations."""
        replacements = {'a': '@', 'e': '3', 'i': '1', 'o': '0', 's': '$', 'l': '1'}
        result = text.lower()
        for char, replacement in replacements.items():
            result = result.replace(char, replacement)
        return result
    
    def _leet_advanced(self, text: str) -> str:
        """Advanced leet speak transformations."""
        replacements = {
            'a': '@', 'e': '3', 'i': '1', 'o': '0', 's': '$', 'l': '1',
            't': '7', 'b': '6', 'g': '9', 'z': '2', 'h': '#'
        }
        result = text.lower()
        for char, replacement in replacements.items():
            result = result.replace(char, replacement)
        return result


class PAnd(BasePattern):
    """
    Concatenates patterns in sequential order (Logical AND).
    Replaces the old `OrderedPattern` and `PasswordStructure`.
    """
    
    def __init__(self, *patterns: BasePattern, name: str = "PAnd"):
        super().__init__(name)
        self.patterns = patterns
    
    def _generate(self) -> Iterator[str]:
        """Generate cartesian product of all sub-patterns."""
        # Note: list() is needed to "realize" the generators for product
        pattern_generators = [list(p._generate()) for p in self.patterns]
        for combination in itertools.product(*pattern_generators):
            yield ''.join(combination)
    
    def estimate_count(self) -> int:
        count = 1
        for pattern in self.patterns:
            count *= pattern.estimate_count()
        return count


class POr(BasePattern):
    """
    Chooses one pattern from several alternatives (Logical OR).
    It chains the generators of all sub-patterns.
    """
    
    def __init__(self, *patterns: BasePattern, name: str = "POr"):
        super().__init__(name)
        self.patterns = patterns
    
    def _generate(self) -> Iterator[str]:
        """Generate values from all alternative patterns."""
        for pattern in self.patterns:
            yield from pattern._generate()
    
    def estimate_count(self) -> int:
        return sum(p.estimate_count() for p in self.patterns)


class RepeatPattern(BasePattern):
    """Repeat a pattern N times."""
    
    def __init__(self, pattern: BasePattern, count: int, name: str = "repeat"):
        super().__init__(name)
        self.pattern = pattern
        self.count = count
    
    def _generate(self) -> Iterator[str]:
        """Generate pattern repeated count times."""
        pattern_values = list(self.pattern._generate())
        for combo in itertools.product(pattern_values, repeat=self.count):
            yield ''.join(combo)
    
    def estimate_count(self) -> int:
        return self.pattern.estimate_count() ** self.count


class InterleavePattern(BasePattern):
    """Insert separator between other patterns."""
    
    def __init__(self, separator: str, *patterns: BasePattern, name: str = "interleave"):
        super().__init__(name)
        self.separator = separator
        self.patterns = patterns
    
    def _generate(self) -> Iterator[str]:
        """Generate patterns with separator between them."""
        pattern_generators = [list(p._generate()) for p in self.patterns]
        for combination in itertools.product(*pattern_generators):
            yield self.separator.join(combination)
    
    def estimate_count(self) -> int:
        count = 1
        for pattern in self.patterns:
            count *= pattern.estimate_count()
        return count


class Birthday(BasePattern):
    """Generate birthday-based number patterns."""
    
    def __init__(self, years: Optional[List[int]] = None, 
                 formats: Optional[List[str]] = None, name: str = "birthday"):
        super().__init__(name)
        self.years = years or list(range(1980, 2005))  # Common birth years
        self.months = list(range(1, 13))
        self.days = list(range(1, 32))
        self.formats = formats or ["MMDD", "YYMMDD", "YYYYMMDD", "DDMM"]
    
    def _generate(self) -> Iterator[str]:
        """Generate birthday patterns in various formats, skipping invalid dates."""
        for year in self.years:
            for month in self.months:
                for day in self.days:
                    try:
                        # Create a date object to validate the date (handles leap years)
                        d = date(year, month, day)
                        for fmt in self.formats:
                            yield self._format_date(d, fmt)
                    except ValueError:
                        # Skip invalid dates like Feb 30th or Apr 31st
                        continue
    
    def estimate_count(self) -> int:
        # A more accurate estimate would be complex, this is a reasonable upper bound
        return len(self.years) * 366 * len(self.formats)
    
    def _format_date(self, d: date, format_type: str) -> str:
        """Format date according to specified format using strftime."""
        if format_type == "MMDD":
            return d.strftime("%m%d")
        elif format_type == "YYMMDD":
            return d.strftime("%y%m%d")
        elif format_type == "YYYYMMDD":
            return d.strftime("%Y%m%d")
        elif format_type == "DDMM":
            return d.strftime("%d%m")
        else:
            return d.strftime("%Y%m%d")


# Convenience functions for fluent interface
def save_to_file(pattern: BasePattern, filepath: Path, min_len: int, max_len: int, max_count: Optional[int] = None) -> int:
    """
    Generate passwords from a pattern and save them to a file.
    
    Args:
        pattern: The pattern to generate from.
        filepath: The path to the output file.
        min_len: Minimum password length.
        max_len: Maximum password length.
        max_count: The maximum number of passwords to generate.
        
    Returns:
        The total number of passwords written to the file.
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with open(filepath, 'w') as f:
        for password in pattern.generate(min_len, max_len):
            f.write(password + '\n')
            count += 1
            if max_count and count >= max_count:
                break
    return count 