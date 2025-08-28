# HashSmith Wiki

A modern, compositional password pattern engine for building targeted, declarative wordlists.

## Quick Start

HashSmith lets you build password patterns using simple composition operators:

```python
from hashsmith.patterns import P, Transform

# Generate: word + number + optional symbol
pattern = (
    P(["admin", "user"]).expand(Transform.CAPITALIZE) &
    P(["123", "456"]) &
    P(["", "!", "$"])
)
```

## Documentation

- [[Design Rationale]](Design-Rationale.md) - Core concepts and mathematical model
- [[Transforms]](Transforms.md) - Available transformations and usage patterns
- [[Examples]](Examples.md) - Practical usage examples and patterns

## Repository Documentation

For API documentation, examples, and development guides, see the main repository's `/docs` directory.
