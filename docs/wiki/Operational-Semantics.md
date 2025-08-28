# Operational Semantics

This document defines the mathematical foundations and operational semantics of HashSmith's pattern engine for targeted wordlist generation.

## Core Operators

**Reference implementations**: See `tests/test_patterns.py` for comprehensive operator examples.

### `P(items)` – Pattern Constructor

- **Semantics**: Represents a finite set of candidate strings.
- **Example**: `P(["a", "b"])` generates `{"a", "b"}` (discrete alternatives, not concatenation).
- **Role**: Forms the atomic building block for all pattern operations.

### `PAnd` / `&` – Sequential Composition

- **Operation**: Cartesian product with string concatenation.
- **Semantics**: `A & B = {a + b | a ∈ A, b ∈ B}`
- **Example**: `P(["a", "b"]) & P(["1", "2"]) → {"a1", "a2", "b1", "b2"}`
- **Properties**: Associative, non-commutative
- **Complexity**: `|A & B| = |A| × |B|` (multiplicative growth)

### `POr` / `|` – Alternative Composition

- **Operation**: Set union of pattern outputs.
- **Semantics**: `A | B = A ∪ B`
- **Example**: `P(["admin"]) | P(["user"]) → {"admin", "user"}`
- **Properties**: Commutative, associative, idempotent
- **Complexity**: `|A | B| ≤ |A| + |B|` (additive growth, deduplication applied)

## Optional Pattern Semantics

**Reference implementations**: See `tests/test_patterns.py` for optional pattern test cases.

Optional components are modeled using union with the empty string (`EMPTY = P(["""])`):

### Basic Optional Suffix

```text
A & (B | EMPTY) ≡ A | (A & B)
```

**Interpretation**: Generate base pattern A, with optional suffix B.

### Optional Separator

```text
A & (sep | EMPTY) & B ≡ (A & sep & B) | (A & B)
```

**Application**: Word boundaries, delimiters in credential patterns.

### Compositional Optional Segments

```text
A & (B | EMPTY) & (C | EMPTY) ≡ A | (A & B) | (A & C) | (A & B & C)
```

**Security relevance**: Models common password construction patterns (base + year + symbol).

## Design Rationale

### Mathematical Soundness

- **Deterministic**: Same pattern specification always yields identical wordlists.
- **Compositional**: Complex patterns built from simple, well-defined operators.
- **Algebraic**: Supports formal reasoning about pattern equivalences and optimizations.

### Security Applications

- **Mirrors attack patterns**: Reflects empirical password construction behaviors.
- **Scalable enumeration**: Efficient generation for large keyspaces without memory explosion.
- **Targeted wordlists**: Precise control over output characteristics for specific attack scenarios.

### Implementation Benefits

- **Transform compatibility**: Operators compose cleanly with string transformations.
- **Estimation**: Closed-form size calculations enable pre-attack planning.
- **Lazy evaluation**: Memory-efficient generation for massive pattern combinations.

**See also**: [[Transforms]](Transforms.md) for transform semantics and `tests/test_transform.py` for transform examples.
