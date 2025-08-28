# HashSmith Wiki

A modern, compositional password pattern engine for building targeted, declarative wordlists.

## Quick Start

HashSmith lets you build password patterns using simple composition operators:

```python
from hashsmith.patterns import P, Transform, EMPTY

# Generate: word + number + optional symbol
pattern = (
    P(["admin", "user"]).expand(Transform.CAPITALIZE) &
    P(["123", "456"]) &
    (P(["!", "$"]) | EMPTY)
)
```

## Repository Documentation

For API documentation, examples, and development guides, see the main repository's `/docs` directory.

This wiki is automatically synced by .github/workflows/sync-wiki.yml
