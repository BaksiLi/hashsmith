# Transforms

Transforms generate variations from base items. HashSmith offers two modes:

**Reference implementations**: See `tests/test_transform.py` for comprehensive transform examples.

## `.alter()` – Exclusive

- Replaces items with their transformed forms
- Prefer placing `.alter()` before `.expand()` when chaining, so you alter the base then add inclusive variants

```python
P(["hello"]).alter(Transform.UPPER)
# → ["HELLO"]
```

## `.expand()` – Inclusive

- Adds transformed items alongside originals
- Use for wordlist expansion (common case)

```python
P(["hello"]).expand(Transform.UPPER)
# → ["hello", "HELLO"]
```

## Chaining

- Methods operate on the full set from previous step

```python
P(["web"]).alter(Transform.UPPER).expand(Transform.REVERSE)
# → ["WEB", "BEW"]

P(["x"]).expand(lambda s: s + s).expand(Transform.UPPER)
# → ["x", "xx", "X", "XX"]
```

## Available Transforms

- `UPPER`, `LOWER`, `CAPITALIZE`, `TITLE`
- `REVERSE`, `REPEAT`
- `LEET_BASIC`, `LEET_ADVANCED`
- `ZERO_PAD_2`, `ZERO_PAD_4`

Notes:

- Numeric zero padding applies only to digit-only strings
- Duplicates are removed within a `P([...])` emission order

See also: [[Operational Semantics]](Operational-Semantics.md) for how transforms compose with `&` and `|`.
