# Design Rationale

This page explains the core model and why HashSmith uses set-theoretic composition for building wordlists.

## Core Primitives

### `P(items)` – Alternatives
- Represents a set of complete alternatives.
- `P(["a", "b"])` means "generate `a` or `b`" (not `"ab"`).

### `PAnd` / `&` – Cartesian Product (Sequential Concatenation)
- Concatenates each item from the left with each item from the right.
- Example: `P(["a", "b"]) & P(["1", "2"]) → ["a1", "a2", "b1", "b2"]`.
- Associative: `(A & B) & C = A & (B & C)`.
- Count multiplies: `|A & B| = |A| × |B|`.

### `POr` / `|` – Union (Alternatives)
- Yields all items from both patterns.
- Example: `P(["admin"]) | P(["user"]) → ["admin", "user"]`.
- Commutative and associative.
- Count adds: `|A | B| = |A| + |B|` (minus duplicates if present).

## Inclusive AND: Logical Equivalences

Sometimes you want an optional part, e.g., a suffix that may or may not appear.

- Optional right pattern using union with empty string:
  - `A & (B | P([""]))  ≡  A | (A & B)`
  - Reads as: generate A alone or A concatenated with B.

- Optional middle separator:
  - `A & (P([sep]) | P([""])) & B  ≡  (A & sep & B) | (A & B)`

- Multiple optional segments compose naturally:
  - `A & (B | ε) & (C | ε)  ≡  A | (A & B) | (A & C) | (A & B & C)`

These equivalences explain the "inclusive AND" patterns common in real-world passwords (base word, optional number, optional symbol).

## Why This Model?
- Predictable, composable, and mathematically sound
- Mirrors how users structure passwords (slots): base + modifier + suffix
- Enables fast estimation and pruning
- Plays well with transforms (see [[Transforms]](Transforms.md))
