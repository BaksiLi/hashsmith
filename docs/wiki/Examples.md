# Examples

This page shows practical examples of building password patterns with HashSmith.

**Additional examples**: See `tests/test_patterns.py` and `tests/test_transform.py` for comprehensive test cases demonstrating pattern operations and transforms.

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

### Importing Items From Files

```python
from hashsmith.patterns import P, Transform

# Describe the structure using independent sources (one item per line per file)
corporate_pattern = (
    (P.from_file("names.txt") | P.from_file("nicks.txt").alter(Transform.CAPITALIZE)) &
    P.from_file("projects.txt") &
    P.from_file("codes.txt")
)

# Iterate or save
for pwd in corporate_pattern.generate(min_len=1, max_len=32):
    print(pwd)
```

### Running Hashcat with Generated Wordlists

```python
from hashsmith.attacks import DictionaryAttack
from hashsmith.core import HashcatRunner

# Build your pattern and save to a wordlist
# save_to_file(pattern, "custom.txt", min_len=8, max_len=16)

attack = DictionaryAttack("/usr/bin/hashcat")
runner = HashcatRunner("/usr/bin/hashcat")

cmd = attack.generate_command(
    hash_file="hashes.txt",
    wordlist="custom.txt",
)

runner.run(cmd)
```

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
3. **Use `""` for optional parts** - `P(["", "!", "$"])` is simple and clear
4. **Chain transformations carefully** - `.alter()` followed by `.expand()` works well
5. **Use length constraints** - `pattern.generate(min_len=6, max_len=15)` to control output size

## Performance Considerations

- Large patterns can generate millions of combinations
- Use length constraints to limit output size
- Consider using `pattern.estimate_size()` before generation
- Transformations are applied lazily for memory efficiency
