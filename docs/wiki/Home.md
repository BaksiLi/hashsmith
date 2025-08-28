# HashSmith Wiki

A modern, declarative and compositional password pattern engine for building targeted wordlists.

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

## Repository Documentation

For API documentation, examples, and development guides, see the main repository's `/docs` directory.

This wiki is automatically synced by .github/workflows/sync-wiki.yml

## Installation

Install from PyPI:

```bash
pip install hashsmith
```

PyPI page: [`pypi.org/project/hashsmith`](https://pypi.org/project/hashsmith/)

## Hashcat Orchestrator

HashSmith ships with a lightweight Hashcat orchestrator to help you run attacks using the wordlists you generate.

```python
from hashsmith.core import HashcatRunner

# Point to your hashcat binary
runner = HashcatRunner("/usr/bin/hashcat")

# Example: show cracked passwords for a previous run
runner.run([
    "/usr/bin/hashcat",
    "--session", "my_session",
    "-m", "0",              # MD5
    "-a", "0",              # straight/dictionary
    "hashes.txt",
    "custom_wordlist.txt",
])
```

See `README.md` for a full example integrating `DictionaryAttack` and `HashcatRunner`.
