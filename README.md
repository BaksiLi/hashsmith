# HashSmith

> ⚠️ **Beta Software**: This project is under active development.

A modern, compositional password pattern engine and hashcat orchestrator for Python.

**Philosophy**: Declarative, composable, explicit patterns for targeted password generation.

**For detailed documentation, see the wiki:** [`github.com/BaksiLi/hashsmith/wiki`](https://github.com/BaksiLi/hashsmith/wiki)

- **Operational Semantics**: Mathematical foundations and pattern engine semantics.
- **Transforms**: How to use `.alter()` and `.expand()` effectively.
- **Examples**: Practical patterns and scenarios.

## ✨ Core Features

- **🧱 Compositional**: Build complex patterns from simple, reusable pieces.
- **📝 Declarative**: Describe *what* you want, not *how* to generate it.
- **📖 Readable**: Code structure documents the password pattern.
- **🔧 Extensible**: Easy to add new pattern types and transforms.
- **🧠 Memory Efficient**: Lazy generation for combining patterns to handle massive keyspaces.

## 🚀 Quick Start

```python
from hashsmith.patterns import P, Birthday, Transform

# Build a [word][numbers][suffix] pattern
pattern = (
    P(["crypto", "bitcoin"]).expand(Transform.CAPITALIZE) &
    (
        P(["123", "456", "789"]) |
        Birthday(years=[1990, 1995], formats=["MMDD"])
    ) &
    P(["", "!", "$"])
)

# Generate and print the first 10 passwords
passwords = list(pattern.generate(min_len=6, max_len=15))
for p in passwords[:10]:
    print(p)

# → crypto123, crypto123!, crypto123$, crypto456, ...
```

## 🧩 Core Components

| Component | Purpose | Example |
|-----------|---------|---------|
| **`P`** | Basic pattern with items | `P(["word1", "word2"])` |
| **`&` (`PAnd`)** | Sequential concatenation | `pattern1 & pattern2` |
| **`\|` (`POr`)** | Alternatives (choose one) | `pattern1 \| pattern2` |
| **Transforms** | Inclusive `.expand()` or exclusive `.alter()` | `P(["a"]).expand(Transform.UPPER)` |

### Additional Patterns

| Pattern | Purpose | Example |
|---------|---------|---------|
| **`Birthday`** | Date-based patterns (calendar-aware) | `Birthday(years=[1990], formats=["MMDD"])` |

**Coming Soon**: `Incremental`, `Charset`, `Keyboard` patterns

## ⚡ Transform System

HashSmith supports two transformation modes:

```python
# Inclusive expansion (adds to the set)
P(["hello"]).expand(Transform.UPPER)
# → ["hello", "HELLO"]

# Exclusive alteration (replaces the set)
P(["hello"]).alter(Transform.UPPER)
# → ["HELLO"]

# Mix alter (exclusive) and expand (inclusive)
# Prefer `.alter()` before `.expand()` when chaining
P(["web"]).alter(Transform.UPPER).expand(Transform.REVERSE)
# → ["WEB", "BEW"]

# Chained expansions accumulate results
P(["hello"]).expand(Transform.UPPER).expand(lambda x: x + "!")
# → ["hello", "HELLO", "hello!", "HELLO!"]

# Available transforms
Transform.UPPER, Transform.LOWER, Transform.CAPITALIZE
Transform.LEET_BASIC  # hello → h3ll0
Transform.REVERSE     # hello → olleh
Transform.ZERO_PAD_2  # 5 → 05
Transform.REPEAT
```

## 🔥 Attack on Hashes

HashSmith generates wordlists optimized for [Hashcat](https://hashcat.net/hashcat/) attacks:

```python
from hashsmith.attacks import DictionaryAttack
from hashsmith.core import HashcatRunner

# Generate targeted wordlist
pattern = pattern  # build your pattern
# save_to_file(pattern, "custom.txt", min_len=8, max_len=16)

# Run hashcat attack
attack = DictionaryAttack("/usr/bin/hashcat")
runner = HashcatRunner("/usr/bin/hashcat")

command = attack.generate_command(
    hash_file="hashes.txt",
    wordlist="custom.txt",
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

