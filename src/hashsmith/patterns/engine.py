"""
Pattern-based password generation engine with compositional design.

This module implements a LISP-influenced approach to password generation where
passwords are built from composable patterns with explicit transformations.
"""

import itertools
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from datetime import date
from enum import Enum, auto
from pathlib import Path




class Transform(Enum):
    """Standard text transformations for password patterns."""

    LOWER = auto()
    UPPER = auto()
    CAPITALIZE = auto()
    TITLE = auto()
    REVERSE = auto()
    LEET_BASIC = auto()  # a->@, e->3, i->1, o->0, s->$
    LEET_ADVANCED = auto()  # More extensive leet speak
    REPEAT = auto()  # hello -> hheelllloo (double each character)

    # Numeric transformations
    ZERO_PAD_2 = auto()  # 5 -> 05
    ZERO_PAD_4 = auto()  # 5 -> 0005


class PatternType(Enum):
    """Types of pattern composition."""

    AND = auto()  # Sequential concatenation (replaces Ordered)
    OR = auto()  # One of several alternatives


@dataclass
class TransformConfig:
    """Configuration for pattern transformations."""

    transforms: list[Transform]
    probability: float = 1.0
    custom_fn: Callable[[str], str] | None = None

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

    def __iter__(self) -> Iterator[str]:
        """Allow direct iteration: list(pattern) yields all generated strings.

        Uses default length constraints (no filtering beyond 0..99), matching
        generate() defaults for consistency.
        """
        return self.generate()

    def __or__(self, other: "BasePattern") -> "POr":
        """Syntactic sugar for POr(self, other)."""
        return POr(self, other)

    def __and__(self, other: "BasePattern") -> "PAnd":
        """Syntactic sugar for PAnd(self, other)."""
        return PAnd(self, other)


