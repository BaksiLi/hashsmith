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
