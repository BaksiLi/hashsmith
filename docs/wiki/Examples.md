# Examples

This page shows practical examples of building password patterns with HashSmith.

## Basic Patterns

### Word + Number Combinations

```python
from hashsmith.patterns import P, Transform

# Simple word + number pattern
pattern = P(["admin", "user"]) & P(["123", "456"])
# Generates: ["admin123", "admin456", "user123", "user456"]
```

### With Capitalization

```python
# Add capitalized versions of words
pattern = P(["admin", "user"]).expand(Transform.CAPITALIZE) & P(["123"])
# Generates: ["admin123", "Admin123", "user123", "User123"]
```

### Optional Suffixes

```python
# Optional symbol suffix using empty string
pattern = P(["password"]) & P(["", "!", "$", "#"])
# Generates: ["password", "password!", "password$", "password#"]
```

## Advanced Patterns

### Birthday + Word Combinations

```python
from hashsmith.patterns import Birthday

# Combine words with birthday formats
pattern = (
    P(["john", "jane"]).expand(Transform.CAPITALIZE) &
    Birthday(years=[1990, 1995], formats=["MMDD", "MMDDYY"])
)
# Generates combinations like: "John0101", "John010190", "Jane1231", etc.
```

### Leet Speak Transformations

```python
# Apply leet speak to words
pattern = P(["password", "admin"]).expand(Transform.LEET_BASIC)
# Generates: ["password", "p@ssw0rd", "admin", "adm1n"]
```

### Chained Transformations

```python
# Multiple transformations in sequence
pattern = (
    P(["web"])
    .alter(Transform.UPPER)  # Replace with "WEB"
    .expand(Transform.REVERSE)  # Add "BEW"
)
# Generates: ["WEB", "BEW"]
```

## Real-World Scenarios

### Common Password Structure

```python
# Typical pattern: word + number + optional symbol
pattern = (
    P(["password", "admin", "user", "root"]).expand(Transform.CAPITALIZE) &
    P(["123", "456", "789", "2023", "2024"]) &
    P(["", "!", "$", "#", "@"])
)
```

### Company-Specific Patterns

```python
# Company name + year + common suffixes
pattern = (
    P(["acme", "tech", "corp"]).expand(Transform.CAPITALIZE) &
    P(["2023", "2024", "2025"]) &
    P(["", "!", "123", "admin"])
)
```

### Gaming Passwords

```python
# Gaming username patterns
pattern = (
    P(["player", "gamer", "pro"]).expand(Transform.LEET_BASIC) &
    P(["123", "456", "789", "2023"]) &
    P(["", "x", "xx", "xxx"])
)
```

## Tips and Best Practices

1. **Use `.expand()` for inclusive transformations** - keeps originals and adds variations
2. **Use `.alter()` for exclusive transformations** - replaces originals with new forms
3. **Empty strings `""` create optional parts** - useful for suffixes and separators
4. **Chain transformations carefully** - `.alter()` followed by `.expand()` works well
5. **Use length constraints** - `pattern.generate(min_len=6, max_len=15)` to control output size

## Performance Considerations

- Large patterns can generate millions of combinations
- Use length constraints to limit output size
- Consider using `pattern.estimate_size()` before generation
- Transformations are applied lazily for memory efficiency