class P(BasePattern):
    """Basic pattern containing a list of strings with transformations."""

    _TRANSFORM_MAP = {
        Transform.LOWER: lambda t: t.lower(),
        Transform.UPPER: lambda t: t.upper(),
        Transform.CAPITALIZE: lambda t: t.capitalize(),
        Transform.TITLE: lambda t: t.title(),
        Transform.REVERSE: lambda t: t[::-1],
        Transform.LEET_BASIC: lambda t, self=None: self._leet_basic(t) if self else t,
        Transform.LEET_ADVANCED: (
            lambda t, self=None: self._leet_advanced(t) if self else t
        ),
        Transform.REPEAT: lambda t: "".join([char * 2 for char in t]),
        Transform.ZERO_PAD_2: lambda t: t.zfill(2) if t.isdigit() else t,
        Transform.ZERO_PAD_4: lambda t: t.zfill(4) if t.isdigit() else t,
    }

    def __init__(
        self,
        items: list[str],
        name: str = "",
        transforms: list[Transform] | None = None,
        custom_transforms: list[Callable[[str], str]] | None = None,
    ):
        super().__init__(name)
        self.items = items
        self.transforms = transforms or []  # Default to no transforms
        self.custom_transforms = custom_transforms or []

    @classmethod
    def from_file(
        cls,
        filepath: str | Path,
        *,
        strip: bool = True,
        skip_empty: bool = True,
        comment_prefixes: tuple[str, ...] = ("#", ";"),
        encoding: str = "utf-8",
    ) -> "P":
        """Create a pattern by loading items from a text file.

        Each non-empty line becomes one item. Lines starting with any of
        ``comment_prefixes`` after optional leading whitespace are ignored.

        Args:
            filepath: Path to the input text file.
            strip: Strip whitespace around each line.
            skip_empty: Skip empty lines after stripping.
            comment_prefixes: Line prefixes to treat as comments.
            encoding: File encoding to use when reading.

        Returns:
            A ``P`` instance whose items are the lines from the file.
        """
        path_obj = Path(filepath)
        items: list[str] = []
        with path_obj.open("r", encoding=encoding) as f:
            for raw_line in f:
                line = raw_line.rstrip("\n\r")
                if strip:
                    line = line.strip()
                if skip_empty and not line:
                    continue
                # Skip commented lines (after stripping leading whitespace)
                lstripped = line.lstrip()
                if any(lstripped.startswith(prefix) for prefix in comment_prefixes):
                    continue
                items.append(line)

        return cls(items, name=path_obj.name)

    def expand(self, *transforms: Transform | Callable[[str], str]) -> "P":
        """Add transformations, expanding the set of results (inclusive).

        This is an inclusive operation: it generates the original items plus
        all their transformed versions.
        """
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

    def alter(self, *transforms: Transform | Callable[[str], str]) -> "P":
        """Apply transformations, replacing the current items (exclusive).

        This is an exclusive operation: it only generates the transformed
        versions of the items, not the original ones.
        """
        if not transforms:
            return self

        current_outputs = list(self._generate())
        final_outputs = set()

        transform_fns = []
        for t in transforms:
            if isinstance(t, Transform):
                transform_fns.append(lambda text, t=t: self._apply_transform(text, t))
            elif callable(t):
                transform_fns.append(t)

        if not transform_fns:
            return P(current_outputs, self.name)

        for output in current_outputs:
            for fn in transform_fns:
                final_outputs.add(fn(output))

        return P(list(final_outputs), self.name)

    def lambda_expand(self, fn: Callable[[str], str]) -> "P":
        """Inclusive lambda transformation (adds new variations)."""
        return self.expand(fn)

    def lambda_transform(self, fn: Callable[[str], str]) -> "P":
        """Exclusive lambda transformation (replaces items)."""
        return self.alter(fn)

    def _generate(self) -> Iterator[str]:
        """Generate original items plus all transformed versions."""
        # Create a combined list of all transform functions
        all_transforms: list[Callable[[str], str]] = [
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
                yielded = {item}  # Include original to avoid re-yielding it
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
        transform_func = self._TRANSFORM_MAP.get(transform)
        if transform_func:
            # Pass self to the lambda if it's a leet transform
            if transform in (Transform.LEET_BASIC, Transform.LEET_ADVANCED):
                return transform_func(text, self=self)
            return transform_func(text)
        else:
            return text

    def _leet_basic(self, text: str) -> str:
        """Basic leet speak transformations."""
        replacements = {"a": "@", "e": "3", "i": "1", "o": "0", "s": "$", "l": "1"}
        result = text.lower()
        for char, replacement in replacements.items():
            result = result.replace(char, replacement)
        return result

    def _leet_advanced(self, text: str) -> str:
        """Advanced leet speak transformations."""
        replacements = {
            "a": "@",
            "e": "3",
            "i": "1",
            "o": "0",
            "s": "$",
            "l": "1",
            "t": "7",
            "b": "6",
            "g": "9",
            "z": "2",
            "h": "#",
        }
        result = text.lower()
        for char, replacement in replacements.items():
            result = result.replace(char, replacement)
        return result

    def _repeat_chars(self, text: str) -> str:
        """Helper method to repeat characters in a string."""
        return "".join([char * 2 for char in text])


# Common pattern constants
EMPTY = P([""])  # Empty pattern (ε) for optional components


class PAnd(BasePattern):
    """
    Concatenates patterns in sequential order (Cartesian Product).

    Creates all possible combinations by concatenating each item from
    the first pattern with each item from the second pattern.

    Example:
        P(["a", "b"]) & P(["1", "2"]) generates ["a1", "a2", "b1", "b2"]

    This is NOT string concatenation of items within a single pattern.
    To get "ab" from ["a", "b"], you need P(["ab"]) or P(["a"]) & P(["b"]).
    """

    def __init__(self, *patterns: BasePattern, name: str = "PAnd"):
        super().__init__(name)

        # Flatten nested PAnd patterns for efficiency
        new_patterns = []
        for p in patterns:
            if isinstance(p, PAnd):
                new_patterns.extend(p.patterns)
            else:
                new_patterns.append(p)
        self.patterns = tuple(new_patterns)

    def _generate(self) -> Iterator[str]:
        """Generate cartesian product of all sub-patterns lazily."""

        def _generate_recursive(patterns: tuple[BasePattern, ...]) -> Iterator[str]:
            if not patterns:
                yield ""
                return

            first_pattern = patterns[0]
            rest_patterns = patterns[1:]

            # A generator can only be consumed once. To use it in the inner loop
            # multiple times, we must cache its values in a list.
            for first_item in list(first_pattern._generate()):
                for rest_items in _generate_recursive(rest_patterns):
                    yield first_item + rest_items

        # The initial call still holds the lazy generation behavior for the outer loop
        yield from _generate_recursive(self.patterns)

    def estimate_count(self) -> int:
        count = 1
        for pattern in self.patterns:
            count *= pattern.estimate_count()
        return count


class POr(BasePattern):
    """
    Union of patterns - yields all items from all sub-patterns.

    Generates all values from each alternative pattern. This is a union
    operation, not a choice - it produces ALL alternatives.

    Example:
        P(["admin"]) | P(["user", "guest"]) generates ["admin", "user", "guest"]

    Note: This yields ALL items, not just one. The name "OR" refers to the
    fact that in the final password, you get items from this pattern OR that pattern.
    """

    def __init__(self, *patterns: BasePattern, name: str = "POr"):
        super().__init__(name)

        # Flatten nested POr patterns for efficiency
        new_patterns = []
        for p in patterns:
            if isinstance(p, POr):
                new_patterns.extend(p.patterns)
            else:
                new_patterns.append(p)
        self.patterns = tuple(new_patterns)

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
        # Note: list() is needed to "realize" the generator for product,
        # which can be memory-intensive for large base patterns.
        pattern_values = list(self.pattern._generate())
        for combo in itertools.product(pattern_values, repeat=self.count):
            yield "".join(combo)

    def estimate_count(self) -> int:
        return self.pattern.estimate_count() ** self.count


class InterleavePattern(BasePattern):
    """Insert separator between other patterns."""

    def __init__(
        self, separator: str, *patterns: BasePattern, name: str = "interleave"
    ):
        super().__init__(name)
        self.separator = separator
        self.patterns = patterns

    def _generate(self) -> Iterator[str]:
        """Generate patterns with separator between them."""
        # Note: list() is needed to "realize" the generators for product,
        # which can be memory-intensive for large base patterns.
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

    def __init__(
        self,
        years: list[int] | None = None,
        formats: list[str] | None = None,
        name: str = "birthday",
    ):
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
def save_to_file(
    pattern: BasePattern,
    filepath: Path,
    min_len: int,
    max_len: int,
    max_count: int | None = None,
) -> int:
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
    with open(filepath, "w") as f:
        for password in pattern.generate(min_len, max_len):
            f.write(password + "\n")
            count += 1
            if max_count and count >= max_count:
                break
    return count
