# HashSmith

> ⚠️ **Beta Software**: This project is under active development.

A modern, compositional password pattern engine and hashcat orchestrator for Python.

**Philosophy**: Declarative, composable, explicit patterns for targeted password generation.

## ✨ Why HashSmith?

- **🧱 Compositional**: Build complex patterns from simple, reusable pieces
- **📝 Declarative**: Describe *what* you want, not *how* to generate it  
- **📖 Readable**: Code structure documents the password pattern
- **🔧 Extensible**: Easy to add new pattern types and transforms
- **⚡ Efficient**: Optimized for large-scale password generation

## 🚀 Quick Start

```python
from hashsmith.patterns import P, Birthday, Transform

# Build a pattern: [word][numbers][suffix] using & and | operators
pattern = (
    P(["crypto", "bitcoin"]).alter(Transform.CAPITALIZE) &
    (
        P(["123", "456", "789"]) |
        Birthday(years=[1990, 1995], formats=["MMDD"])
    ) &
    P(["", "!", "$"])
)

# Generate passwords with length constraints
passwords = list(pattern.generate(min_len=6, max_len=15))
print(passwords[:5])  # Show first 5
# Output: ['crypto123', 'crypto123!', 'crypto123$', 'crypto456', 'crypto456!']
```

As syntactic sugar, `&` (and) / `|` (or) operators work for all patterns.

## 🧩 Core Components

| Component | Purpose | Example |
|-----------|---------|---------|
| **`P`** | Basic pattern with items | `P(["word1", "word2"])` |
| **`&` (`PAnd`)** | Sequential concatenation | `pattern1 & pattern2` |
| **`\|` (`POr`)** | Alternatives (choose one) | `pattern1 \| pattern2` |
| **`Transform`** | Text transformations | `.alter(Transform.CAPITALIZE)` |

### Additional Patterns

| Pattern | Purpose | Example |
|---------|---------|---------|
| **`Birthday`** | Date-based patterns (calendar-aware) | `Birthday(years=[1990], formats=["MMDD"])` |

**Coming Soon**: `Incremental`, `Charset` patterns

## ⚡ Transform System

```python
# Basic transform
P(["hello"]).alter(Transform.UPPER)
# → ["hello", "HELLO"]

# Chained transforms (like string methods)
P(["hello"]).alter(Transform.UPPER).alter(lambda x: x + "!")
# → ["hello", "HELLO", "hello!", "HELLO!"]

# Available transforms
Transform.UPPER, Transform.LOWER, Transform.CAPITALIZE
Transform.LEET_BASIC  # hello → h3ll0
Transform.REVERSE     # hello → olleh
Transform.ZERO_PAD_2  # 5 → 05
```

## 🔥 Attack on Hashes

HashSmith generates wordlists optimized for [Hashcat](https://hashcat.net/hashcat/) attacks:

```python
from hashsmith.attacks import DictionaryAttack
from hashsmith.core import HashcatRunner

# Generate targeted wordlist
pattern = create_your_pattern()
save_to_file(pattern, "custom.txt", min_len=8, max_len=16)

# Run hashcat attack
attack = DictionaryAttack("/usr/bin/hashcat")
runner = HashcatRunner("/usr/bin/hashcat")

command = attack.generate_command(
    hash_file="hashes.txt",
    wordlist="custom.txt",
    session_name="custom_attack"
)
runner.run(command)
```

COMING: Piping with Hashcat.

## 📦 Installation

```bash
# Clone repository
git clone https://github.com/yourusername/hashsmith.git
cd hashsmith

# Install with PDM
pdm install

# Or install dependencies manually
pip install -r requirements.txt
```

## 📖 Development

For development, testing, and contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).
